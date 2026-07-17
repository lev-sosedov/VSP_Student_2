from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.models.model_submission_attachment import (
    SubmissionAttachment
)


class SubmissionAttachmentRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить файл по ID
    # =================================================

    async def get_by_id(
        self,
        attachment_id: int
    ) -> SubmissionAttachment | None:
        query = select(SubmissionAttachment).where(
            SubmissionAttachment.id == attachment_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить список файлов
    # =================================================

    async def get_list(
        self,
        submission_id: int | None = None,
        uploaded_by: int | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[SubmissionAttachment], int]:
        filters = []

        if submission_id is not None:
            filters.append(
                SubmissionAttachment.submission_id
                == submission_id
            )

        if uploaded_by is not None:
            filters.append(
                SubmissionAttachment.uploaded_by
                == uploaded_by
            )

        attachments_query = (
            select(SubmissionAttachment)
            .where(*filters)
            .order_by(
                SubmissionAttachment.sort_order,
                SubmissionAttachment.created_at,
                SubmissionAttachment.id
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(
                func.count(SubmissionAttachment.id)
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
    # Создать файл
    # =================================================

    async def create(
        self,
        submission_id: int,
        title: str,
        attachment_type,
        file_url: str,
        file_name: str | None,
        mime_type: str | None,
        file_size: int | None,
        sort_order: int,
        uploaded_by: int
    ) -> SubmissionAttachment:
        attachment = SubmissionAttachment(
            submission_id=submission_id,
            title=title,
            attachment_type=attachment_type,
            file_url=file_url,
            file_name=file_name,
            mime_type=mime_type,
            file_size=file_size,
            sort_order=sort_order,
            uploaded_by=uploaded_by
        )

        self.session.add(attachment)

        await self.session.flush()
        await self.session.refresh(attachment)

        return attachment

    # =================================================
    # Изменить файл
    # =================================================

    async def update(
        self,
        attachment: SubmissionAttachment,
        update_data: dict
    ) -> SubmissionAttachment:
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
    # Удалить файл
    # =================================================

    async def delete(
        self,
        attachment_id: int
    ) -> None:
        query = delete(SubmissionAttachment).where(
            SubmissionAttachment.id == attachment_id
        )

        await self.session.execute(query)
        await self.session.flush()