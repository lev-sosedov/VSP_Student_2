from sqlalchemy.ext.asyncio import AsyncSession

from communication_service.models.model_message_read import (
    MessageRead
)
from communication_service.repositories.repository_chat import (
    ChatRepository
)
from communication_service.repositories.repository_chat_member import (
    ChatMemberRepository
)
from communication_service.repositories.repository_message import (
    MessageRepository
)
from communication_service.repositories.repository_message_read import (
    MessageReadRepository
)
from communication_service.websocket.websocket_events import (
    build_message_read_event
)
from communication_service.websocket.websocket_manager import (
    websocket_manager
)


class MessageReadService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.chat_repository = ChatRepository(
            session=session
        )

        self.member_repository = (
            ChatMemberRepository(
                session=session
            )
        )

        self.message_repository = MessageRepository(
            session=session
        )

        self.read_repository = MessageReadRepository(
            session=session
        )

    # =================================================
    # Прочитать одно сообщение
    # =================================================

    async def mark_as_read(
        self,
        message_id: int,
        user_id: int
    ) -> MessageRead:
        message = await self.message_repository.get_by_id(
            message_id=message_id
        )

        if message is None:
            raise ValueError(
                "Сообщение не найдено"
            )

        if message.is_deleted:
            raise ValueError(
                "Нельзя отметить удалённое сообщение"
            )

        member = await self._get_active_member(
            chat_id=message.chat_id,
            user_id=user_id
        )

        existing_read = await self.read_repository.get_read(
            message_id=message.id,
            user_id=user_id
        )

        if existing_read is not None:
            return existing_read

        message_read = await self.read_repository.create_read(
            message_id=message.id,
            user_id=user_id
        )

        current_last_read = (
            member.last_read_message_id or 0
        )

        if message.id > current_last_read:
            await self.read_repository.set_last_read_message(
                member=member,
                message_id=message.id
            )

        await websocket_manager.broadcast_to_chat(
            chat_id=message.chat_id,
            event=build_message_read_event(
                chat_id=message.chat_id,
                message_id=message.id,
                user_id=user_id,
                read_at=message_read.read_at
            ),
            exclude_user_id=user_id
        )

        return message_read


    # =================================================
    # Прочитать весь чат
    # =================================================

    async def mark_chat_as_read(
        self,
        chat_id: int,
        user_id: int
    ) -> tuple[int, int | None]:
        chat = await self.chat_repository.get_by_id(
            chat_id=chat_id
        )

        if chat is None:
            raise ValueError(
                "Чат не найден"
            )

        member = await self._get_active_member(
            chat_id=chat_id,
            user_id=user_id
        )

        unread_messages = (
            await self.read_repository.get_unread_messages(
                chat_id=chat_id,
                user_id=user_id
            )
        )

        created_count = (
            await self.read_repository.create_reads(
                messages=unread_messages,
                user_id=user_id
            )
        )

        last_message = (
            await self.read_repository.get_last_message(
                chat_id=chat_id
            )
        )

        last_message_id = (
            last_message.id
            if last_message is not None
            else None
        )

        await self.read_repository.set_last_read_message(
            member=member,
            message_id=last_message_id
        )

        return created_count, last_message_id

    # =================================================
    # Непрочитанные сообщения чата
    # =================================================

    async def get_chat_unread_count(
        self,
        chat_id: int,
        user_id: int
    ) -> int:
        chat = await self.chat_repository.get_by_id(
            chat_id=chat_id
        )

        if chat is None:
            raise ValueError(
                "Чат не найден"
            )

        await self._get_active_member(
            chat_id=chat_id,
            user_id=user_id
        )

        return await (
            self.read_repository.get_chat_unread_count(
                chat_id=chat_id,
                user_id=user_id
            )
        )

    # =================================================
    # Общий счётчик пользователя
    # =================================================

    async def get_user_unread_count(
        self,
        user_id: int
    ) -> int:
        return await (
            self.read_repository.get_user_unread_count(
                user_id=user_id
            )
        )

    # =================================================
    # Получить активного участника
    # =================================================

    async def _get_active_member(
        self,
        chat_id: int,
        user_id: int
    ):
        member = await self.member_repository.get_member(
            chat_id=chat_id,
            user_id=user_id
        )

        if member is None or not member.is_active:
            raise ValueError(
                "Пользователь не является "
                "активным участником чата"
            )

        return member