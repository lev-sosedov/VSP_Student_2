from datetime import datetime

from sqlalchemy import (
    func,
    select
)
from sqlalchemy.ext.asyncio import AsyncSession

from communication_service.models.model_chat_member import (
    ChatMember
)
from communication_service.models.model_message import (
    Message
)
from communication_service.models.model_message_read import (
    MessageRead
)


class MessageReadRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить запись прочтения
    # =================================================

    async def get_read(
        self,
        message_id: int,
        user_id: int
    ) -> MessageRead | None:
        query = select(MessageRead).where(
            MessageRead.message_id == message_id,
            MessageRead.user_id == user_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Создать запись прочтения
    # =================================================

    async def create_read(
        self,
        message_id: int,
        user_id: int
    ) -> MessageRead:
        message_read = MessageRead(
            message_id=message_id,
            user_id=user_id,
            read_at=datetime.utcnow()
        )

        self.session.add(message_read)

        await self.session.flush()
        await self.session.refresh(message_read)

        return message_read

    # =================================================
    # Последнее сообщение чата
    # =================================================

    async def get_last_message(
        self,
        chat_id: int
    ) -> Message | None:
        query = (
            select(Message)
            .where(
                Message.chat_id == chat_id,
                Message.is_deleted.is_(False)
            )
            .order_by(
                Message.id.desc()
            )
            .limit(1)
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Сообщения для массового прочтения
    # =================================================

    async def get_unread_messages(
        self,
        chat_id: int,
        user_id: int
    ) -> list[Message]:
        already_read_subquery = (
            select(MessageRead.message_id)
            .where(
                MessageRead.user_id == user_id
            )
        )

        query = (
            select(Message)
            .where(
                Message.chat_id == chat_id,
                Message.is_deleted.is_(False),
                Message.sender_id != user_id,
                Message.id.not_in(
                    already_read_subquery
                )
            )
            .order_by(Message.id)
        )

        result = await self.session.execute(query)

        return list(
            result.scalars().all()
        )

    # =================================================
    # Массово создать прочтения
    # =================================================

    async def create_reads(
        self,
        messages: list[Message],
        user_id: int
    ) -> int:
        now = datetime.utcnow()

        for message in messages:
            self.session.add(
                MessageRead(
                    message_id=message.id,
                    user_id=user_id,
                    read_at=now
                )
            )

        await self.session.flush()

        return len(messages)

    # =================================================
    # Обновить last_read_message_id
    # =================================================

    async def set_last_read_message(
        self,
        member: ChatMember,
        message_id: int | None
    ) -> ChatMember:
        member.last_read_message_id = message_id

        await self.session.flush()
        await self.session.refresh(member)

        return member

    # =================================================
    # Непрочитанные сообщения конкретного чата
    # =================================================

    async def get_chat_unread_count(
        self,
        chat_id: int,
        user_id: int
    ) -> int:
        read_subquery = (
            select(MessageRead.message_id)
            .where(
                MessageRead.user_id == user_id
            )
        )

        query = select(
            func.count(Message.id)
        ).where(
            Message.chat_id == chat_id,
            Message.is_deleted.is_(False),
            Message.sender_id != user_id,
            Message.id.not_in(
                read_subquery
            )
        )

        result = await self.session.execute(query)

        return result.scalar_one()

    # =================================================
    # Все непрочитанные сообщения пользователя
    # =================================================

    async def get_user_unread_count(
        self,
        user_id: int
    ) -> int:
        active_chat_ids_subquery = (
            select(ChatMember.chat_id)
            .where(
                ChatMember.user_id == user_id,
                ChatMember.is_active.is_(True)
            )
        )

        read_subquery = (
            select(MessageRead.message_id)
            .where(
                MessageRead.user_id == user_id
            )
        )

        query = select(
            func.count(Message.id)
        ).where(
            Message.chat_id.in_(
                active_chat_ids_subquery
            ),
            Message.is_deleted.is_(False),
            Message.sender_id != user_id,
            Message.id.not_in(
                read_subquery
            )
        )

        result = await self.session.execute(query)

        return result.scalar_one()