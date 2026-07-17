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
from news_service.schemas.schemas_post_view import (
    PostViewCountResponse,
    PostViewCreate,
    PostViewListResponse,
    PostViewRegistrationResponse
)
from news_service.services.service_post_view import (
    PostViewService
)


router = APIRouter(
    prefix="/post-views",
    tags=["Post views"]
)


# =====================================================
# Зарегистрировать просмотр
# =====================================================

@router.post(
    "/{post_id}",
    response_model=PostViewRegistrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Зарегистрировать просмотр публикации"
)
async def register_post_view_endpoint(
    post_id: int,
    view_data: PostViewCreate,
    session: AsyncSession = Depends(get_session)
):
    service = PostViewService(
        session=session
    )

    try:
        view, created, views_count = (
            await service.register_view(
                post_id=post_id,
                user_id=view_data.user_id
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error

    return PostViewRegistrationResponse(
        post_id=post_id,
        user_id=view_data.user_id,
        created=created,
        views_count=views_count,
        view=view
    )


# =====================================================
# Получить просмотры публикации
# =====================================================

@router.get(
    "/post/{post_id}",
    response_model=PostViewListResponse,
    summary="Получить список просмотров публикации"
)
async def get_post_views_endpoint(
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
    service = PostViewService(
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

    return PostViewListResponse(
        total=total,
        items=items
    )


# =====================================================
# Получить счётчик просмотров
# =====================================================

@router.get(
    "/post/{post_id}/count",
    response_model=PostViewCountResponse,
    summary="Получить количество просмотров"
)
async def get_post_view_count_endpoint(
    post_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = PostViewService(
        session=session
    )

    try:
        views_count = await service.get_count(
            post_id=post_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error

    return PostViewCountResponse(
        post_id=post_id,
        views_count=views_count
    )