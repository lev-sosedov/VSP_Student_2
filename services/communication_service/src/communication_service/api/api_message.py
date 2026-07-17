from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from communication_service.db.db_session import (
    get_session
)
from communication_service.schemas.schemas_message import (
    MessageActionRequest,
    MessageCreate,
    MessageDetailResponse,
    MessageListResponse,
    MessageResponse,
    MessageUpdate
)
from communication_service.services.service_message import (
    MessageService
)


router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)


# =====================================================
# Создать сообщение
# =====================================================

@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Отправить сообщение"
)
async def create_message_endpoint(
    message_data: MessageCreate,
    session: AsyncSession = Depends(get_session)
):
    service = MessageService(
        session=session
    )

    try:
        return await service.create(
            message_data=message_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Получить сообщения чата
# =====================================================

@router.get(
    "/chat/{chat_id}",
    response_model=MessageListResponse,
    summary="Получить сообщения чата"
)
async def get_chat_messages_endpoint(
    chat_id: int,
    requested_by: int = Query(
        ...,
        gt=0
    ),
    include_deleted: bool = Query(
        default=False
    ),
    sender_id: int | None = Query(
        default=None,
        gt=0
    ),
    is_pinned: bool | None = Query(
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
    service = MessageService(
        session=session
    )

    try:
        messages, total = (
            await service.get_chat_messages(
                chat_id=chat_id,
                requested_by=requested_by,
                include_deleted=include_deleted,
                sender_id=sender_id,
                is_pinned=is_pinned,
                skip=skip,
                limit=limit
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error

    return MessageListResponse(
        total=total,
        items=messages
    )


# =====================================================
# Получить сообщение по ID
# =====================================================

@router.get(
    "/{message_id}",
    response_model=MessageDetailResponse,
    summary="Получить сообщение по ID"
)
async def get_message_endpoint(
    message_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = MessageService(
        session=session
    )

    message = await service.get_by_id(
        message_id=message_id,
        with_reply=True
    )

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщение не найдено"
        )

    return message


# =====================================================
# Изменить сообщение
# =====================================================

@router.patch(
    "/{message_id}",
    response_model=MessageResponse,
    summary="Изменить сообщение"
)
async def update_message_endpoint(
    message_id: int,
    message_data: MessageUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = MessageService(
        session=session
    )

    message = await service.get_by_id(
        message_id=message_id
    )

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщение не найдено"
        )

    try:
        return await service.update(
            message=message,
            message_data=message_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Удалить сообщение
# =====================================================

@router.post(
    "/{message_id}/delete",
    response_model=MessageResponse,
    summary="Удалить сообщение"
)
async def delete_message_endpoint(
    message_id: int,
    action_data: MessageActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = MessageService(
        session=session
    )

    message = await service.get_by_id(
        message_id=message_id
    )

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщение не найдено"
        )

    try:
        return await service.delete(
            message=message,
            requested_by=action_data.requested_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Закрепить сообщение
# =====================================================

@router.post(
    "/{message_id}/pin",
    response_model=MessageResponse,
    summary="Закрепить сообщение"
)
async def pin_message_endpoint(
    message_id: int,
    action_data: MessageActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = MessageService(
        session=session
    )

    message = await service.get_by_id(
        message_id=message_id
    )

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщение не найдено"
        )

    try:
        return await service.pin(
            message=message,
            requested_by=action_data.requested_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Открепить сообщение
# =====================================================

@router.post(
    "/{message_id}/unpin",
    response_model=MessageResponse,
    summary="Открепить сообщение"
)
async def unpin_message_endpoint(
    message_id: int,
    action_data: MessageActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = MessageService(
        session=session
    )

    message = await service.get_by_id(
        message_id=message_id
    )

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщение не найдено"
        )

    try:
        return await service.unpin(
            message=message,
            requested_by=action_data.requested_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error