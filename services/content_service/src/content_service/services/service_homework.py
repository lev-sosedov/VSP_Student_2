from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from content_service.models.model_homework import Homework
from content_service.repositories.repository_homework import (
    HomeworkRepository
)
from content_service.schemas.schemas_homework import (
    HomeworkCreate,
    HomeworkUpdate
)
from content_service.services.service_external_validation import (
    validate_content_author,
    validate_lesson
)
from content_service.messaging.messaging_event_publisher import (
    content_event_publisher
)


class HomeworkService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.repository = HomeworkRepository(
            session=session
        )

    # =================================================
    # Получить задание по ID
    # =================================================

    async def get_by_id(
        self,
        homework_id: int
    ) -> Homework | None:
        return await self.repository.get_by_id(
            homework_id=homework_id
        )

    # =================================================
    # Получить задание занятия
    # =================================================

    async def get_by_lesson_id(
        self,
        lesson_id: int
    ) -> Homework | None:
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
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[Homework], int]:
        return await self.repository.get_list(
            lesson_id=lesson_id,
            created_by=created_by,
            is_published=is_published,
            is_active=is_active,
            skip=skip,
            limit=limit
        )

    # =================================================
    # Создать домашнее задание
    # =================================================

    async def create(
        self,
        homework_data: HomeworkCreate
    ) -> Homework:
        lesson = await validate_lesson(
            lesson_id=homework_data.lesson_id
        )

        user = await validate_content_author(
            user_id=homework_data.created_by
        )

        if (
            user.get("role") in {"teacher", "TEACHER"}
            and lesson.get("teacher_id")
            != homework_data.created_by
        ):
            raise ValueError(
                "Преподаватель не назначен на это занятие"
            )

        existing_homework = (
            await self.repository.get_by_lesson_id(
                lesson_id=homework_data.lesson_id
            )
        )

        if existing_homework is not None:
            raise ValueError(
                "Для этого занятия домашнее задание "
                "уже создано"
            )

        self._validate_due_at(
            due_at=homework_data.due_at
        )

        homework = await self.repository.create(
            lesson_id=homework_data.lesson_id,
            title=homework_data.title,
            description=homework_data.description,
            instructions=homework_data.instructions,
            max_score=homework_data.max_score,
            due_at=homework_data.due_at,
            allow_late_submission=(
                homework_data.allow_late_submission
            ),
            is_published=homework_data.is_published,
            created_by=homework_data.created_by
        )

        await content_event_publisher.publish(
            routing_key="content.homework.created",
            payload={
                "homework_id": homework.id,
                "lesson_id": homework.lesson_id,
                "created_by": homework.created_by,
                "is_published": homework.is_published,
                "due_at": homework.due_at
            }
        )

        if homework.is_published:
            await content_event_publisher.publish(
                routing_key="content.homework.published",
                payload={
                    "homework_id": homework.id,
                    "lesson_id": homework.lesson_id,
                    "created_by": homework.created_by,
                    "due_at": homework.due_at
                }
            )

        return homework

    # =================================================
    # Изменить домашнее задание
    # =================================================

    async def update(
        self,
        homework: Homework,
        homework_data: HomeworkUpdate
    ) -> Homework:
        await self._validate_editor(
            homework=homework,
            user_id=homework_data.updated_by
        )

        if not homework.is_active:
            raise ValueError(
                "Нельзя изменить неактивное "
                "домашнее задание"
            )

        update_data = homework_data.model_dump(
            exclude_unset=True,
            exclude={
                "updated_by"
            }
        )

        if "due_at" in update_data:
            self._validate_due_at(
                due_at=update_data["due_at"]
            )

        update_data["updated_by"] = (
            homework_data.updated_by
        )

        return await self.repository.update(
            homework=homework,
            update_data=update_data
        )

    # =================================================
    # Опубликовать задание
    # =================================================

    async def publish(
        self,
        homework: Homework,
        updated_by: int
    ) -> Homework:
        await self._validate_editor(
            homework=homework,
            user_id=updated_by
        )

        if not homework.is_active:
            raise ValueError(
                "Нельзя опубликовать неактивное "
                "домашнее задание"
            )

        if homework.is_published:
            raise ValueError(
                "Домашнее задание уже опубликовано"
            )

        homework = await self.repository.set_publication(
            homework=homework,
            is_published=True,
            updated_by=updated_by
        )

        await content_event_publisher.publish(
            routing_key="content.homework.published",
            payload={
                "homework_id": homework.id,
                "lesson_id": homework.lesson_id,
                "updated_by": updated_by,
                "due_at": homework.due_at
            }
        )

        return homework

    # =================================================
    # Снять задание с публикации
    # =================================================

    async def unpublish(
        self,
        homework: Homework,
        updated_by: int
    ) -> Homework:
        await self._validate_editor(
            homework=homework,
            user_id=updated_by
        )

        if not homework.is_published:
            raise ValueError(
                "Домашнее задание уже снято "
                "с публикации"
            )

        homework = await self.repository.set_publication(
            homework=homework,
            is_published=False,
            updated_by=updated_by
        )

        await content_event_publisher.publish(
            routing_key="content.homework.unpublished",
            payload={
                "homework_id": homework.id,
                "lesson_id": homework.lesson_id,
                "updated_by": updated_by
            }
        )

        return homework

    # =================================================
    # Деактивировать задание
    # =================================================

    async def deactivate(
        self,
        homework: Homework,
        updated_by: int
    ) -> Homework:
        await self._validate_editor(
            homework=homework,
            user_id=updated_by
        )

        if not homework.is_active:
            raise ValueError(
                "Домашнее задание уже неактивно"
            )

        return await self.repository.set_activity(
            homework=homework,
            is_active=False,
            updated_by=updated_by
        )

    # =================================================
    # Активировать задание
    # =================================================

    async def activate(
        self,
        homework: Homework,
        updated_by: int
    ) -> Homework:
        await self._validate_editor(
            homework=homework,
            user_id=updated_by
        )

        if homework.is_active:
            raise ValueError(
                "Домашнее задание уже активно"
            )

        lesson = await validate_lesson(
            lesson_id=homework.lesson_id
        )

        if lesson.get("status") == "cancelled":
            raise ValueError(
                "Нельзя активировать задание "
                "для отменённого занятия"
            )

        return await self.repository.set_activity(
            homework=homework,
            is_active=True,
            updated_by=updated_by
        )

    # =================================================
    # Проверка пользователя
    # =================================================

    async def _validate_editor(
        self,
        homework: Homework,
        user_id: int
    ) -> None:
        user = await validate_content_author(
            user_id=user_id
        )

        if (
            user.get("role") in {"teacher", "TEACHER"}
            and homework.created_by != user_id
        ):
            raise ValueError(
                "Преподаватель не является автором "
                "этого домашнего задания"
            )

    # =================================================
    # Проверка крайнего срока
    # =================================================

    @staticmethod
    def _validate_due_at(
        due_at: datetime | None
    ) -> None:
        if due_at is None:
            return

        # PostgreSQL DateTime сейчас хранится без timezone.
        # Поэтому для сравнения приводим текущее время
        # к naive UTC.
        now = datetime.now(
            timezone.utc
        ).replace(
            tzinfo=None
        )

        comparable_due_at = due_at

        if due_at.tzinfo is not None:
            comparable_due_at = due_at.astimezone(
                timezone.utc
            ).replace(
                tzinfo=None
            )

        if comparable_due_at <= now:
            raise ValueError(
                "Крайний срок должен быть в будущем"
            )