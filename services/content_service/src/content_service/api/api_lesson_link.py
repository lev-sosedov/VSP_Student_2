from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.db.db_session import get_session
from content_service.schemas.schemas_lesson_link import (
    LessonLinkCreate,
    LessonLinkDeleteResponse,
    LessonLinkListResponse,
    LessonLinkResponse,
    LessonLinkUpdate,
    LessonLinkVisibilityRequest
)
from content_service.services.service_lesson_link import (
    LessonLinkService
)


router = APIRouter(
    prefix="/lesson-links",
    tags=["Lesson links"]
)


# =====================================================
# Создать ссылку
# =====================================================

@router.post(
    "",
    response_model=LessonLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить ссылку к материалу занятия"
)
async def create_lesson_link_endpoint(
    link_data: LessonLinkCreate,
    session: AsyncSession = Depends(get_session)
):
    service = LessonLinkService(
        session=session
    )

    try:
        return await service.create(
            link_data=link_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Получить список ссылок
# =====================================================

@router.get(
    "",
    response_model=LessonLinkListResponse,
    summary="Получить список ссылок"
)
async def get_lesson_links_endpoint(
    lesson_content_id: int | None = Query(
        default=None,
        gt=0
    ),
    is_visible: bool | None = Query(
        default=None
    ),
    added_by: int | None = Query(
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
    service = LessonLinkService(
        session=session
    )

    links, total = await service.get_list(
        lesson_content_id=lesson_content_id,
        is_visible=is_visible,
        added_by=added_by,
        skip=skip,
        limit=limit
    )

    return LessonLinkListResponse(
        total=total,
        items=links
    )


# =====================================================
# Получить ссылки конкретного материала
# Этот маршрут должен находиться до /{link_id}
# =====================================================

@router.get(
    "/content/{lesson_content_id}",
    response_model=LessonLinkListResponse,
    summary="Получить ссылки материала занятия"
)
async def get_content_links_endpoint(
    lesson_content_id: int,
    is_visible: bool | None = Query(
        default=None
    ),
    session: AsyncSession = Depends(get_session)
):
    service = LessonLinkService(
        session=session
    )

    links, total = await service.get_list(
        lesson_content_id=lesson_content_id,
        is_visible=is_visible,
        skip=0,
        limit=500
    )

    return LessonLinkListResponse(
        total=total,
        items=links
    )


# =====================================================
# Получить ссылку по ID
# =====================================================

@router.get(
    "/{link_id}",
    response_model=LessonLinkResponse,
    summary="Получить ссылку по ID"
)
async def get_lesson_link_endpoint(
    link_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = LessonLinkService(
        session=session
    )

    lesson_link = await service.get_by_id(
        link_id=link_id
    )

    if lesson_link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ссылка не найдена"
        )

    return lesson_link


# =====================================================
# Изменить ссылку
# =====================================================

@router.patch(
    "/{link_id}",
    response_model=LessonLinkResponse,
    summary="Изменить ссылку"
)
async def update_lesson_link_endpoint(
    link_id: int,
    link_data: LessonLinkUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = LessonLinkService(
        session=session
    )

    lesson_link = await service.get_by_id(
        link_id=link_id
    )

    if lesson_link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ссылка не найдена"
        )

    try:
        return await service.update(
            lesson_link=lesson_link,
            link_data=link_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Скрыть ссылку
# =====================================================

@router.post(
    "/{link_id}/hide",
    response_model=LessonLinkResponse,
    summary="Скрыть ссылку от студентов"
)
async def hide_lesson_link_endpoint(
    link_id: int,
    visibility_data: LessonLinkVisibilityRequest,
    session: AsyncSession = Depends(get_session)
):
    service = LessonLinkService(
        session=session
    )

    lesson_link = await service.get_by_id(
        link_id=link_id
    )

    if lesson_link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ссылка не найдена"
        )

    try:
        return await service.hide(
            lesson_link=lesson_link,
            updated_by=visibility_data.updated_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Показать ссылку
# =====================================================

@router.post(
    "/{link_id}/show",
    response_model=LessonLinkResponse,
    summary="Показать ссылку студентам"
)
async def show_lesson_link_endpoint(
    link_id: int,
    visibility_data: LessonLinkVisibilityRequest,
    session: AsyncSession = Depends(get_session)
):
    service = LessonLinkService(
        session=session
    )

    lesson_link = await service.get_by_id(
        link_id=link_id
    )

    if lesson_link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ссылка не найдена"
        )

    try:
        return await service.show(
            lesson_link=lesson_link,
            updated_by=visibility_data.updated_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Удалить ссылку
# =====================================================

@router.delete(
    "/{link_id}",
    response_model=LessonLinkDeleteResponse,
    summary="Удалить ссылку"
)
async def delete_lesson_link_endpoint(
    link_id: int,
    deleted_by: int = Query(
        ...,
        gt=0,
        description=(
            "ID пользователя, удаляющего ссылку. "
            "Позже будет получаться из JWT"
        )
    ),
    session: AsyncSession = Depends(get_session)
):
    service = LessonLinkService(
        session=session
    )

    lesson_link = await service.get_by_id(
        link_id=link_id
    )

    if lesson_link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ссылка не найдена"
        )

    try:
        await service.delete(
            lesson_link=lesson_link,
            deleted_by=deleted_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error

    return LessonLinkDeleteResponse(
        deleted=True,
        link_id=link_id
    )