from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.db.db_session import get_session
from content_service.schemas.schemas_homework import (
    HomeworkActivityRequest,
    HomeworkCreate,
    HomeworkListResponse,
    HomeworkPublicationRequest,
    HomeworkResponse,
    HomeworkUpdate
)
from content_service.services.service_homework import (
    HomeworkService
)


router = APIRouter(
    prefix="/homeworks",
    tags=["Homeworks"]
)


# =====================================================
# Создать домашнее задание
# =====================================================

@router.post(
    "",
    response_model=HomeworkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать домашнее задание"
)
async def create_homework_endpoint(
    homework_data: HomeworkCreate,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkService(
        session=session
    )

    try:
        return await service.create(
            homework_data=homework_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Получить список домашних заданий
# =====================================================

@router.get(
    "",
    response_model=HomeworkListResponse,
    summary="Получить список домашних заданий"
)
async def get_homeworks_endpoint(
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
    is_active: bool | None = Query(
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
    service = HomeworkService(
        session=session
    )

    homeworks, total = await service.get_list(
        lesson_id=lesson_id,
        created_by=created_by,
        is_published=is_published,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

    return HomeworkListResponse(
        total=total,
        items=homeworks
    )


# =====================================================
# Получить задание конкретного занятия
# Этот маршрут должен быть до /{homework_id}
# =====================================================

@router.get(
    "/lesson/{lesson_id}",
    response_model=HomeworkResponse,
    summary="Получить домашнее задание занятия"
)
async def get_homework_by_lesson_endpoint(
    lesson_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkService(
        session=session
    )

    homework = await service.get_by_lesson_id(
        lesson_id=lesson_id
    )

    if homework is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашнее задание не найдено"
        )

    return homework


# =====================================================
# Получить задание по ID
# =====================================================

@router.get(
    "/{homework_id}",
    response_model=HomeworkResponse,
    summary="Получить домашнее задание по ID"
)
async def get_homework_endpoint(
    homework_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkService(
        session=session
    )

    homework = await service.get_by_id(
        homework_id=homework_id
    )

    if homework is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашнее задание не найдено"
        )

    return homework


# =====================================================
# Изменить домашнее задание
# =====================================================

@router.patch(
    "/{homework_id}",
    response_model=HomeworkResponse,
    summary="Изменить домашнее задание"
)
async def update_homework_endpoint(
    homework_id: int,
    homework_data: HomeworkUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkService(
        session=session
    )

    homework = await service.get_by_id(
        homework_id=homework_id
    )

    if homework is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашнее задание не найдено"
        )

    try:
        return await service.update(
            homework=homework,
            homework_data=homework_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Опубликовать домашнее задание
# =====================================================

@router.post(
    "/{homework_id}/publish",
    response_model=HomeworkResponse,
    summary="Опубликовать домашнее задание"
)
async def publish_homework_endpoint(
    homework_id: int,
    publication_data: HomeworkPublicationRequest,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkService(
        session=session
    )

    homework = await service.get_by_id(
        homework_id=homework_id
    )

    if homework is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашнее задание не найдено"
        )

    try:
        return await service.publish(
            homework=homework,
            updated_by=publication_data.updated_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Снять домашнее задание с публикации
# =====================================================

@router.post(
    "/{homework_id}/unpublish",
    response_model=HomeworkResponse,
    summary="Снять домашнее задание с публикации"
)
async def unpublish_homework_endpoint(
    homework_id: int,
    publication_data: HomeworkPublicationRequest,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkService(
        session=session
    )

    homework = await service.get_by_id(
        homework_id=homework_id
    )

    if homework is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашнее задание не найдено"
        )

    try:
        return await service.unpublish(
            homework=homework,
            updated_by=publication_data.updated_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Деактивировать домашнее задание
# =====================================================

@router.post(
    "/{homework_id}/deactivate",
    response_model=HomeworkResponse,
    summary="Деактивировать домашнее задание"
)
async def deactivate_homework_endpoint(
    homework_id: int,
    activity_data: HomeworkActivityRequest,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkService(
        session=session
    )

    homework = await service.get_by_id(
        homework_id=homework_id
    )

    if homework is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашнее задание не найдено"
        )

    try:
        return await service.deactivate(
            homework=homework,
            updated_by=activity_data.updated_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Активировать домашнее задание
# =====================================================

@router.post(
    "/{homework_id}/activate",
    response_model=HomeworkResponse,
    summary="Активировать домашнее задание"
)
async def activate_homework_endpoint(
    homework_id: int,
    activity_data: HomeworkActivityRequest,
    session: AsyncSession = Depends(get_session)
):
    service = HomeworkService(
        session=session
    )

    homework = await service.get_by_id(
        homework_id=homework_id
    )

    if homework is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Домашнее задание не найдено"
        )

    try:
        return await service.activate(
            homework=homework,
            updated_by=activity_data.updated_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error