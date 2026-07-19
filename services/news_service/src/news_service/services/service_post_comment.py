from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_post_comment_status import (
    PostCommentStatus
)
from common.utils.enum_post_status import (
    PostStatus
)
from news_service.models.model_post_comment import (
    PostComment
)
from news_service.repositories.repository_post import (
    PostRepository
)
from news_service.repositories.repository_post_comment import (
    PostCommentRepository
)
from news_service.schemas.schemas_post_comment import (
    PostCommentCreate,
    PostCommentUpdate
)
from news_service.services.service_external_validation import (
    external_validation_service
)
from news_service.messaging.messaging_event_publisher import (
    news_event_publisher
)


class PostCommentService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.post_repository = PostRepository(
            session=session
        )

        self.comment_repository = (
            PostCommentRepository(
                session=session
            )
        )

    # =================================================
    # Получить комментарий
    # =================================================

    async def get_by_id(
        self,
        comment_id: int,
        with_replies: bool = False
    ) -> PostComment | None:
        return await self.comment_repository.get_by_id(
            comment_id=comment_id,
            with_replies=with_replies
        )

    # =================================================
    # Получить комментарии публикации
    # =================================================

    async def get_by_post(
        self,
        post_id: int,
        include_hidden: bool = False,
        include_deleted: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[PostComment], int]:
        post = await self.post_repository.get_by_id(
            post_id=post_id
        )

        if post is None:
            raise ValueError(
                "Публикация не найдена"
            )

        return await self.comment_repository.get_by_post(
            post_id=post_id,
            include_hidden=include_hidden,
            include_deleted=include_deleted,
            skip=skip,
            limit=limit
        )

    # =================================================
    # Создать комментарий
    # =================================================

    async def create(
        self,
        comment_data: PostCommentCreate
    ) -> PostComment:

        await external_validation_service.get_active_user(
            user_id=comment_data.author_id
        )
        post = await self.post_repository.get_by_id(
            post_id=comment_data.post_id
        )

        if post is None:
            raise ValueError(
                "Публикация не найдена"
            )

        if not post.is_active:
            raise ValueError(
                "Публикация неактивна"
            )

        if post.status != PostStatus.PUBLISHED:
            raise ValueError(
                "Комментировать можно только "
                "опубликованные публикации"
            )

        if not post.allow_comments:
            raise ValueError(
                "Комментарии к этой публикации отключены"
            )

        parent_comment = None

        if comment_data.parent_comment_id is not None:
            parent_comment = (
                await self.comment_repository.get_by_id(
                    comment_id=(
                        comment_data.parent_comment_id
                    )
                )
            )

            if parent_comment is None:
                raise ValueError(
                    "Родительский комментарий не найден"
                )

            if parent_comment.post_id != post.id:
                raise ValueError(
                    "Нельзя ответить на комментарий "
                    "из другой публикации"
                )

            if (
                parent_comment.status
                != PostCommentStatus.PUBLISHED
            ):
                raise ValueError(
                    "Нельзя ответить на скрытый "
                    "или удалённый комментарий"
                )

            # Ограничиваем вложенность одним уровнем:
            # комментарий → ответы.
            if parent_comment.parent_comment_id is not None:
                raise ValueError(
                    "Нельзя отвечать на ответ. "
                    "Ответьте на основной комментарий"
                )

        create_data = comment_data.model_dump()

        create_data["status"] = (
            PostCommentStatus.PUBLISHED
        )

        comment = await self.comment_repository.create(
            comment_data=create_data
        )

        await (
            self.comment_repository
            .increment_post_comments(
                post=post
            )
        )

        # =============================================
        # Ответ на комментарий
        # =============================================

        if parent_comment is not None:
            # Автор не должен получать уведомление
            # о собственном ответе самому себе.
            if (
                    parent_comment.author_id
                    != comment.author_id
            ):
                await news_event_publisher.publish(
                    routing_key=(
                        "news.comment.reply_created"
                    ),
                    payload={
                        "post_id": post.id,
                        "post_title": post.title,
                        "post_slug": post.slug,
                        "comment_id": comment.id,
                        "parent_comment_id": (
                            parent_comment.id
                        ),
                        "author_id": (
                            comment.author_id
                        ),
                        "recipient_user_id": (
                            parent_comment.author_id
                        ),
                        "text": comment.text,
                        "created_at": (
                            comment.created_at
                        )
                    }
                )

        # =============================================
        # Новый основной комментарий
        # =============================================

        else:
            # Автор поста не получает уведомление,
            # если сам прокомментировал свой пост.
            if post.created_by != comment.author_id:
                await news_event_publisher.publish(
                    routing_key=(
                        "news.comment.created"
                    ),
                    payload={
                        "post_id": post.id,
                        "post_title": post.title,
                        "post_slug": post.slug,
                        "comment_id": comment.id,
                        "author_id": (
                            comment.author_id
                        ),
                        "recipient_user_id": (
                            post.created_by
                        ),
                        "text": comment.text,
                        "created_at": (
                            comment.created_at
                        )
                    }
                )

        return comment

    # =================================================
    # Изменить комментарий
    # =================================================

    async def update(
        self,
        comment: PostComment,
        comment_data: PostCommentUpdate
    ) -> PostComment:
        await external_validation_service.get_active_user(
            user_id=comment_data.edited_by
        )
        if (
            comment.status
            != PostCommentStatus.PUBLISHED
        ):
            raise ValueError(
                "Нельзя изменить скрытый "
                "или удалённый комментарий"
            )

        if comment.author_id != comment_data.edited_by:
            raise ValueError(
                "Изменить комментарий может "
                "только его автор"
            )

        return await self.comment_repository.update_text(
            comment=comment,
            text=comment_data.text
        )

    # =================================================
    # Удалить автором
    # =================================================

    async def delete(
        self,
        comment: PostComment,
        requested_by: int
    ) -> PostComment:
        await external_validation_service.get_active_user(
            user_id=requested_by
        )
        if comment.status == PostCommentStatus.DELETED:
            raise ValueError(
                "Комментарий уже удалён"
            )

        if comment.author_id != requested_by:
            raise ValueError(
                "Удалить комментарий может "
                "только его автор"
            )

        post = await self.post_repository.get_by_id(
            post_id=comment.post_id
        )

        if post is None:
            raise ValueError(
                "Публикация не найдена"
            )

        was_visible = (
            comment.status
            == PostCommentStatus.PUBLISHED
        )

        comment = await self.comment_repository.set_status(
            comment=comment,
            status=PostCommentStatus.DELETED,
            clear_text=True
        )

        if was_visible:
            await (
                self.comment_repository
                .decrement_post_comments(
                    post=post
                )
            )

        return comment

    # =================================================
    # Скрыть модератором
    # =================================================

    async def hide(
        self,
        comment: PostComment,
        requested_by: int
    ) -> PostComment:
        await external_validation_service.get_comment_moderator(
            user_id=requested_by
        )
        if comment.status == PostCommentStatus.HIDDEN:
            raise ValueError(
                "Комментарий уже скрыт"
            )

        if comment.status == PostCommentStatus.DELETED:
            raise ValueError(
                "Нельзя скрыть удалённый комментарий"
            )

        post = await self.post_repository.get_by_id(
            post_id=comment.post_id
        )

        if post is None:
            raise ValueError(
                "Публикация не найдена"
            )

        comment = await self.comment_repository.set_status(
            comment=comment,
            status=PostCommentStatus.HIDDEN
        )

        await (
            self.comment_repository
            .decrement_post_comments(
                post=post
            )
        )

        return comment

    # =================================================
    # Восстановить скрытый комментарий
    # =================================================

    async def restore(
        self,
        comment: PostComment,
        requested_by: int
    ) -> PostComment:
        await external_validation_service.get_comment_moderator(
            user_id=requested_by
        )
        if comment.status != PostCommentStatus.HIDDEN:
            raise ValueError(
                "Восстановить можно только "
                "скрытый комментарий"
            )

        post = await self.post_repository.get_by_id(
            post_id=comment.post_id
        )

        if post is None:
            raise ValueError(
                "Публикация не найдена"
            )

        comment = await self.comment_repository.set_status(
            comment=comment,
            status=PostCommentStatus.PUBLISHED
        )

        await (
            self.comment_repository
            .increment_post_comments(
                post=post
            )
        )

        return comment