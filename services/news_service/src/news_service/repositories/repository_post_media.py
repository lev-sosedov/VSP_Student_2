from sqlalchemy import (
    func,
    select
)
from sqlalchemy.ext.asyncio import AsyncSession

from news_service.models.model_post_media import (
    PostMedia
)


class PostMediaRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить медиа по ID
    # =================================================

    async def get_by_id(
        self,
        media_id: int
    ) -> PostMedia | None:
        query = select(PostMedia).where(
            PostMedia.id == media_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить медиа публикации
    # =================================================

    async def get_by_post(
        self,
        post_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[PostMedia], int]:
        query = (
            select(PostMedia)
            .where(
                PostMedia.post_id == post_id
            )
            .order_by(
                PostMedia.sort_order,
                PostMedia.id
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = select(
            func.count(PostMedia.id)
        ).where(
            PostMedia.post_id == post_id
        )

        result = await self.session.execute(query)
        count_result = await self.session.execute(
            count_query
        )

        items = list(
            result.scalars().all()
        )

        total = count_result.scalar_one()

        return items, total

    # =================================================
    # Создать медиа
    # =================================================

    async def create(
        self,
        media_data: dict
    ) -> PostMedia:
        media = PostMedia(
            **media_data
        )

        self.session.add(media)

        await self.session.flush()
        await self.session.refresh(media)

        return media

    # =================================================
    # Изменить медиа
    # =================================================

    async def update(
        self,
        media: PostMedia,
        update_data: dict
    ) -> PostMedia:
        for field_name, field_value in update_data.items():
            setattr(
                media,
                field_name,
                field_value
            )

        await self.session.flush()
        await self.session.refresh(media)

        return media

    # =================================================
    # Удалить медиа
    # =================================================

    async def delete(
        self,
        media: PostMedia
    ) -> None:
        await self.session.delete(media)
        await self.session.flush()