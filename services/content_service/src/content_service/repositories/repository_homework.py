from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.models.model_homework import Homework


class HomeworkRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить домашнее задание по ID
    # =================================================

    async def get_by_id(
        self,
        homework_id: int
    ) -> Homework | None:
        query = select(Homework).where(
            Homework.id == homework_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить домашнее задание по занятию
    # =================================================

    async def get_by_lesson_id(
        self,
        lesson_id: int
    ) -> Homework | None:
        query = select(Homework).where(
            Homework.lesson_id == lesson_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить список домашних заданий
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
        filters = []

        if lesson_id is not None:
            filters.append(
                Homework.lesson_id == lesson_id
            )

        if created_by is not None:
            filters.append(
                Homework.created_by == created_by
            )

        if is_published is not None:
            filters.append(
                Homework.is_published == is_published
            )

        if is_active is not None:
            filters.append(
                Homework.is_active == is_active
            )

        homeworks_query = (
            select(Homework)
            .where(*filters)
            .order_by(
                Homework.due_at,
                Homework.created_at.desc(),
                Homework.id.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(func.count(Homework.id))
            .where(*filters)
        )

        homeworks_result = await self.session.execute(
            homeworks_query
        )

        count_result = await self.session.execute(
            count_query
        )

        homeworks = list(
            homeworks_result.scalars().all()
        )

        total = count_result.scalar_one()

        return homeworks, total

    # =================================================
    # Создать домашнее задание
    # =================================================

    async def create(
        self,
        lesson_id: int,
        title: str,
        description: str,
        instructions: str | None,
        max_score: int,
        due_at,
        allow_late_submission: bool,
        is_published: bool,
        created_by: int
    ) -> Homework:
        homework = Homework(
            lesson_id=lesson_id,
            title=title,
            description=description,
            instructions=instructions,
            max_score=max_score,
            due_at=due_at,
            allow_late_submission=allow_late_submission,
            is_published=is_published,
            is_active=True,
            created_by=created_by
        )

        self.session.add(homework)

        await self.session.flush()
        await self.session.refresh(homework)

        return homework

    # =================================================
    # Изменить домашнее задание
    # =================================================

    async def update(
        self,
        homework: Homework,
        update_data: dict
    ) -> Homework:
        for field_name, field_value in update_data.items():
            setattr(
                homework,
                field_name,
                field_value
            )

        await self.session.flush()
        await self.session.refresh(homework)

        return homework

    # =================================================
    # Изменить публикацию
    # =================================================

    async def set_publication(
        self,
        homework: Homework,
        is_published: bool,
        updated_by: int
    ) -> Homework:
        homework.is_published = is_published
        homework.updated_by = updated_by

        await self.session.flush()
        await self.session.refresh(homework)

        return homework

    # =================================================
    # Изменить активность
    # =================================================

    async def set_activity(
        self,
        homework: Homework,
        is_active: bool,
        updated_by: int
    ) -> Homework:
        homework.is_active = is_active
        homework.updated_by = updated_by

        if not is_active:
            homework.is_published = False

        await self.session.flush()
        await self.session.refresh(homework)

        return homework