from sqlalchemy.ext.asyncio import AsyncSession

from news_service.models.model_post_media import (
    PostMedia
)
from news_service.repositories.repository_post import (
    PostRepository
)
from news_service.repositories.repository_post_media import (
    PostMediaRepository
)
from news_service.schemas.schemas_post_media import (
    PostMediaCreate,
    PostMediaUpdate
)
from news_service.services.service_external_validation import (
    external_validation_service
)


class PostMediaService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.post_repository = PostRepository(
            session=session
        )

        self.media_repository = PostMediaRepository(
            session=session
        )

    # =================================================
    # Получить медиа
    # =================================================

    async def get_by_id(
        self,
        media_id: int
    ) -> PostMedia | None:
        return await self.media_repository.get_by_id(
            media_id=media_id
        )

    # =================================================
    # Получить список медиа
    # =================================================

    async def get_by_post(
        self,
        post_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[PostMedia], int]:
        post = await self.post_repository.get_by_id(
            post_id=post_id
        )

        if post is None:
            raise ValueError(
                "Публикация не найдена"
            )

        return await self.media_repository.get_by_post(
            post_id=post_id,
            skip=skip,
            limit=limit
        )

    # =================================================
    # Создать медиа
    # =================================================

    async def create(
        self,
        media_data: PostMediaCreate
    ) -> PostMedia:
        await external_validation_service.get_content_manager(
            user_id=media_data.uploaded_by
        )
        post = await self.post_repository.get_by_id(
            post_id=media_data.post_id
        )

        if post is None:
            raise ValueError(
                "Публикация не найдена"
            )

        if not post.is_active:
            raise ValueError(
                "Нельзя добавлять медиа "
                "в неактивную публикацию"
            )

        create_data = media_data.model_dump()

        media = await self.media_repository.create(
            media_data=create_data
        )

        return media

    # =================================================
    # Изменить медиа
    # =================================================

    async def update(
        self,
        media: PostMedia,
        media_data: PostMediaUpdate
    ) -> PostMedia:
        await external_validation_service.get_content_manager(
            user_id=media_data.updated_by
        )
        update_data = media_data.model_dump(
            exclude_unset=True,
            exclude={
                "updated_by"
            }
        )

        return await self.media_repository.update(
            media=media,
            update_data=update_data
        )

    # =================================================
    # Удалить медиа
    # =================================================

    async def delete(
        self,
        media: PostMedia,
        user_id: int
    ) -> dict:
        await external_validation_service.get_content_manager(
            user_id=user_id
        )
        post = await self.post_repository.get_by_id(
            post_id=media.post_id
        )

        if post is None:
            raise ValueError(
                "Публикация не найдена"
            )

        media_id = media.id
        post_id = media.post_id

        # Если удаляемая запись используется как обложка,
        # очищаем обложку публикации.
        if post.cover_media_url == media.file_url:
            await self.post_repository.update(
                post=post,
                update_data={
                    "cover_media_url": None,
                    "cover_media_type": None,
                    "cover_preview_url": None,
                    "cover_width": None,
                    "cover_height": None,
                    "updated_by": user_id
                }
            )

        await self.media_repository.delete(
            media=media
        )

        return {
            "media_id": media_id,
            "post_id": post_id,
            "deleted": True
        }

    # =================================================
    # Установить медиа как обложку
    # =================================================

    async def set_cover(
        self,
        media: PostMedia,
        user_id: int
    ):
        await external_validation_service.get_content_manager(
            user_id=user_id
        )
        post = await self.post_repository.get_by_id(
            post_id=media.post_id
        )

        if post is None:
            raise ValueError(
                "Публикация не найдена"
            )

        return await self.post_repository.update(
            post=post,
            update_data={
                "cover_media_url": media.file_url,
                "cover_media_type": media.media_type.value,
                "cover_preview_url": media.preview_url,
                "cover_width": media.width,
                "cover_height": media.height,
                "updated_by": user_id
            }
        )
