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
from communication_service.schemas.schemas_message_attachment import (
    MessageAttachmentCreate,
    MessageAttachmentDeleteRequest,
    MessageAttachmentDeleteResponse,
    MessageAttachmentListResponse,
    MessageAttachmentResponse
)
from communication_service.services.service_message_attachment import (
    MessageAttachmentService
)


router = APIRouter(
    prefix="/message-attachments",
    tags=["Message attachments"]
)


# =====================================================
# Создать вложение
# =====================================================

@router.post(
    "",
    response_model=MessageAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить вложение к сообщению"
)
async def create_message_attachment_endpoint(
    attachment_data: MessageAttachmentCreate,
    session: AsyncSession = Depends(get_session)
):
    service = MessageAttachmentService(
        session=session
    )

    try:
        return await service.create(
            attachment_data=attachment_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Получить вложения сообщения
# =====================================================

@router.get(
    "/message/{message_id}",
    response_model=MessageAttachmentListResponse,
    summary="Получить вложения сообщения"
)
async def get_message_attachments_endpoint(
    message_id: int,
    requested_by: int = Query(
        ...,
        gt=0
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
    service = MessageAttachmentService(
        session=session
    )

    try:
        attachments, total = (
            await service.get_by_message(
                message_id=message_id,
                requested_by=requested_by,
                skip=skip,
                limit=limit
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error

    return MessageAttachmentListResponse(
        total=total,
        items=attachments
    )


# =====================================================
# Получить вложение по ID
# =====================================================

@router.get(
    "/{attachment_id}",
    response_model=MessageAttachmentResponse,
    summary="Получить вложение по ID"
)
async def get_message_attachment_endpoint(
    attachment_id: int,
    requested_by: int = Query(
        ...,
        gt=0
    ),
    session: AsyncSession = Depends(get_session)
):
    service = MessageAttachmentService(
        session=session
    )

    try:
        attachment = await service.get_by_id(
            attachment_id=attachment_id,
            requested_by=requested_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вложение не найдено"
        )

    return attachment


# =====================================================
# Удалить вложение
# =====================================================

@router.delete(
    "/{attachment_id}",
    response_model=MessageAttachmentDeleteResponse,
    summary="Удалить вложение"
)
async def delete_message_attachment_endpoint(
    attachment_id: int,
    delete_data: MessageAttachmentDeleteRequest,
    session: AsyncSession = Depends(get_session)
):
    service = MessageAttachmentService(
        session=session
    )

    attachment = await service.get_raw_by_id(
        attachment_id=attachment_id
    )

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вложение не найдено"
        )

    try:
        return await service.delete(
            attachment=attachment,
            requested_by=delete_data.requested_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


