from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.db.db_session import get_session
from content_service.schemas.schemas_lesson_attachment import (
    LessonAttachmentCreate,
    LessonAttachmentDeleteResponse,
    LessonAttachmentListResponse,
    LessonAttachmentResponse,
    LessonAttachmentUpdate,
    LessonAttachmentVisibilityRequest
)
from content_service.services.service_lesson_attachment import (
    LessonAttachmentService
)


router = APIRouter(
    prefix="/lesson-attachments",
    tags=["Lesson attachments"]
)


# =====================================================
# Создать вложение
# =====================================================

@router.post(
    "",
    response_model=LessonAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить вложение к материалу занятия"
)
async def create_lesson_attachment_endpoint(
    attachment_data: LessonAttachmentCreate,
    session: AsyncSession = Depends(get_session)
):
    service = LessonAttachmentService(
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
    response_model=LessonAttachmentListResponse,
    summary="Получить список вложений"
)
async def get_lesson_attachments_endpoint(
    lesson_content_id: int | None = Query(
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
    service = LessonAttachmentService(
        session=session
    )

    attachments, total = await service.get_list(
        lesson_content_id=lesson_content_id,
        is_visible=is_visible,
        uploaded_by=uploaded_by,
        skip=skip,
        limit=limit
    )

    return LessonAttachmentListResponse(
        total=total,
        items=attachments
    )


# =====================================================
# Получить вложения конкретного материала
# Маршрут должен быть до /{attachment_id}
# =====================================================

@router.get(
    "/content/{lesson_content_id}",
    response_model=LessonAttachmentListResponse,
    summary="Получить вложения материала занятия"
)
async def get_content_attachments_endpoint(
    lesson_content_id: int,
    is_visible: bool | None = Query(
        default=None
    ),
    session: AsyncSession = Depends(get_session)
):
    service = LessonAttachmentService(
        session=session
    )

    attachments, total = await service.get_list(
        lesson_content_id=lesson_content_id,
        is_visible=is_visible,
        skip=0,
        limit=500
    )

    return LessonAttachmentListResponse(
        total=total,
        items=attachments
    )


# =====================================================
# Получить вложение по ID
# =====================================================

@router.get(
    "/{attachment_id}",
    response_model=LessonAttachmentResponse,
    summary="Получить вложение по ID"
)
async def get_lesson_attachment_endpoint(
    attachment_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = LessonAttachmentService(
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
    response_model=LessonAttachmentResponse,
    summary="Изменить вложение"
)
async def update_lesson_attachment_endpoint(
    attachment_id: int,
    attachment_data: LessonAttachmentUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = LessonAttachmentService(
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
    response_model=LessonAttachmentResponse,
    summary="Скрыть вложение от студентов"
)
async def hide_lesson_attachment_endpoint(
    attachment_id: int,
    visibility_data: LessonAttachmentVisibilityRequest,
    session: AsyncSession = Depends(get_session)
):
    service = LessonAttachmentService(
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
    response_model=LessonAttachmentResponse,
    summary="Показать вложение студентам"
)
async def show_lesson_attachment_endpoint(
    attachment_id: int,
    visibility_data: LessonAttachmentVisibilityRequest,
    session: AsyncSession = Depends(get_session)
):
    service = LessonAttachmentService(
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
    response_model=LessonAttachmentDeleteResponse,
    summary="Удалить вложение"
)
async def delete_lesson_attachment_endpoint(
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
    service = LessonAttachmentService(
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

    return LessonAttachmentDeleteResponse(
        deleted=True,
        attachment_id=attachment_id
    )