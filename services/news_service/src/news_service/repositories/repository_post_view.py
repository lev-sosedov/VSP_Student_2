from sqlalchemy import (
    func,
    select
)
from sqlalchemy.ext.asyncio import AsyncSession

from news_service.models.model_post import (
    Post
)
from news_service.models.model_post_view import (
    PostView
)


class PostViewRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить просмотр пользователя
    # =================================================

    async def get_by_post_and_user(
        self,
        post_id: int,
        user_id: int
    ) -> PostView | None:
        query = select(PostView).where(
            PostView.post_id == post_id,
            PostView.user_id == user_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить просмотры публикации
    # =================================================

    async def get_by_post(
        self,
        post_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[PostView], int]:
        views_query = (
            select(PostView)
            .where(
                PostView.post_id == post_id
            )
            .order_by(
                PostView.viewed_at.desc(),
                PostView.id.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = select(
            func.count(PostView.id)
        ).where(
            PostView.post_id == post_id
        )

        views_result = await self.session.execute(
            views_query
        )

        count_result = await self.session.execute(
            count_query
        )

        views = list(
            views_result.scalars().all()
        )

        total = count_result.scalar_one()

        return views, total

    # =================================================
    # Создать просмотр
    # =================================================

    async def create(
        self,
        post_id: int,
        user_id: int
    ) -> PostView:
        view = PostView(
            post_id=post_id,
            user_id=user_id
        )

        self.session.add(view)

        await self.session.flush()
        await self.session.refresh(view)

        return view

    # =================================================
    # Увеличить счётчик публикации
    # =================================================

    async def increment_post_views(
        self,
        post: Post
    ) -> Post:
        post.views_count += 1

        await self.session.flush()
        await self.session.refresh(post)

        return post