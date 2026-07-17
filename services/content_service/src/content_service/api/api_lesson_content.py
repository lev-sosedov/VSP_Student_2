from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.db.db_session import get_session
from content_service.schemas.schemas_lesson_content import (
    LessonContentCreate,
    LessonContentListResponse,
    LessonContentPublicationRequest,
    LessonContentResponse,
    LessonContentUpdate
)
from content_service.services.service_lesson_content import (
    LessonContentService
)


router = APIRouter(
    prefix="/lesson-contents",
    tags=["Lesson contents"]
)


# =====================================================
# Создать основной материал занятия
# =====================================================

@router.post(
    "",
    response_model=LessonContentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать материал занятия"
)
async def create_lesson_content_endpoint(
    content_data: LessonContentCreate,
    session: AsyncSession = Depends(get_session)
):
    service = LessonContentService(
        session=session
    )

    try:
        return await service.create(
            content_data=content_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Получить список материалов
# =====================================================

@router.get(
    "",
    response_model=LessonContentListResponse,
    summary="Получить список материалов занятий"
)
async def get_lesson_contents_endpoint(
    lesson_id: int | None = Query(
        default=None,
        gt=0
    ),
    created_by: int | None = Query(
        default=None,
        gt=0
    ),
    is_published: bool | None = Query(
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
    service = LessonContentService(
        session=session
    )

    contents, total = await service.get_list(
        lesson_id=lesson_id,
        created_by=created_by,
        is_published=is_published,
        skip=skip,
        limit=limit
    )

    return LessonContentListResponse(
        total=total,
        items=contents
    )


# =====================================================
# Получить материал по ID занятия
# Этот маршрут должен быть до /{content_id}
# =====================================================

@router.get(
    "/lesson/{lesson_id}",
    response_model=LessonContentResponse,
    summary="Получить материал конкретного занятия"
)
async def get_lesson_content_by_lesson_endpoint(
    lesson_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = LessonContentService(
        session=session
    )

    lesson_content = await service.get_by_lesson_id(
        lesson_id=lesson_id
    )

    if lesson_content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Материал занятия не найден"
        )

    return lesson_content


# =====================================================
# Получить материал по ID
# =====================================================

@router.get(
    "/{content_id}",
    response_model=LessonContentResponse,
    summary="Получить материал по ID"
)
async def get_lesson_content_endpoint(
    content_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = LessonContentService(
        session=session
    )

    lesson_content = await service.get_by_id(
        content_id=content_id
    )

    if lesson_content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Материал занятия не найден"
        )

    return lesson_content


# =====================================================
# Изменить материал
# =====================================================

@router.patch(
    "/{content_id}",
    response_model=LessonContentResponse,
    summary="Изменить материал занятия"
)
async def update_lesson_content_endpoint(
    content_id: int,
    content_data: LessonContentUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = LessonContentService(
        session=session
    )

    lesson_content = await service.get_by_id(
        content_id=content_id
    )

    if lesson_content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Материал занятия не найден"
        )

    return await service.update(
        lesson_content=lesson_content,
        content_data=content_data
    )


# =====================================================
# Опубликовать материал
# =====================================================

@router.post(
    "/{content_id}/publish",
    response_model=LessonContentResponse,
    summary="Опубликовать материал для студентов"
)
async def publish_lesson_content_endpoint(
    content_id: int,
    publication_data: LessonContentPublicationRequest,
    session: AsyncSession = Depends(get_session)
):
    service = LessonContentService(
        session=session
    )

    lesson_content = await service.get_by_id(
        content_id=content_id
    )

    if lesson_content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Материал занятия не найден"
        )

    try:
        return await service.publish(
            lesson_content=lesson_content,
            updated_by=publication_data.updated_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Снять материал с публикации
# =====================================================

@router.post(
    "/{content_id}/unpublish",
    response_model=LessonContentResponse,
    summary="Снять материал с публикации"
)
async def unpublish_lesson_content_endpoint(
    content_id: int,
    publication_data: LessonContentPublicationRequest,
    session: AsyncSession = Depends(get_session)
):
    service = LessonContentService(
        session=session
    )

    lesson_content = await service.get_by_id(
        content_id=content_id
    )

    if lesson_content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Материал занятия не найден"
        )

    try:
        return await service.unpublish(
            lesson_content=lesson_content,
            updated_by=publication_data.updated_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error