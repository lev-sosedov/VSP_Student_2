from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_post_status import (
    PostStatus
)
from news_service.models.model_post_view import (
    PostView
)
from news_service.repositories.repository_post import (
    PostRepository
)
from news_service.repositories.repository_post_view import (
    PostViewRepository
)
from news_service.services.service_external_validation import (
    external_validation_service
)


class PostViewService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.post_repository = PostRepository(
            session=session
        )

        self.view_repository = PostViewRepository(
            session=session
        )

    # =================================================
    # Зарегистрировать просмотр
    # =================================================

    async def register_view(
        self,
        post_id: int,
        user_id: int
    ) -> tuple[PostView, bool, int]:
        await external_validation_service.get_active_user(
            user_id=user_id
        )
        post = await self.post_repository.get_by_id(
            post_id=post_id
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
                "Просматривать можно только "
                "опубликованные публикации"
            )

        existing_view = (
            await self.view_repository
            .get_by_post_and_user(
                post_id=post_id,
                user_id=user_id
            )
        )

        if existing_view is not None:
            return (
                existing_view,
                False,
                post.views_count
            )

        view = await self.view_repository.create(
            post_id=post_id,
            user_id=user_id
        )

        post = (
            await self.view_repository
            .increment_post_views(
                post=post
            )
        )

        return (
            view,
            True,
            post.views_count
        )

    # =================================================
    # Получить просмотры публикации
    # =================================================

    async def get_by_post(
        self,
        post_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[PostView], int]:
        post = await self.post_repository.get_by_id(
            post_id=post_id
        )

        if post is None:
            raise ValueError(
                "Публикация не найдена"
            )

        return await self.view_repository.get_by_post(
            post_id=post_id,
            skip=skip,
            limit=limit
        )

    # =================================================
    # Получить счётчик
    # =================================================

    async def get_count(
        self,
        post_id: int
    ) -> int:
        post = await self.post_repository.get_by_id(
            post_id=post_id
        )

        if post is None:
            raise ValueError(
                "Публикация не найдена"
            )

        return post.views_count