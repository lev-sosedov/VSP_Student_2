from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.models.model_homework_attachment import (
    HomeworkAttachment
)


class HomeworkAttachmentRepository:
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
    ) -> HomeworkAttachment | None:
        query = select(HomeworkAttachment).where(
            HomeworkAttachment.id == attachment_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить список вложений
    # =================================================

    async def get_list(
        self,
        homework_id: int | None = None,
        is_visible: bool | None = None,
        uploaded_by: int | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[HomeworkAttachment], int]:
        filters = []

        if homework_id is not None:
            filters.append(
                HomeworkAttachment.homework_id
                == homework_id
            )

        if is_visible is not None:
            filters.append(
                HomeworkAttachment.is_visible
                == is_visible
            )

        if uploaded_by is not None:
            filters.append(
                HomeworkAttachment.uploaded_by
                == uploaded_by
            )

        attachments_query = (
            select(HomeworkAttachment)
            .where(*filters)
            .order_by(
                HomeworkAttachment.sort_order,
                HomeworkAttachment.created_at,
                HomeworkAttachment.id
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(
                func.count(HomeworkAttachment.id)
            )
            .where(*filters)
        )

        attachments_result = (
            await self.session.execute(
                attachments_query
            )
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
        homework_id: int,
        title: str,
        attachment_type,
        file_url: str,
        file_name: str | None,
        mime_type: str | None,
        file_size: int | None,
        sort_order: int,
        is_visible: bool,
        uploaded_by: int
    ) -> HomeworkAttachment:
        attachment = HomeworkAttachment(
            homework_id=homework_id,
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
        attachment: HomeworkAttachment,
        update_data: dict
    ) -> HomeworkAttachment:
        for field_name, field_value in (
            update_data.items()
        ):
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
        attachment: HomeworkAttachment,
        is_visible: bool
    ) -> HomeworkAttachment:
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
        query = delete(HomeworkAttachment).where(
            HomeworkAttachment.id == attachment_id
        )

        await self.session.execute(query)
        await self.session.flush()