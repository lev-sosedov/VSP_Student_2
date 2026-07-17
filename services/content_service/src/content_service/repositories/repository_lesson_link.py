from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.models.model_lesson_link import (
    LessonLink
)


class LessonLinkRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить ссылку по ID
    # =================================================

    async def get_by_id(
        self,
        link_id: int
    ) -> LessonLink | None:
        query = select(LessonLink).where(
            LessonLink.id == link_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

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
        filters = []

        if lesson_content_id is not None:
            filters.append(
                LessonLink.lesson_content_id
                == lesson_content_id
            )

        if is_visible is not None:
            filters.append(
                LessonLink.is_visible == is_visible
            )

        if added_by is not None:
            filters.append(
                LessonLink.added_by == added_by
            )

        links_query = (
            select(LessonLink)
            .where(*filters)
            .order_by(
                LessonLink.sort_order,
                LessonLink.created_at,
                LessonLink.id
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(func.count(LessonLink.id))
            .where(*filters)
        )

        links_result = await self.session.execute(
            links_query
        )

        count_result = await self.session.execute(
            count_query
        )

        links = list(
            links_result.scalars().all()
        )

        total = count_result.scalar_one()

        return links, total

    # =================================================
    # Создать ссылку
    # =================================================

    async def create(
        self,
        lesson_content_id: int,
        title: str,
        url: str,
        description: str | None,
        sort_order: int,
        is_visible: bool,
        added_by: int
    ) -> LessonLink:
        lesson_link = LessonLink(
            lesson_content_id=lesson_content_id,
            title=title,
            url=url,
            description=description,
            sort_order=sort_order,
            is_visible=is_visible,
            added_by=added_by
        )

        self.session.add(lesson_link)

        await self.session.flush()
        await self.session.refresh(lesson_link)

        return lesson_link

    # =================================================
    # Изменить ссылку
    # =================================================

    async def update(
        self,
        lesson_link: LessonLink,
        update_data: dict
    ) -> LessonLink:
        for field_name, field_value in update_data.items():
            setattr(
                lesson_link,
                field_name,
                field_value
            )

        await self.session.flush()
        await self.session.refresh(lesson_link)

        return lesson_link

    # =================================================
    # Изменить видимость
    # =================================================

    async def set_visibility(
        self,
        lesson_link: LessonLink,
        is_visible: bool
    ) -> LessonLink:
        lesson_link.is_visible = is_visible

        await self.session.flush()
        await self.session.refresh(lesson_link)

        return lesson_link

    # =================================================
    # Удалить ссылку
    # =================================================

    async def delete(
        self,
        link_id: int
    ) -> None:
        query = delete(LessonLink).where(
            LessonLink.id == link_id
        )

        await self.session.execute(query)
        await self.session.flush()