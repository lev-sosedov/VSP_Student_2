from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from communication_service.models.model_message import (
    Message
)


class MessageRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить сообщение по ID
    # =================================================

    async def get_by_id(
        self,
        message_id: int,
        with_reply: bool = False
    ) -> Message | None:
        query = select(Message).where(
            Message.id == message_id
        )

        if with_reply:
            query = query.options(
                selectinload(
                    Message.reply_to
                )
            )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить список сообщений чата
    # =================================================

    async def get_chat_messages(
        self,
        chat_id: int,
        include_deleted: bool = False,
        sender_id: int | None = None,
        is_pinned: bool | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[Message], int]:
        filters = [
            Message.chat_id == chat_id
        ]

        if not include_deleted:
            filters.append(
                Message.is_deleted.is_(False)
            )

        if sender_id is not None:
            filters.append(
                Message.sender_id == sender_id
            )

        if is_pinned is not None:
            filters.append(
                Message.is_pinned == is_pinned
            )

        messages_query = (
            select(Message)
            .where(*filters)
            .order_by(
                Message.created_at.asc(),
                Message.id.asc()
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(func.count(Message.id))
            .where(*filters)
        )

        messages_result = await self.session.execute(
            messages_query
        )

        count_result = await self.session.execute(
            count_query
        )

        messages = list(
            messages_result.scalars().all()
        )

        total = count_result.scalar_one()

        return messages, total

    # =================================================
    # Создать сообщение
    # =================================================

    async def create(
        self,
        message_data: dict
    ) -> Message:
        message = Message(
            **message_data
        )

        self.session.add(message)

        await self.session.flush()
        await self.session.refresh(message)

        return message

    # =================================================
    # Изменить сообщение
    # =================================================

    async def update_text(
        self,
        message: Message,
        text: str
    ) -> Message:
        message.text = text
        message.is_edited = True
        message.edited_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(message)

        return message

    # =================================================
    # Мягкое удаление
    # =================================================

    async def soft_delete(
        self,
        message: Message
    ) -> Message:
        message.text = None
        message.is_deleted = True
        message.deleted_at = datetime.utcnow()
        message.is_pinned = False

        await self.session.flush()
        await self.session.refresh(message)

        return message

    # =================================================
    # Закрепить или открепить
    # =================================================

    async def set_pinned(
        self,
        message: Message,
        is_pinned: bool
    ) -> Message:
        message.is_pinned = is_pinned

        await self.session.flush()
        await self.session.refresh(message)

        return message