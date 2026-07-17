from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.db.db_session import get_session
from content_service.schemas.schemas_homework_attachment import (
    HomeworkAttachmentCreate,
    HomeworkAttachmentDeleteResponse,
    HomeworkAttachmentListResponse,
    HomeworkAttachmentResponse,
    HomeworkAttachmentUpdate,
    HomeworkAttachmentVisibilityRequest
)
from content_service.services.service_homework_attachment import (
    HomeworkAttachmentService
)


router = APIRouter(
    prefix="/homework-attachments",
    tags=["Homework attachments"]
)


# =====================================================
# Создать вложение домашнего задания
# =====================================================

@router.post(
    "",
    response_model=HomeworkAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить вложение к домашнему заданию"
)
async def create_homework_attachment_endpoint(
    attachment_data: HomeworkAttachmentCreate,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkAttachmentService(
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
# Получить список вложений
# =====================================================

@router.get(
    "",
    response_model=HomeworkAttachmentListResponse,
    summary="Получить вложения домашних заданий"
)
async def get_homework_attachments_endpoint(
    homework_id: int | None = Query(
        default=None,
        gt=0
    ),
    is_visible: bool | None = Query(
        default=None
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
    service = HomeworkAttachmentService(
        session=session
    )

    attachments, total = await service.get_list(
        homework_id=homework_id,
        is_visible=is_visible,
        uploaded_by=uploaded_by,
        skip=skip,
        limit=limit
    )

    return HomeworkAttachmentListResponse(
        total=total,
        items=attachments
    )


# =====================================================
# Получить вложения домашнего задания
# Маршрут должен быть до /{attachment_id}
# =====================================================

@router.get(
    "/homework/{homework_id}",
    response_model=HomeworkAttachmentListResponse,
    summary="Получить вложения домашнего задания"
)
async def get_homework_attachments_by_homework_endpoint(
    homework_id: int,
    is_visible: bool | None = Query(
        default=None
    ),
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkAttachmentService(
        session=session
    )

    attachments, total = await service.get_list(
        homework_id=homework_id,
        is_visible=is_visible,
        skip=0,
        limit=500
    )

    return HomeworkAttachmentListResponse(
        total=total,
        items=attachments
    )


# =====================================================
# Получить вложение по ID
# =====================================================

@router.get(
    "/{attachment_id}",
    response_model=HomeworkAttachmentResponse,
    summary="Получить вложение по ID"
)
async def get_homework_attachment_endpoint(
    attachment_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkAttachmentService(
        session=session
    )

    attachment = await service.get_by_id(
        attachment_id=attachment_id
    )

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вложение не найдено"
        )

    return attachment


# =====================================================
# Изменить вложение
# =====================================================

@router.patch(
    "/{attachment_id}",
    response_model=HomeworkAttachmentResponse,
    summary="Изменить вложение домашнего задания"
)
async def update_homework_attachment_endpoint(
    attachment_id: int,
    attachment_data: HomeworkAttachmentUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkAttachmentService(
        session=session
    )

    attachment = await service.get_by_id(
        attachment_id=attachment_id
    )

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вложение не найдено"
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
# Скрыть вложение
# =====================================================

@router.post(
    "/{attachment_id}/hide",
    response_model=HomeworkAttachmentResponse,
    summary="Скрыть вложение от студентов"
)
async def hide_homework_attachment_endpoint(
    attachment_id: int,
    visibility_data: HomeworkAttachmentVisibilityRequest,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkAttachmentService(
        session=session
    )

    attachment = await service.get_by_id(
        attachment_id=attachment_id
    )

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вложение не найдено"
        )

    try:
        return await service.hide(
            attachment=attachment,
            updated_by=visibility_data.updated_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Показать вложение
# =====================================================

@router.post(
    "/{attachment_id}/show",
    response_model=HomeworkAttachmentResponse,
    summary="Показать вложение студентам"
)
async def show_homework_attachment_endpoint(
    attachment_id: int,
    visibility_data: HomeworkAttachmentVisibilityRequest,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkAttachmentService(
        session=session
    )

    attachment = await service.get_by_id(
        attachment_id=attachment_id
    )

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вложение не найдено"
        )

    try:
        return await service.show(
            attachment=attachment,
            updated_by=visibility_data.updated_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Удалить вложение
# =====================================================

@router.delete(
    "/{attachment_id}",
    response_model=HomeworkAttachmentDeleteResponse,
    summary="Удалить вложение домашнего задания"
)
async def delete_homework_attachment_endpoint(
    attachment_id: int,
    deleted_by: int = Query(
        ...,
        gt=0,
        description=(
            "ID пользователя, удаляющего вложение. "
            "Позже будет получаться из JWT"
        )
    ),
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkAttachmentService(
        session=session
    )

    attachment = await service.get_by_id(
        attachment_id=attachment_id
    )

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вложение не найдено"
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

    return HomeworkAttachmentDeleteResponse(
        deleted=True,
        attachment_id=attachment_id
    )