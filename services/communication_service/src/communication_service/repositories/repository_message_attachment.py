from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from communication_service.models.model_message_attachment import (
    MessageAttachment
)


class MessageAttachmentRepository:
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
    ) -> MessageAttachment | None:
        query = select(
            MessageAttachment
        ).where(
            MessageAttachment.id == attachment_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить вложения сообщения
    # =================================================

    async def get_by_message(
        self,
        message_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[MessageAttachment], int]:
        query = (
            select(MessageAttachment)
            .where(
                MessageAttachment.message_id
                == message_id
            )
            .order_by(
                MessageAttachment.created_at,
                MessageAttachment.id
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = select(
            func.count(
                MessageAttachment.id
            )
        ).where(
            MessageAttachment.message_id
            == message_id
        )

        result = await self.session.execute(query)

        count_result = await self.session.execute(
            count_query
        )

        attachments = list(
            result.scalars().all()
        )

        total = count_result.scalar_one()

        return attachments, total

    # =================================================
    # Создать вложение
    # =================================================

    async def create(
        self,
        attachment_data: dict
    ) -> MessageAttachment:
        attachment = MessageAttachment(
            **attachment_data
        )

        self.session.add(attachment)

        await self.session.flush()
        await self.session.refresh(attachment)

        return attachment

    # =================================================
    # Удалить вложение
    # =================================================

    async def delete(
        self,
        attachment: MessageAttachment
    ) -> None:
        await self.session.delete(attachment)
        await self.session.flush()