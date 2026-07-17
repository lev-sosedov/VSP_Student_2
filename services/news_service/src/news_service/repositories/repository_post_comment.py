from datetime import datetime

from sqlalchemy import (
    func,
    select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from common.utils.enum_post_comment_status import (
    PostCommentStatus
)
from news_service.models.model_post import (
    Post
)
from news_service.models.model_post_comment import (
    PostComment
)


class PostCommentRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить комментарий по ID
    # =================================================

    async def get_by_id(
        self,
        comment_id: int,
        with_replies: bool = False
    ) -> PostComment | None:
        query = select(PostComment).where(
            PostComment.id == comment_id
        )

        if with_replies:
            query = query.options(
                selectinload(
                    PostComment.replies
                )
            )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить корневые комментарии публикации
    # =================================================

    async def get_by_post(
        self,
        post_id: int,
        include_hidden: bool = False,
        include_deleted: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[PostComment], int]:
        filters = [
            PostComment.post_id == post_id,
            PostComment.parent_comment_id.is_(None)
        ]

        excluded_statuses = []

        if not include_hidden:
            excluded_statuses.append(
                PostCommentStatus.HIDDEN
            )

        if not include_deleted:
            excluded_statuses.append(
                PostCommentStatus.DELETED
            )

        if excluded_statuses:
            filters.append(
                PostComment.status.not_in(
                    excluded_statuses
                )
            )

        comments_query = (
            select(PostComment)
            .options(
                selectinload(
                    PostComment.replies
                )
            )
            .where(*filters)
            .order_by(
                PostComment.created_at.asc(),
                PostComment.id.asc()
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(func.count(PostComment.id))
            .where(*filters)
        )

        comments_result = await self.session.execute(
            comments_query
        )

        count_result = await self.session.execute(
            count_query
        )

        comments = list(
            comments_result.scalars().all()
        )

        total = count_result.scalar_one()

        return comments, total

    # =================================================
    # Создать комментарий
    # =================================================

    async def create(
        self,
        comment_data: dict
    ) -> PostComment:
        comment = PostComment(
            **comment_data
        )

        self.session.add(comment)

        await self.session.flush()
        await self.session.refresh(comment)

        return comment

    # =================================================
    # Изменить текст
    # =================================================

    async def update_text(
        self,
        comment: PostComment,
        text: str
    ) -> PostComment:
        comment.text = text
        comment.is_edited = True
        comment.edited_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(comment)

        return comment

    # =================================================
    # Изменить статус
    # =================================================

    async def set_status(
        self,
        comment: PostComment,
        status: PostCommentStatus,
        clear_text: bool = False
    ) -> PostComment:
        comment.status = status

        if status == PostCommentStatus.DELETED:
            comment.deleted_at = datetime.utcnow()

            if clear_text:
                comment.text = None

        else:
            comment.deleted_at = None

        await self.session.flush()
        await self.session.refresh(comment)

        return comment

    # =================================================
    # Увеличить comments_count
    # =================================================

    async def increment_post_comments(
        self,
        post: Post
    ) -> Post:
        post.comments_count += 1

        await self.session.flush()
        await self.session.refresh(post)

        return post

    # =================================================
    # Уменьшить comments_count
    # =================================================

    async def decrement_post_comments(
        self,
        post: Post
    ) -> Post:
        post.comments_count = max(
            post.comments_count - 1,
            0
        )

        await self.session.flush()
        await self.session.refresh(post)

        return post