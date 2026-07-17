from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_post_status import (
    PostStatus
)
from common.utils.enum_post_type import (
    PostType
)
from news_service.db.db_session import (
    get_session
)
from news_service.schemas.schemas_post import (
    PostActionRequest,
    PostCreate,
    PostListResponse,
    PostPublishRequest,
    PostResponse,
    PostUpdate
)
from news_service.services.service_post import (
    PostService
)


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


async def get_post_or_404(
    post_id: int,
    service: PostService
):
    post = await service.get_by_id(
        post_id=post_id
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Публикация не найдена"
        )

    return post


# =====================================================
# Создать черновик
# =====================================================

@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать черновик публикации"
)
async def create_post_endpoint(
    post_data: PostCreate,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(
        session=session
    )

    try:
        return await service.create(
            post_data=post_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Получить список
# =====================================================

@router.get(
    "",
    response_model=PostListResponse,
    summary="Получить список публикаций"
)
async def get_posts_endpoint(
    post_type: PostType | None = Query(
        default=None
    ),
    post_status: PostStatus | None = Query(
        default=None,
        alias="status"
    ),
    category: str | None = Query(
        default=None
    ),
    created_by: int | None = Query(
        default=None,
        gt=0
    ),
    is_pinned: bool | None = Query(
        default=None
    ),
    is_active: bool | None = Query(
        default=None
    ),
    search: str | None = Query(
        default=None,
        max_length=500
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
    service = PostService(
        session=session
    )

    posts, total = await service.get_list(
        post_type=post_type,
        status=post_status,
        category=category,
        created_by=created_by,
        is_pinned=is_pinned,
        is_active=is_active,
        search=search,
        skip=skip,
        limit=limit
    )

    return PostListResponse(
        total=total,
        items=posts
    )


# =====================================================
# Получить по slug
# Важно: этот маршрут должен находиться перед /{post_id}
# =====================================================

@router.get(
    "/slug/{slug}",
    response_model=PostResponse,
    summary="Получить публикацию по slug"
)
async def get_post_by_slug_endpoint(
    slug: str,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(
        session=session
    )

    post = await service.get_by_slug(
        slug=slug
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Публикация не найдена"
        )

    return post


# =====================================================
# Получить по ID
# =====================================================

@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Получить публикацию по ID"
)
async def get_post_endpoint(
    post_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(
        session=session
    )

    return await get_post_or_404(
        post_id=post_id,
        service=service
    )


# =====================================================
# Изменить
# =====================================================

@router.patch(
    "/{post_id}",
    response_model=PostResponse,
    summary="Изменить публикацию"
)
async def update_post_endpoint(
    post_id: int,
    post_data: PostUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(
        session=session
    )

    post = await get_post_or_404(
        post_id=post_id,
        service=service
    )

    try:
        return await service.update(
            post=post,
            post_data=post_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Опубликовать
# =====================================================

@router.post(
    "/{post_id}/publish",
    response_model=PostResponse,
    summary="Опубликовать публикацию"
)
async def publish_post_endpoint(
    post_id: int,
    publish_data: PostPublishRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(
        session=session
    )

    post = await get_post_or_404(
        post_id=post_id,
        service=service
    )

    try:
        return await service.publish(
            post=post,
            publish_data=publish_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Снять с публикации
# =====================================================

@router.post(
    "/{post_id}/unpublish",
    response_model=PostResponse,
    summary="Снять публикацию с публикации"
)
async def unpublish_post_endpoint(
    post_id: int,
    action_data: PostActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(
        session=session
    )

    post = await get_post_or_404(
        post_id=post_id,
        service=service
    )

    try:
        return await service.unpublish(
            post=post,
            user_id=action_data.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Закрепить
# =====================================================

@router.post(
    "/{post_id}/pin",
    response_model=PostResponse,
    summary="Закрепить публикацию"
)
async def pin_post_endpoint(
    post_id: int,
    action_data: PostActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(session=session)

    post = await get_post_or_404(
        post_id=post_id,
        service=service
    )

    try:
        return await service.pin(
            post=post,
            user_id=action_data.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Открепить
# =====================================================

@router.post(
    "/{post_id}/unpin",
    response_model=PostResponse,
    summary="Открепить публикацию"
)
async def unpin_post_endpoint(
    post_id: int,
    action_data: PostActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(session=session)

    post = await get_post_or_404(
        post_id=post_id,
        service=service
    )

    try:
        return await service.unpin(
            post=post,
            user_id=action_data.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Архивировать
# =====================================================

@router.post(
    "/{post_id}/archive",
    response_model=PostResponse,
    summary="Архивировать публикацию"
)
async def archive_post_endpoint(
    post_id: int,
    action_data: PostActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(session=session)

    post = await get_post_or_404(
        post_id=post_id,
        service=service
    )

    try:
        return await service.archive(
            post=post,
            user_id=action_data.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Восстановить
# =====================================================

@router.post(
    "/{post_id}/restore",
    response_model=PostResponse,
    summary="Восстановить публикацию из архива"
)
async def restore_post_endpoint(
    post_id: int,
    action_data: PostActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(session=session)

    post = await get_post_or_404(
        post_id=post_id,
        service=service
    )

    try:
        return await service.restore(
            post=post,
            user_id=action_data.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Деактивировать
# =====================================================

@router.post(
    "/{post_id}/deactivate",
    response_model=PostResponse,
    summary="Деактивировать публикацию"
)
async def deactivate_post_endpoint(
    post_id: int,
    action_data: PostActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(session=session)

    post = await get_post_or_404(
        post_id=post_id,
        service=service
    )

    try:
        return await service.deactivate(
            post=post,
            user_id=action_data.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Активировать
# =====================================================

@router.post(
    "/{post_id}/activate",
    response_model=PostResponse,
    summary="Активировать публикацию"
)
async def activate_post_endpoint(
    post_id: int,
    action_data: PostActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostService(session=session)

    post = await get_post_or_404(
        post_id=post_id,
        service=service
    )

    try:
        return await service.activate(
            post=post,
            user_id=action_data.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error