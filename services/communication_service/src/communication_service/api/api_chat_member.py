from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_chat_member_role import (
    ChatMemberRole
)
from common.security.dependencies import get_current_principal
from common.security.principal import CurrentPrincipal
from communication_service.api.dependencies import require_chat_member
from communication_service.db.db_session import (
    get_session
)
from communication_service.schemas.schemas_chat_member import (
    ChatLeaveRequest,
    ChatMemberActionRequest,
    ChatMemberCreate,
    ChatMemberListResponse,
    ChatMemberResponse,
    ChatMemberRoleUpdate
)
from communication_service.services.service_chat_member import (
    ChatMemberService
)


router = APIRouter(
    prefix="/chat-members",
    tags=["Chat members"]
)


# =====================================================
# Добавить участника
# =====================================================

@router.post(
    "",
    response_model=ChatMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить участника в чат"
)
async def create_chat_member_endpoint(
    member_data: ChatMemberCreate,
    session: AsyncSession = Depends(get_session)
):
    service = ChatMemberService(
        session=session
    )

    try:
        return await service.create(
            member_data=member_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Список участников чата
# =====================================================

@router.get(
    "/chat/{chat_id}",
    response_model=ChatMemberListResponse,
    summary="Получить участников чата"
)
async def get_chat_members_endpoint(
    chat_id: int,
    _member: CurrentPrincipal = Depends(require_chat_member),
    is_active: bool | None = Query(
        default=None
    ),
    member_role: ChatMemberRole | None = Query(
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
    session: AsyncSession = Depends(get_session)
):
    service = ChatMemberService(
        session=session
    )

    try:
        members, total = await service.get_list(
            chat_id=chat_id,
            is_active=is_active,
            member_role=member_role,
            skip=skip,
            limit=limit
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error

    return ChatMemberListResponse(
        total=total,
        items=members
    )


# =====================================================
# Получить участника по ID
# =====================================================

@router.get(
    "/{member_id}",
    response_model=ChatMemberResponse,
    summary="Получить участника чата по ID"
)
async def get_chat_member_endpoint(
    member_id: int,
    principal: CurrentPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session)
):
    service = ChatMemberService(
        session=session
    )

    member = await service.get_by_id(
        member_id=member_id
    )

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Участник чата не найден"
        )
    if not await require_chat_member(
        Request({"type": "http", "method": "GET", "path": "/", "path_params": {"chat_id": member.chat_id}, "query_string": b"", "headers": [], "state": {}}),
        principal,
        session,
    ):
        raise HTTPException(status_code=403, detail="Chat membership required")

    return member


# =====================================================
# Изменить роль
# =====================================================

@router.patch(
    "/{member_id}/role",
    response_model=ChatMemberResponse,
    summary="Изменить роль участника чата"
)
async def update_chat_member_role_endpoint(
    member_id: int,
    role_data: ChatMemberRoleUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = ChatMemberService(
        session=session
    )

    member = await service.get_by_id(
        member_id=member_id
    )

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Участник чата не найден"
        )

    try:
        return await service.update_role(
            member=member,
            role_data=role_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Деактивировать участника
# =====================================================

@router.post(
    "/{member_id}/deactivate",
    response_model=ChatMemberResponse,
    summary="Удалить участника из чата"
)
async def deactivate_chat_member_endpoint(
    member_id: int,
    action_data: ChatMemberActionRequest,
    principal: CurrentPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session)
):
    service = ChatMemberService(
        session=session
    )

    member = await service.get_by_id(
        member_id=member_id
    )

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Участник чата не найден"
        )

    try:
        return await service.deactivate(
            member=member,
            requested_by=principal.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Активировать участника
# =====================================================

@router.post(
    "/{member_id}/activate",
    response_model=ChatMemberResponse,
    summary="Вернуть участника в чат"
)
async def activate_chat_member_endpoint(
    member_id: int,
    action_data: ChatMemberActionRequest,
    principal: CurrentPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session)
):
    service = ChatMemberService(
        session=session
    )

    member = await service.get_by_id(
        member_id=member_id
    )

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Участник чата не найден"
        )

    try:
        return await service.activate(
            member=member,
            requested_by=principal.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Покинуть чат
# =====================================================

@router.post(
    "/chat/{chat_id}/leave",
    response_model=ChatMemberResponse,
    summary="Покинуть чат"
)
async def leave_chat_endpoint(
    chat_id: int,
    leave_data: ChatLeaveRequest,
    principal: CurrentPrincipal = Depends(require_chat_member),
    session: AsyncSession = Depends(get_session)
):
    service = ChatMemberService(
        session=session
    )

    try:
        return await service.leave(
            chat_id=chat_id,
            user_id=principal.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error
