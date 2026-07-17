from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from news_service.db.db_session import (
    get_session
)
from news_service.schemas.schemas_post import (
    PostResponse
)
from news_service.schemas.schemas_post_media import (
    PostMediaActionRequest,
    PostMediaCreate,
    PostMediaDeleteResponse,
    PostMediaListResponse,
    PostMediaResponse,
    PostMediaUpdate
)
from news_service.services.service_post_media import (
    PostMediaService
)


router = APIRouter(
    prefix="/post-media",
    tags=["Post media"]
)


# =====================================================
# Создать медиа
# =====================================================

@router.post(
    "",
    response_model=PostMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить медиа в публикацию"
)
async def create_post_media_endpoint(
    media_data: PostMediaCreate,
    session: AsyncSession = Depends(get_session)
):
    service = PostMediaService(
        session=session
    )

    try:
        return await service.create(
            media_data=media_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Получить медиа публикации
# =====================================================

@router.get(
    "/post/{post_id}",
    response_model=PostMediaListResponse,
    summary="Получить медиа публикации"
)
async def get_post_media_endpoint(
    post_id: int,
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
    service = PostMediaService(
        session=session
    )

    try:
        items, total = await service.get_by_post(
            post_id=post_id,
            skip=skip,
            limit=limit
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error

    return PostMediaListResponse(
        total=total,
        items=items
    )


# =====================================================
# Получить медиа по ID
# =====================================================

@router.get(
    "/{media_id}",
    response_model=PostMediaResponse,
    summary="Получить медиа по ID"
)
async def get_post_media_by_id_endpoint(
    media_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = PostMediaService(
        session=session
    )

    media = await service.get_by_id(
        media_id=media_id
    )

    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медиа не найдено"
        )

    return media


# =====================================================
# Изменить медиа
# =====================================================

@router.patch(
    "/{media_id}",
    response_model=PostMediaResponse,
    summary="Изменить медиа"
)
async def update_post_media_endpoint(
    media_id: int,
    media_data: PostMediaUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = PostMediaService(
        session=session
    )

    media = await service.get_by_id(
        media_id=media_id
    )

    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медиа не найдено"
        )

    return await service.update(
        media=media,
        media_data=media_data
    )


# =====================================================
# Удалить медиа
# =====================================================

@router.delete(
    "/{media_id}",
    response_model=PostMediaDeleteResponse,
    summary="Удалить медиа"
)
async def delete_post_media_endpoint(
    media_id: int,
    action_data: PostMediaActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostMediaService(
        session=session
    )

    media = await service.get_by_id(
        media_id=media_id
    )

    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медиа не найдено"
        )

    try:
        return await service.delete(
            media=media,
            user_id=action_data.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Установить обложку
# =====================================================

@router.post(
    "/{media_id}/set-cover",
    response_model=PostResponse,
    summary="Установить медиа как обложку"
)
async def set_post_cover_endpoint(
    media_id: int,
    action_data: PostMediaActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostMediaService(
        session=session
    )

    media = await service.get_by_id(
        media_id=media_id
    )

    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медиа не найдено"
        )

    try:
        return await service.set_cover(
            media=media,
            user_id=action_data.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error