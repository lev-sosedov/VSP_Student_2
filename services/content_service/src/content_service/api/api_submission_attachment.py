from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.db.db_session import get_session
from content_service.schemas.schemas_submission_attachment import (
    SubmissionAttachmentCreate,
    SubmissionAttachmentDeleteResponse,
    SubmissionAttachmentListResponse,
    SubmissionAttachmentResponse,
    SubmissionAttachmentUpdate
)
from content_service.services.service_submission_attachment import (
    SubmissionAttachmentService
)


router = APIRouter(
    prefix="/submission-attachments",
    tags=["Submission attachments"]
)


# =====================================================
# Создать файл студенческой работы
# =====================================================

@router.post(
    "",
    response_model=SubmissionAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить файл к домашней работе"
)
async def create_submission_attachment_endpoint(
    attachment_data: SubmissionAttachmentCreate,
    session: AsyncSession = Depends(get_session)
):
    service = SubmissionAttachmentService(
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
# Получить список файлов
# =====================================================

@router.get(
    "",
    response_model=SubmissionAttachmentListResponse,
    summary="Получить файлы домашних работ"
)
async def get_submission_attachments_endpoint(
    submission_id: int | None = Query(
        default=None,
        gt=0
    ),
    uploaded_by: int | None = Query(
        default=None,
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
    service = SubmissionAttachmentService(
        session=session
    )

    attachments, total = await service.get_list(
        submission_id=submission_id,
        uploaded_by=uploaded_by,
        skip=skip,
        limit=limit
    )

    return SubmissionAttachmentListResponse(
        total=total,
        items=attachments
    )


# =====================================================
# Получить файлы конкретной работы
# До маршрута /{attachment_id}
# =====================================================

@router.get(
    "/submission/{submission_id}",
    response_model=SubmissionAttachmentListResponse,
    summary="Получить файлы конкретной домашней работы"
)
async def get_attachments_by_submission_endpoint(
    submission_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = SubmissionAttachmentService(
        session=session
    )

    attachments, total = await service.get_list(
        submission_id=submission_id,
        skip=0,
        limit=500
    )

    return SubmissionAttachmentListResponse(
        total=total,
        items=attachments
    )


# =====================================================
# Получить файл по ID
# =====================================================

@router.get(
    "/{attachment_id}",
    response_model=SubmissionAttachmentResponse,
    summary="Получить файл домашней работы по ID"
)
async def get_submission_attachment_endpoint(
    attachment_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = SubmissionAttachmentService(
        session=session
    )

    attachment = await service.get_by_id(
        attachment_id=attachment_id
    )

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл домашней работы не найден"
        )

    return attachment


# =====================================================
# Изменить файл
# =====================================================

@router.patch(
    "/{attachment_id}",
    response_model=SubmissionAttachmentResponse,
    summary="Изменить файл домашней работы"
)
async def update_submission_attachment_endpoint(
    attachment_id: int,
    attachment_data: SubmissionAttachmentUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = SubmissionAttachmentService(
        session=session
    )

    attachment = await service.get_by_id(
        attachment_id=attachment_id
    )

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл домашней работы не найден"
        )

    try:
        return await service.update(
            attachment=attachment,
            attachment_data=attachment_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Удалить файл
# =====================================================

@router.delete(
    "/{attachment_id}",
    response_model=SubmissionAttachmentDeleteResponse,
    summary="Удалить файл домашней работы"
)
async def delete_submission_attachment_endpoint(
    attachment_id: int,
    deleted_by: int = Query(
        ...,
        gt=0,
        description=(
            "ID студента, удаляющего файл. "
            "Позже будет получаться из JWT"
        )
    ),
    session: AsyncSession = Depends(get_session)
):
    service = SubmissionAttachmentService(
        session=session
    )

    attachment = await service.get_by_id(
        attachment_id=attachment_id
    )

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл домашней работы не найден"
        )

    try:
        await service.delete(
            attachment=attachment,
            deleted_by=deleted_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error

    return SubmissionAttachmentDeleteResponse(
        deleted=True,
        attachment_id=attachment_id
    )