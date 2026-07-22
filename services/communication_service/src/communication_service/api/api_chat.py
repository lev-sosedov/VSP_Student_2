from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_chat_type import ChatType
from communication_service.db.db_session import (
    get_session
)
from communication_service.schemas.schemas_chat import (
    ChatActionRequest,
    ChatCreate,
    ChatDetailResponse,
    ChatListItemResponse,
    ChatListResponse,
    ChatResponse,
    ChatUpdate
)
from communication_service.services.service_chat import (
    ChatService
)
from communication_service.services.service_message_read import (
    MessageReadService
)


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
    session: AsyncSession = Depends(get_session)
):
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
    session: AsyncSession = Depends(get_session)
):
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
    if user_id is None:
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
                    user_id=user_id
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
# Получить чат по ID
# =====================================================

@router.get(
    "/{chat_id}",
    response_model=ChatDetailResponse,
    summary="Получить чат по ID"
)
async def get_chat_endpoint(
    chat_id: int,
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
            user_id=action_data.user_id
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
            user_id=action_data.user_id
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
            user_id=action_data.user_id
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
            user_id=action_data.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error