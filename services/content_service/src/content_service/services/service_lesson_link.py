from sqlalchemy.ext.asyncio import AsyncSession

from content_service.models.model_lesson_link import (
    LessonLink
)
from content_service.repositories.repository_lesson_content import (
    LessonContentRepository
)
from content_service.repositories.repository_lesson_link import (
    LessonLinkRepository
)
from content_service.schemas.schemas_lesson_link import (
    LessonLinkCreate,
    LessonLinkUpdate
)
from content_service.services.service_external_validation import (
    validate_content_author
)


class LessonLinkService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.link_repository = LessonLinkRepository(
            session=session
        )

        self.content_repository = LessonContentRepository(
            session=session
        )

    # =================================================
    # Получить ссылку по ID
    # =================================================

    async def get_by_id(
        self,
        link_id: int
    ) -> LessonLink | None:
        return await self.link_repository.get_by_id(
            link_id=link_id
        )

    # =================================================
    # Получить список ссылок
    # =================================================

    async def get_list(
        self,
        lesson_content_id: int | None = None,
        is_visible: bool | None = None,
        added_by: int | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[LessonLink], int]:
        return await self.link_repository.get_list(
            lesson_content_id=lesson_content_id,
            is_visible=is_visible,
            added_by=added_by,
            skip=skip,
            limit=limit
        )

    # =================================================
    # Создать ссылку
    # =================================================

    async def create(
        self,
        link_data: LessonLinkCreate
    ) -> LessonLink:
        lesson_content = (
            await self.content_repository.get_by_id(
                content_id=link_data.lesson_content_id
            )
        )

        if lesson_content is None:
            raise ValueError(
                "Основной материал занятия не найден"
            )

        user = await validate_content_author(
            user_id=link_data.added_by
        )

        if (
            user.get("role") in {"teacher", "TEACHER"}
            and lesson_content.created_by
            != link_data.added_by
        ):
            raise ValueError(
                "Преподаватель не является автором "
                "этого материала занятия"
            )

        return await self.link_repository.create(
            lesson_content_id=link_data.lesson_content_id,
            title=link_data.title,
            url=str(link_data.url),
            description=link_data.description,
            sort_order=link_data.sort_order,
            is_visible=link_data.is_visible,
            added_by=link_data.added_by
        )

    # =================================================
    # Изменить ссылку
    # =================================================

    async def update(
        self,
        lesson_link: LessonLink,
        link_data: LessonLinkUpdate
    ) -> LessonLink:
        await self._validate_editor(
            lesson_link=lesson_link,
            user_id=link_data.updated_by
        )

        update_data = link_data.model_dump(
            exclude_unset=True,
            exclude={
                "updated_by"
            }
        )

        if "url" in update_data:
            update_data["url"] = str(
                update_data["url"]
            )

        return await self.link_repository.update(
            lesson_link=lesson_link,
            update_data=update_data
        )

    # =================================================
    # Показать ссылку
    # =================================================

    async def show(
        self,
        lesson_link: LessonLink,
        updated_by: int
    ) -> LessonLink:
        await self._validate_editor(
            lesson_link=lesson_link,
            user_id=updated_by
        )

        if lesson_link.is_visible:
            raise ValueError(
                "Ссылка уже отображается студентам"
            )

        return await self.link_repository.set_visibility(
            lesson_link=lesson_link,
            is_visible=True
        )

    # =================================================
    # Скрыть ссылку
    # =================================================

    async def hide(
        self,
        lesson_link: LessonLink,
        updated_by: int
    ) -> LessonLink:
        await self._validate_editor(
            lesson_link=lesson_link,
            user_id=updated_by
        )

        if not lesson_link.is_visible:
            raise ValueError(
                "Ссылка уже скрыта"
            )

        return await self.link_repository.set_visibility(
            lesson_link=lesson_link,
            is_visible=False
        )

    # =================================================
    # Удалить ссылку
    # =================================================

    async def delete(
        self,
        lesson_link: LessonLink,
        deleted_by: int
    ) -> None:
        await self._validate_editor(
            lesson_link=lesson_link,
            user_id=deleted_by
        )

        await self.link_repository.delete(
            link_id=lesson_link.id
        )

    # =================================================
    # Проверка пользователя
    # =================================================

    async def _validate_editor(
        self,
        lesson_link: LessonLink,
        user_id: int
    ) -> None:
        user = await validate_content_author(
            user_id=user_id
        )

        if (
            user.get("role") in {"teacher", "TEACHER"}
            and lesson_link.added_by != user_id
        ):
            raise ValueError(
                "Преподаватель не добавлял эту ссылку"
            )