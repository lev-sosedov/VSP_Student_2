from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.models.model_lesson_content import (
    LessonContent
)


class LessonContentRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить материал по ID
    # =================================================

    async def get_by_id(
        self,
        content_id: int
    ) -> LessonContent | None:
        query = select(LessonContent).where(
            LessonContent.id == content_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить материал по ID занятия
    # =================================================

    async def get_by_lesson_id(
        self,
        lesson_id: int
    ) -> LessonContent | None:
        query = select(LessonContent).where(
            LessonContent.lesson_id == lesson_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить список материалов
    # =================================================

    async def get_list(
        self,
        lesson_id: int | None = None,
        created_by: int | None = None,
        is_published: bool | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[LessonContent], int]:
        filters = []

        if lesson_id is not None:
            filters.append(
                LessonContent.lesson_id == lesson_id
            )

        if created_by is not None:
            filters.append(
                LessonContent.created_by == created_by
            )

        if is_published is not None:
            filters.append(
                LessonContent.is_published == is_published
            )

        contents_query = (
            select(LessonContent)
            .where(*filters)
            .order_by(
                LessonContent.created_at.desc(),
                LessonContent.id.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(func.count(LessonContent.id))
            .where(*filters)
        )

        contents_result = await self.session.execute(
            contents_query
        )

        count_result = await self.session.execute(
            count_query
        )

        contents = list(
            contents_result.scalars().all()
        )

        total = count_result.scalar_one()

        return contents, total

    # =================================================
    # Создать материал
    # =================================================

    async def create(
        self,
        lesson_id: int,
        title: str,
        summary: str | None,
        content: str | None,
        is_published: bool,
        created_by: int
    ) -> LessonContent:
        lesson_content = LessonContent(
            lesson_id=lesson_id,
            title=title,
            summary=summary,
            content=content,
            is_published=is_published,
            created_by=created_by
        )

        self.session.add(lesson_content)

        await self.session.flush()
        await self.session.refresh(lesson_content)

        return lesson_content

    # =================================================
    # Изменить материал
    # =================================================

    async def update(
        self,
        lesson_content: LessonContent,
        update_data: dict
    ) -> LessonContent:
        for field_name, field_value in update_data.items():
            setattr(
                lesson_content,
                field_name,
                field_value
            )

        await self.session.flush()
        await self.session.refresh(lesson_content)

        return lesson_content

    # =================================================
    # Изменить публикацию
    # =================================================

    async def set_publication(
        self,
        lesson_content: LessonContent,
        is_published: bool,
        updated_by: int
    ) -> LessonContent:
        lesson_content.is_published = is_published
        lesson_content.updated_by = updated_by

        await self.session.flush()
        await self.session.refresh(lesson_content)

        return lesson_content