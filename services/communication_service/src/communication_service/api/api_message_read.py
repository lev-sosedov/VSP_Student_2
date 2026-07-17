from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from communication_service.db.db_session import (
    get_session
)
from communication_service.schemas.schemas_message_read import (
    ChatReadAllRequest,
    ChatReadAllResponse,
    ChatUnreadCountResponse,
    MessageReadCreate,
    MessageReadResponse,
    UserUnreadCountResponse
)
from communication_service.services.service_message_read import (
    MessageReadService
)


router = APIRouter(
    prefix="/message-reads",
    tags=["Message reads"]
)


# =====================================================
# Отметить сообщение прочитанным
# =====================================================

@router.post(
    "/{message_id}",
    response_model=MessageReadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Отметить сообщение прочитанным"
)
async def mark_message_as_read_endpoint(
    message_id: int,
    read_data: MessageReadCreate,
    session: AsyncSession = Depends(get_session)
):
    service = MessageReadService(
        session=session
    )

    try:
        return await service.mark_as_read(
            message_id=message_id,
            user_id=read_data.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Отметить весь чат прочитанным
# =====================================================

@router.post(
    "/chat/{chat_id}/read-all",
    response_model=ChatReadAllResponse,
    summary="Отметить все сообщения чата прочитанными"
)
async def mark_chat_as_read_endpoint(
    chat_id: int,
    read_data: ChatReadAllRequest,
    session: AsyncSession = Depends(get_session)
):
    service = MessageReadService(
        session=session
    )

    try:
        created_count, last_message_id = (
            await service.mark_chat_as_read(
                chat_id=chat_id,
                user_id=read_data.user_id
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error

    return ChatReadAllResponse(
        chat_id=chat_id,
        user_id=read_data.user_id,
        last_read_message_id=last_message_id,
        created_read_count=created_count
    )


# =====================================================
# Счётчик непрочитанных чата
# =====================================================

@router.get(
    "/chat/{chat_id}/unread-count",
    response_model=ChatUnreadCountResponse,
    summary="Получить непрочитанные сообщения чата"
)
async def get_chat_unread_count_endpoint(
    chat_id: int,
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = MessageReadService(
        session=session
    )

    try:
        unread_count = (
            await service.get_chat_unread_count(
                chat_id=chat_id,
                user_id=user_id
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error

    return ChatUnreadCountResponse(
        chat_id=chat_id,
        user_id=user_id,
        unread_count=unread_count
    )


# =====================================================
# Общий счётчик пользователя
# =====================================================

@router.get(
    "/user/{user_id}/unread-count",
    response_model=UserUnreadCountResponse,
    summary="Получить все непрочитанные сообщения пользователя"
)
async def get_user_unread_count_endpoint(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = MessageReadService(
        session=session
    )

    unread_count = (
        await service.get_user_unread_count(
            user_id=user_id
        )
    )

    return UserUnreadCountResponse(
        user_id=user_id,
        unread_count=unread_count
    )