from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.models.model_lesson_attachment import (
    LessonAttachment
)


class LessonAttachmentRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить вложение по ID
    # =================================================

    async def get_by_id(
        self,
        attachment_id: int
    ) -> LessonAttachment | None:
        query = select(LessonAttachment).where(
            LessonAttachment.id == attachment_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить список вложений
    # =================================================

    async def get_list(
        self,
        lesson_content_id: int | None = None,
        is_visible: bool | None = None,
        uploaded_by: int | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[LessonAttachment], int]:
        filters = []

        if lesson_content_id is not None:
            filters.append(
                LessonAttachment.lesson_content_id
                == lesson_content_id
            )

        if is_visible is not None:
            filters.append(
                LessonAttachment.is_visible
                == is_visible
            )

        if uploaded_by is not None:
            filters.append(
                LessonAttachment.uploaded_by
                == uploaded_by
            )

        attachments_query = (
            select(LessonAttachment)
            .where(*filters)
            .order_by(
                LessonAttachment.sort_order,
                LessonAttachment.created_at,
                LessonAttachment.id
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(func.count(LessonAttachment.id))
            .where(*filters)
        )

        attachments_result = await self.session.execute(
            attachments_query
        )

        count_result = await self.session.execute(
            count_query
        )

        attachments = list(
            attachments_result.scalars().all()
        )

        total = count_result.scalar_one()

        return attachments, total

    # =================================================
    # Создать вложение
    # =================================================

    async def create(
        self,
        lesson_content_id: int,
        title: str,
        attachment_type,
        file_url: str,
        file_name: str | None,
        mime_type: str | None,
        file_size: int | None,
        sort_order: int,
        is_visible: bool,
        uploaded_by: int
    ) -> LessonAttachment:
        attachment = LessonAttachment(
            lesson_content_id=lesson_content_id,
            title=title,
            attachment_type=attachment_type,
            file_url=file_url,
            file_name=file_name,
            mime_type=mime_type,
            file_size=file_size,
            sort_order=sort_order,
            is_visible=is_visible,
            uploaded_by=uploaded_by
        )

        self.session.add(attachment)

        await self.session.flush()
        await self.session.refresh(attachment)

        return attachment

    # =================================================
    # Изменить вложение
    # =================================================

    async def update(
        self,
        attachment: LessonAttachment,
        update_data: dict
    ) -> LessonAttachment:
        for field_name, field_value in update_data.items():
            setattr(
                attachment,
                field_name,
                field_value
            )

        await self.session.flush()
        await self.session.refresh(attachment)

        return attachment

    # =================================================
    # Изменить видимость
    # =================================================

    async def set_visibility(
        self,
        attachment: LessonAttachment,
        is_visible: bool
    ) -> LessonAttachment:
        attachment.is_visible = is_visible

        await self.session.flush()
        await self.session.refresh(attachment)

        return attachment

    # =================================================
    # Удалить вложение
    # =================================================

    async def delete(
        self,
        attachment_id: int
    ) -> None:
        query = delete(LessonAttachment).where(
            LessonAttachment.id == attachment_id
        )

        await self.session.execute(query)
        await self.session.flush()