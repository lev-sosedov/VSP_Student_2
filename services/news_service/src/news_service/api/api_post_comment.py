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
from news_service.schemas.schemas_post_comment import (
    PostCommentActionRequest,
    PostCommentCreate,
    PostCommentDetailResponse,
    PostCommentListResponse,
    PostCommentResponse,
    PostCommentUpdate
)
from news_service.services.service_post_comment import (
    PostCommentService
)


router = APIRouter(
    prefix="/post-comments",
    tags=["Post comments"]
)


async def get_comment_or_404(
    comment_id: int,
    service: PostCommentService,
    with_replies: bool = False
):
    comment = await service.get_by_id(
        comment_id=comment_id,
        with_replies=with_replies
    )

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )

    return comment


# =====================================================
# Создать комментарий
# =====================================================

@router.post(
    "",
    response_model=PostCommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить комментарий"
)
async def create_post_comment_endpoint(
    comment_data: PostCommentCreate,
    session: AsyncSession = Depends(get_session)
):
    service = PostCommentService(
        session=session
    )

    try:
        return await service.create(
            comment_data=comment_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Получить комментарии публикации
# =====================================================

@router.get(
    "/post/{post_id}",
    response_model=PostCommentListResponse,
    summary="Получить комментарии публикации"
)
async def get_post_comments_endpoint(
    post_id: int,
    include_hidden: bool = Query(
        default=False
    ),
    include_deleted: bool = Query(
        default=False
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
    service = PostCommentService(
        session=session
    )

    try:
        items, total = await service.get_by_post(
            post_id=post_id,
            include_hidden=include_hidden,
            include_deleted=include_deleted,
            skip=skip,
            limit=limit
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error

    return PostCommentListResponse(
        total=total,
        items=items
    )


# =====================================================
# Получить комментарий по ID
# =====================================================

@router.get(
    "/{comment_id}",
    response_model=PostCommentDetailResponse,
    summary="Получить комментарий по ID"
)
async def get_post_comment_endpoint(
    comment_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = PostCommentService(
        session=session
    )

    return await get_comment_or_404(
        comment_id=comment_id,
        service=service,
        with_replies=True
    )


# =====================================================
# Изменить комментарий
# =====================================================

@router.patch(
    "/{comment_id}",
    response_model=PostCommentResponse,
    summary="Изменить комментарий"
)
async def update_post_comment_endpoint(
    comment_id: int,
    comment_data: PostCommentUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = PostCommentService(
        session=session
    )

    comment = await get_comment_or_404(
        comment_id=comment_id,
        service=service
    )

    try:
        return await service.update(
            comment=comment,
            comment_data=comment_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Удалить комментарий автором
# =====================================================

@router.post(
    "/{comment_id}/delete",
    response_model=PostCommentResponse,
    summary="Удалить комментарий"
)
async def delete_post_comment_endpoint(
    comment_id: int,
    action_data: PostCommentActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostCommentService(
        session=session
    )

    comment = await get_comment_or_404(
        comment_id=comment_id,
        service=service
    )

    try:
        return await service.delete(
            comment=comment,
            requested_by=action_data.requested_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Скрыть комментарий
# =====================================================

@router.post(
    "/{comment_id}/hide",
    response_model=PostCommentResponse,
    summary="Скрыть комментарий модератором"
)
async def hide_post_comment_endpoint(
    comment_id: int,
    action_data: PostCommentActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostCommentService(
        session=session
    )

    comment = await get_comment_or_404(
        comment_id=comment_id,
        service=service
    )

    try:
        return await service.hide(
            comment=comment,
            requested_by=action_data.requested_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Восстановить скрытый комментарий
# =====================================================

@router.post(
    "/{comment_id}/restore",
    response_model=PostCommentResponse,
    summary="Восстановить скрытый комментарий"
)
async def restore_post_comment_endpoint(
    comment_id: int,
    action_data: PostCommentActionRequest,
    session: AsyncSession = Depends(get_session)
):
    service = PostCommentService(
        session=session
    )

    comment = await get_comment_or_404(
        comment_id=comment_id,
        service=service
    )

    try:
        return await service.restore(
            comment=comment,
            requested_by=action_data.requested_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error