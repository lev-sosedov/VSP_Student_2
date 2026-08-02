from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_chat_type import ChatType
from common.security.dependencies import get_current_principal
from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType
from communication_service.api.dependencies import require_chat_member
from communication_service.db.db_session import (
    get_session
)
from communication_service.schemas.schemas_chat import (
    ChatActionRequest,
    ChatCreate,
    ChatDetailResponse,
    EnsureStudentAdminChatRequest,
    ChatListItemResponse,
    ChatListResponse,
    ChatResponse,
    ChatUpdate
)
from communication_service.core.core_config import settings
from communication_service.services.service_chat import (
    ChatService
)
from communication_service.services.service_message_read import (
    MessageReadService
)
from communication_service.messaging.messaging_rpc_client import communication_rpc_client


router = APIRouter(
    prefix="/chats",
    tags=["Chats"]
)


# =====================================================
# Создать чат
# =====================================================

@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать чат"
)
async def create_chat_endpoint(
    chat_data: ChatCreate,
    principal: CurrentPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session)
):
    if chat_data.created_by != principal.user_id:
        raise HTTPException(status_code=403, detail="created_by must match authenticated user")
    if chat_data.chat_type == ChatType.GROUP:
        if principal.role not in {RoleType.TEACHER, RoleType.ADMIN}:
            raise HTTPException(status_code=403, detail="Only teachers or administrators may create group chats")
        if principal.role is not RoleType.ADMIN:
            try:
                membership = await communication_rpc_client.call_academic(
                    method="academic.authorization.membership",
                    payload={"user_id": principal.user_id, "group_id": chat_data.group_id, "role": "teacher"},
                    timeout=2.0,
                )
                if not isinstance(membership, dict) or membership.get("success") is not True or membership.get("exists") is not True or membership.get("is_active") is not True:
                    raise ValueError("not an active group teacher")
            except Exception as exc:
                raise HTTPException(status_code=403, detail="Group authorization unavailable") from exc
    service = ChatService(
        session=session
    )

    try:
        return await service.create(
            chat_data=chat_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Получить список чатов
# =====================================================

@router.get(
    "",
    response_model=ChatListResponse,
    summary="Получить список чатов"
)
async def get_chats_endpoint(
    user_id: int | None = Query(
        default=None,
        gt=0,
        description=(
            "ID пользователя. Если передан, ответ содержит "
            "unread_count и last_message, а также только чаты, "
            "в которых пользователь является активным участником."
        )
    ),
    chat_type: ChatType | None = Query(
        default=None
    ),
    group_id: int | None = Query(
        default=None,
        gt=0
    ),
    lesson_id: int | None = Query(
        default=None,
        gt=0
    ),
    created_by: int | None = Query(
        default=None,
        gt=0
    ),
    is_active: bool | None = Query(
        default=None
    ),
    is_archived: bool | None = Query(
        default=None
    ),
    skip: int = Query(
        default=0,
        ge=0
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500
    ),
    principal: CurrentPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session)
):
    if user_id is not None and user_id != principal.user_id and principal.role is not RoleType.ADMIN:
        raise HTTPException(status_code=403, detail="Cannot query another user's chats")
    effective_user_id = user_id if principal.role is RoleType.ADMIN and user_id is not None else principal.user_id
    chat_service = ChatService(
        session=session
    )

    chats, total = await chat_service.get_list(
        chat_type=chat_type,
        group_id=group_id,
        lesson_id=lesson_id,
        created_by=created_by,
        is_active=is_active,
        is_archived=is_archived,
        skip=skip,
        limit=limit
    )

    # Старое поведение сохраняется для внутренних запросов,
    # которые пока не передают user_id.
    if effective_user_id is None:
        return ChatListResponse(
            total=total,
            items=[
                ChatListItemResponse.model_validate(
                    chat
                )
                for chat in chats
            ]
        )

    read_service = MessageReadService(
        session=session
    )

    result_items: list[ChatListItemResponse] = []

    for chat in chats:
        try:
            unread_count = (
                await read_service.get_chat_unread_count(
                    chat_id=chat.id,
                    user_id=effective_user_id
                )
            )
        except ValueError:
            # Пользователь не является активным участником.
            # Такой чат не должен попадать в его список.
            continue

        last_message = (
            await read_service.get_last_message(
                chat_id=chat.id
            )
        )

        result_items.append(
            ChatListItemResponse(
                **ChatResponse.model_validate(
                    chat
                ).model_dump(),
                unread_count=unread_count,
                last_message=last_message
            )
        )

    return ChatListResponse(
        total=len(result_items),
        items=result_items
    )


# =====================================================
# Гарантировать чат студента с администрацией
# =====================================================

@router.post(
    "/student-admin/ensure",
    response_model=ChatResponse,
    summary="Создать или получить чат студента с администрацией"
)
async def ensure_student_admin_chat_endpoint(
    request: EnsureStudentAdminChatRequest,
    principal: CurrentPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session)
):
    if principal.role is not RoleType.ADMIN and request.student_id != principal.user_id:
        raise HTTPException(status_code=403, detail="student_id must match authenticated user")
    service = ChatService(
        session=session
    )

    try:
        return await service.ensure_admin_chat(
            student_id=request.student_id,
            admin_id=settings.ADMIN_USER_ID
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Получить чат по ID
# =====================================================

@router.get(
    "/{chat_id}",
    response_model=ChatDetailResponse,
    summary="Получить чат по ID"
)
async def get_chat_endpoint(
    chat_id: int,
    _member: CurrentPrincipal = Depends(require_chat_member),
    session: AsyncSession = Depends(get_session)
):
    service = ChatService(
        session=session
    )

    chat = await service.get_by_id(
        chat_id=chat_id,
        with_members=True
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )

    return chat


# =====================================================
# Изменить чат
# =====================================================

@router.patch(
    "/{chat_id}",
    response_model=ChatResponse,
    summary="Изменить чат"
)
async def update_chat_endpoint(
    chat_id: int,
    chat_data: ChatUpdate,
    _member: CurrentPrincipal = Depends(require_chat_member),
    session: AsyncSession = Depends(get_session)
):
    service = ChatService(
        session=session
    )

    chat = await service.get_by_id(
        chat_id=chat_id
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )

    try:
        return await service.update(
            chat=chat,
            chat_data=chat_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Архивировать чат
# =====================================================

@router.post(
    "/{chat_id}/archive",
    response_model=ChatResponse,
    summary="Архивировать чат"
)
async def archive_chat_endpoint(
    chat_id: int,
    action_data: ChatActionRequest,
    principal: CurrentPrincipal = Depends(require_chat_member),
    session: AsyncSession = Depends(get_session)
):
    service = ChatService(
        session=session
    )

    chat = await service.get_by_id(
        chat_id=chat_id
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )

    try:
        return await service.archive(
            chat=chat,
            user_id=principal.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Восстановить чат
# =====================================================

@router.post(
    "/{chat_id}/restore",
    response_model=ChatResponse,
    summary="Восстановить чат из архива"
)
async def restore_chat_endpoint(
    chat_id: int,
    action_data: ChatActionRequest,
    principal: CurrentPrincipal = Depends(require_chat_member),
    session: AsyncSession = Depends(get_session)
):
    service = ChatService(
        session=session
    )

    chat = await service.get_by_id(
        chat_id=chat_id
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )

    try:
        return await service.restore(
            chat=chat,
            user_id=principal.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Деактивировать чат
# =====================================================

@router.post(
    "/{chat_id}/deactivate",
    response_model=ChatResponse,
    summary="Деактивировать чат"
)
async def deactivate_chat_endpoint(
    chat_id: int,
    action_data: ChatActionRequest,
    principal: CurrentPrincipal = Depends(require_chat_member),
    session: AsyncSession = Depends(get_session)
):
    service = ChatService(
        session=session
    )

    chat = await service.get_by_id(
        chat_id=chat_id
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )

    try:
        return await service.deactivate(
            chat=chat,
            user_id=principal.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Активировать чат
# =====================================================

@router.post(
    "/{chat_id}/activate",
    response_model=ChatResponse,
    summary="Активировать чат"
)
async def activate_chat_endpoint(
    chat_id: int,
    action_data: ChatActionRequest,
    principal: CurrentPrincipal = Depends(require_chat_member),
    session: AsyncSession = Depends(get_session)
):
    service = ChatService(
        session=session
    )

    chat = await service.get_by_id(
        chat_id=chat_id
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )

    try:
        return await service.activate(
            chat=chat,
            user_id=principal.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error
