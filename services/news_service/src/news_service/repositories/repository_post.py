from sqlalchemy import (
    func,
    or_,
    select
)
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_post_status import (
    PostStatus
)
from common.utils.enum_post_type import (
    PostType
)
from news_service.models.model_post import (
    Post
)


class PostRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить публикацию по ID
    # =================================================

    async def get_by_id(
        self,
        post_id: int
    ) -> Post | None:
        query = select(Post).where(
            Post.id == post_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить публикацию по slug
    # =================================================

    async def get_by_slug(
        self,
        slug: str
    ) -> Post | None:
        query = select(Post).where(
            Post.slug == slug
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить список публикаций
    # =================================================

    async def get_list(
        self,
        post_type: PostType | None = None,
        status: PostStatus | None = None,
        category: str | None = None,
        created_by: int | None = None,
        is_pinned: bool | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[Post], int]:
        filters = []

        if post_type is not None:
            filters.append(
                Post.post_type == post_type
            )

        if status is not None:
            filters.append(
                Post.status == status
            )

        if category is not None:
            filters.append(
                Post.category == category
            )

        if created_by is not None:
            filters.append(
                Post.created_by == created_by
            )

        if is_pinned is not None:
            filters.append(
                Post.is_pinned == is_pinned
            )

        if is_active is not None:
            filters.append(
                Post.is_active == is_active
            )

        if search:
            search_pattern = f"%{search.strip()}%"

            filters.append(
                or_(
                    Post.title.ilike(search_pattern),
                    Post.summary.ilike(search_pattern),
                    Post.content.ilike(search_pattern),
                    Post.category.ilike(search_pattern)
                )
            )

        posts_query = (
            select(Post)
            .where(*filters)
            .order_by(
                Post.is_pinned.desc(),
                Post.published_at.desc().nullslast(),
                Post.created_at.desc(),
                Post.id.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(func.count(Post.id))
            .where(*filters)
        )

        posts_result = await self.session.execute(
            posts_query
        )

        count_result = await self.session.execute(
            count_query
        )

        posts = list(
            posts_result.scalars().all()
        )

        total = count_result.scalar_one()

        return posts, total

    # =================================================
    # Создать публикацию
    # =================================================

    async def create(
        self,
        post_data: dict
    ) -> Post:
        post = Post(
            **post_data
        )

        self.session.add(post)

        await self.session.flush()
        await self.session.refresh(post)

        return post

    # =================================================
    # Изменить публикацию
    # =================================================

    async def update(
        self,
        post: Post,
        update_data: dict
    ) -> Post:
        for field_name, field_value in update_data.items():
            setattr(
                post,
                field_name,
                field_value
            )

        await self.session.flush()
        await self.session.refresh(post)

        return post