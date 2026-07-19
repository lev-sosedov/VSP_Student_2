import re
from datetime import datetime
from uuid import uuid4

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
from news_service.repositories.repository_post import (
    PostRepository
)
from news_service.schemas.schemas_post import (
    PostCreate,
    PostPublishRequest,
    PostUpdate
)
from news_service.services.service_external_validation import (
    external_validation_service
)
from news_service.messaging.messaging_event_publisher import (
    news_event_publisher
)


class PostService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.repository = PostRepository(
            session=session
        )

    # =================================================
    # Получить публикацию по ID
    # =================================================

    async def get_by_id(
        self,
        post_id: int
    ) -> Post | None:
        return await self.repository.get_by_id(
            post_id=post_id
        )

    # =================================================
    # Получить публикацию по slug
    # =================================================

    async def get_by_slug(
        self,
        slug: str
    ) -> Post | None:
        return await self.repository.get_by_slug(
            slug=slug
        )

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
        return await self.repository.get_list(
            post_type=post_type,
            status=status,
            category=category,
            created_by=created_by,
            is_pinned=is_pinned,
            is_active=is_active,
            search=search,
            skip=skip,
            limit=limit
        )

    # =================================================
    # Создать черновик
    # =================================================

    async def create(
        self,
        post_data: PostCreate
    ) -> Post:
        await external_validation_service.get_content_manager(
            user_id=post_data.created_by
        )
        create_data = post_data.model_dump()

        requested_slug = create_data.get("slug")

        if requested_slug:
            slug = self._normalize_slug(
                requested_slug
            )

        else:
            slug = self._generate_slug(
                title=post_data.title
            )

        slug = await self._make_slug_unique(
            slug=slug
        )

        create_data["slug"] = slug
        create_data["status"] = PostStatus.DRAFT

        return await self.repository.create(
            post_data=create_data
        )

    # =================================================
    # Изменить публикацию
    # =================================================

    async def update(
        self,
        post: Post,
        post_data: PostUpdate
    ) -> Post:
        await external_validation_service.get_content_manager(
            user_id=post_data.updated_by
        )
        if post.status == PostStatus.ARCHIVED:
            raise ValueError(
                "Сначала восстановите публикацию из архива"
            )

        update_data = post_data.model_dump(
            exclude_unset=True
        )

        updated_by = update_data.pop(
            "updated_by"
        )

        update_data["updated_by"] = updated_by

        if "slug" in update_data:
            requested_slug = self._normalize_slug(
                update_data["slug"]
            )

            existing_post = await self.repository.get_by_slug(
                slug=requested_slug
            )

            if (
                existing_post is not None
                and existing_post.id != post.id
            ):
                raise ValueError(
                    "Публикация с таким slug уже существует"
                )

            update_data["slug"] = requested_slug

        return await self.repository.update(
            post=post,
            update_data=update_data
        )

    # =================================================
    # Опубликовать
    # =================================================

    async def publish(
        self,
        post: Post,
        publish_data: PostPublishRequest
    ) -> Post:
        await external_validation_service.get_content_manager(
            user_id=publish_data.published_by
        )
        if post.status == PostStatus.PUBLISHED:
            raise ValueError(
                "Публикация уже опубликована"
            )

        if post.status == PostStatus.ARCHIVED:
            raise ValueError(
                "Нельзя опубликовать архивную публикацию"
            )

        if not post.is_active:
            raise ValueError(
                "Нельзя опубликовать неактивную публикацию"
            )

        if not post.content and not post.cover_media_url:
            raise ValueError(
                "Для публикации нужен текст или обложка"
            )

        update_data = {
            "status": PostStatus.PUBLISHED,
            "published_by": publish_data.published_by,
            "published_at": datetime.utcnow(),
            "updated_by": publish_data.published_by
        }

        if publish_data.send_notification is not None:
            update_data["send_notification"] = (
                publish_data.send_notification
            )

        post = await self.repository.update(
            post=post,
            update_data=update_data
        )

        if post.send_notification:
            await news_event_publisher.publish(
                routing_key="news.post.published",
                payload={
                    "post_id": post.id,
                    "post_type": post.post_type,
                    "title": post.title,
                    "summary": post.summary,
                    "slug": post.slug,
                    "category": post.category,
                    "cover_media_url": (
                        post.cover_media_url
                    ),
                    "cover_media_type": (
                        post.cover_media_type
                    ),
                    "created_by": post.created_by,
                    "published_by": (
                        post.published_by
                    ),
                    "published_at": (
                        post.published_at
                    )
                }
            )

        return post

    # =================================================
    # Снять с публикации
    # =================================================

    async def unpublish(
        self,
        post: Post,
        user_id: int
    ) -> Post:
        await external_validation_service.get_content_manager(
            user_id=user_id
        )
        if post.status != PostStatus.PUBLISHED:
            raise ValueError(
                "Публикация сейчас не опубликована"
            )

        return await self.repository.update(
            post=post,
            update_data={
                "status": PostStatus.DRAFT,
                "published_by": None,
                "published_at": None,
                "updated_by": user_id
            }
        )

    # =================================================
    # Закрепить
    # =================================================

    async def pin(
        self,
        post: Post,
        user_id: int
    ) -> Post:
        await external_validation_service.get_content_manager(
            user_id=user_id
        )
        if post.status != PostStatus.PUBLISHED:
            raise ValueError(
                "Закрепить можно только "
                "опубликованную публикацию"
            )

        if post.is_pinned:
            raise ValueError(
                "Публикация уже закреплена"
            )

        return await self.repository.update(
            post=post,
            update_data={
                "is_pinned": True,
                "updated_by": user_id
            }
        )

    # =================================================
    # Открепить
    # =================================================

    async def unpin(
        self,
        post: Post,
        user_id: int
    ) -> Post:
        await external_validation_service.get_content_manager(
            user_id=user_id
        )
        if not post.is_pinned:
            raise ValueError(
                "Публикация не закреплена"
            )

        return await self.repository.update(
            post=post,
            update_data={
                "is_pinned": False,
                "updated_by": user_id
            }
        )

    # =================================================
    # Архивировать
    # =================================================

    async def archive(
        self,
        post: Post,
        user_id: int
    ) -> Post:
        await external_validation_service.get_content_manager(
            user_id=user_id
        )
        if post.status == PostStatus.ARCHIVED:
            raise ValueError(
                "Публикация уже находится в архиве"
            )

        return await self.repository.update(
            post=post,
            update_data={
                "status": PostStatus.ARCHIVED,
                "is_pinned": False,
                "updated_by": user_id
            }
        )

    # =================================================
    # Восстановить из архива
    # =================================================

    async def restore(
        self,
        post: Post,
        user_id: int
    ) -> Post:
        await external_validation_service.get_content_manager(
            user_id=user_id
        )
        if post.status != PostStatus.ARCHIVED:
            raise ValueError(
                "Публикация не находится в архиве"
            )

        return await self.repository.update(
            post=post,
            update_data={
                "status": PostStatus.DRAFT,
                "updated_by": user_id
            }
        )

    # =================================================
    # Деактивировать
    # =================================================

    async def deactivate(
        self,
        post: Post,
        user_id: int
    ) -> Post:
        await external_validation_service.get_content_manager(
            user_id=user_id
        )
        if not post.is_active:
            raise ValueError(
                "Публикация уже неактивна"
            )

        return await self.repository.update(
            post=post,
            update_data={
                "is_active": False,
                "is_pinned": False,
                "updated_by": user_id
            }
        )

    # =================================================
    # Активировать
    # =================================================

    async def activate(
        self,
        post: Post,
        user_id: int
    ) -> Post:
        await external_validation_service.get_content_manager(
            user_id=user_id
        )
        if post.is_active:
            raise ValueError(
                "Публикация уже активна"
            )

        return await self.repository.update(
            post=post,
            update_data={
                "is_active": True,
                "updated_by": user_id
            }
        )

    # =================================================
    # Создание slug
    # =================================================

    def _generate_slug(
        self,
        title: str
    ) -> str:
        normalized_title = self._normalize_slug(
            title
        )

        if normalized_title:
            return normalized_title

        return f"post-{uuid4().hex[:12]}"

    def _normalize_slug(
        self,
        value: str
    ) -> str:
        value = value.strip().lower()

        replacements = {
            "а": "a",
            "б": "b",
            "в": "v",
            "г": "g",
            "д": "d",
            "е": "e",
            "ё": "e",
            "ж": "zh",
            "з": "z",
            "и": "i",
            "й": "y",
            "к": "k",
            "л": "l",
            "м": "m",
            "н": "n",
            "о": "o",
            "п": "p",
            "р": "r",
            "с": "s",
            "т": "t",
            "у": "u",
            "ф": "f",
            "х": "h",
            "ц": "c",
            "ч": "ch",
            "ш": "sh",
            "щ": "sch",
            "ъ": "",
            "ы": "y",
            "ь": "",
            "э": "e",
            "ю": "yu",
            "я": "ya"
        }

        for source, replacement in replacements.items():
            value = value.replace(
                source,
                replacement
            )

        value = re.sub(
            r"[^a-z0-9]+",
            "-",
            value
        )

        return value.strip("-")[:600]

    async def _make_slug_unique(
        self,
        slug: str
    ) -> str:
        base_slug = slug or "post"

        existing_post = await self.repository.get_by_slug(
            slug=base_slug
        )

        if existing_post is None:
            return base_slug

        for number in range(2, 10000):
            candidate = f"{base_slug}-{number}"

            existing_post = (
                await self.repository.get_by_slug(
                    slug=candidate
                )
            )

            if existing_post is None:
                return candidate

        return f"{base_slug}-{uuid4().hex[:12]}"