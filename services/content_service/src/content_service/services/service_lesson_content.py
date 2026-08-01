from datetime import date, datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from content_service.models.model_lesson_content import (
    LessonContent
)
from content_service.repositories.repository_lesson_content import (
    LessonContentRepository
)
from content_service.schemas.schemas_lesson_content import (
    LessonContentCreate,
    LessonContentUpdate
)
from content_service.services.service_external_validation import (
    get_lessons_by_ids,
    validate_content_author,
    validate_lesson
)


class LessonContentService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.repository = LessonContentRepository(
            session=session
        )

    # =================================================
    # Получить материал по ID
    # =================================================

    async def get_by_id(
        self,
        content_id: int
    ) -> LessonContent | None:
        return await self.repository.get_by_id(
            content_id=content_id
        )

    # =================================================
    # Получить материал занятия
    # =================================================

    async def get_by_lesson_id(
        self,
        lesson_id: int
    ) -> LessonContent | None:
        return await self.repository.get_by_lesson_id(
            lesson_id=lesson_id
        )

    # =================================================
    # Получить список
    # =================================================

    async def get_list(
        self,
        lesson_id: int | None = None,
        created_by: int | None = None,
        is_published: bool | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[LessonContent], int]:
        contents, total = await self.repository.get_list(
            lesson_id=lesson_id,
            created_by=created_by,
            is_published=is_published,
            skip=skip,
            limit=limit
        )

        # Этот фильтр применяется только к запросам
        # опубликованных материалов. Преподавательские
        # запросы черновиков и библиотеки не изменяются.

        if is_published is not True:
            return contents, total

        school_timezone = timezone(
            timedelta(hours=3)
        )

        today = datetime.now(
            school_timezone
        ).date()

        lessons = await get_lessons_by_ids(
            [
                lesson_content.lesson_id
                for lesson_content in contents
            ]
        )

        lessons_by_id = {
            int(lesson["id"]): lesson
            for lesson in lessons
            if lesson.get("id") is not None
        }

        available_contents = [
            lesson_content
            for lesson_content in contents
            if self._is_available_for_students(
                lesson=lessons_by_id.get(
                    lesson_content.lesson_id
                ),
                today=today
            )
        ]

        return available_contents, len(available_contents)

    # =================================================
    # Доступен ли материал студентам по дате занятия
    # =================================================

    @staticmethod
    def _is_available_for_students(
        lesson: dict | None,
        today: date
    ) -> bool:
        if lesson is None:
            return False

        if lesson.get("status") == "cancelled":
            return False

        lesson_date_value = lesson.get(
            "lesson_date"
        )

        if not lesson_date_value:
            return False

        try:
            lesson_date = date.fromisoformat(
                str(lesson_date_value)
            )

        except ValueError:
            return False

        return lesson_date <= today

    # =================================================
    # Создать материал
    # =================================================

    async def create(
        self,
        content_data: LessonContentCreate
    ) -> LessonContent:
        lesson = await validate_lesson(
            lesson_id=content_data.lesson_id
        )

        user = await validate_content_author(
            user_id=content_data.created_by
        )

        if (
            user.get("role") in {"teacher", "TEACHER"}
            and lesson.get("teacher_id") != content_data.created_by
        ):
            raise ValueError(
                "Преподаватель не назначен на это занятие"
            )

        existing_content = (
            await self.repository.get_by_lesson_id(
                lesson_id=content_data.lesson_id
            )
        )

        if existing_content is not None:
            raise ValueError(
                "Для этого занятия основной материал "
                "уже создан"
            )

        return await self.repository.create(
            lesson_id=content_data.lesson_id,
            title=content_data.title,
            summary=content_data.summary,
            content=content_data.content,
            is_published=content_data.is_published,
            created_by=content_data.created_by
        )

    # =================================================
    # Изменить материал
    # =================================================

    async def update(
        self,
        lesson_content: LessonContent,
        content_data: LessonContentUpdate
    ) -> LessonContent:
        update_data = content_data.model_dump(
            exclude_unset=True
        )

        updated_by = update_data.pop(
            "updated_by"
        )

        update_data["updated_by"] = updated_by

        return await self.repository.update(
            lesson_content=lesson_content,
            update_data=update_data
        )

    # =================================================
    # Опубликовать
    # =================================================

    async def publish(
        self,
        lesson_content: LessonContent,
        updated_by: int
    ) -> LessonContent:
        if lesson_content.is_published:
            raise ValueError(
                "Материал уже опубликован"
            )

        return await self.repository.set_publication(
            lesson_content=lesson_content,
            is_published=True,
            updated_by=updated_by
        )

    # =================================================
    # Снять с публикации
    # =================================================

    async def unpublish(
        self,
        lesson_content: LessonContent,
        updated_by: int
    ) -> LessonContent:
        if not lesson_content.is_published:
            raise ValueError(
                "Материал уже снят с публикации"
            )

        return await self.repository.set_publication(
            lesson_content=lesson_content,
            is_published=False,
            updated_by=updated_by
        )

    # =================================================
    # Удалить / открепить материал от занятия
    # =================================================

    async def delete(
        self,
        lesson_content: LessonContent,
        deleted_by: int
    ) -> None:
        await validate_content_author(
            user_id=deleted_by
        )

        await self.repository.delete(
            content_id=lesson_content.id
        )
