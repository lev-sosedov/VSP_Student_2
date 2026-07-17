from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_chat_member_role import (
    ChatMemberRole
)
from common.utils.enum_message_type import (
    MessageType
)
from communication_service.models.model_message import (
    Message
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
from communication_service.schemas.schemas_message import (
    MessageCreate,
    MessageUpdate
)
from communication_service.websocket.websocket_events import (
    build_message_event
)
from communication_service.websocket.websocket_manager import (
    websocket_manager
)
from communication_service.messaging.messaging_event_publisher import (
    communication_event_publisher
)


class MessageService:
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

    # =================================================
    # Получить сообщение
    # =================================================

    async def get_by_id(
        self,
        message_id: int,
        with_reply: bool = False
    ) -> Message | None:
        return await self.message_repository.get_by_id(
            message_id=message_id,
            with_reply=with_reply
        )

    # =================================================
    # Получить сообщения чата
    # =================================================

    async def get_chat_messages(
        self,
        chat_id: int,
        requested_by: int,
        include_deleted: bool = False,
        sender_id: int | None = None,
        is_pinned: bool | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[Message], int]:
        chat = await self.chat_repository.get_by_id(
            chat_id=chat_id
        )

        if chat is None:
            raise ValueError(
                "Чат не найден"
            )

        await self._get_active_member(
            chat_id=chat_id,
            user_id=requested_by
        )

        return await self.message_repository.get_chat_messages(
            chat_id=chat_id,
            include_deleted=include_deleted,
            sender_id=sender_id,
            is_pinned=is_pinned,
            skip=skip,
            limit=limit
        )

    # =================================================
    # Создать сообщение
    # =================================================

    async def create(
        self,
        message_data: MessageCreate
    ) -> Message:
        chat = await self.chat_repository.get_by_id(
            chat_id=message_data.chat_id
        )

        if chat is None:
            raise ValueError(
                "Чат не найден"
            )

        if not chat.is_active:
            raise ValueError(
                "Нельзя отправлять сообщения "
                "в неактивный чат"
            )

        if chat.is_archived:
            raise ValueError(
                "Нельзя отправлять сообщения "
                "в архивный чат"
            )

        sender = await self._get_active_member(
            chat_id=chat.id,
            user_id=message_data.sender_id
        )

        if sender.member_role == ChatMemberRole.READ_ONLY:
            raise ValueError(
                "Пользователь может только читать чат"
            )

        if message_data.reply_to_message_id is not None:
            reply_message = (
                await self.message_repository.get_by_id(
                    message_id=(
                        message_data.reply_to_message_id
                    )
                )
            )

            if reply_message is None:
                raise ValueError(
                    "Сообщение для ответа не найдено"
                )

            if reply_message.chat_id != chat.id:
                raise ValueError(
                    "Нельзя ответить на сообщение "
                    "из другого чата"
                )

            if reply_message.is_deleted:
                raise ValueError(
                    "Нельзя ответить на удалённое сообщение"
                )

        create_data = message_data.model_dump()

        message = await self.message_repository.create(
            message_data=create_data
        )

        await websocket_manager.broadcast_to_chat(
            chat_id=message.chat_id,
            event=build_message_event(
                event_type="message.created",
                message=message
            )
        )

        # Все активные и не замьюченные участники,
        # кроме отправителя.
        recipient_user_ids = (
            await self.member_repository
            .get_notification_user_ids(
                chat_id=message.chat_id,
                exclude_user_id=message.sender_id
            )
        )

        # Пользователям, которые сейчас находятся
        # в этом чате, отдельное уведомление не нужно.
        online_user_ids = (
            websocket_manager.get_online_user_ids(
                chat_id=message.chat_id
            )
        )

        notification_user_ids = [
            user_id
            for user_id in recipient_user_ids
            if user_id not in online_user_ids
        ]

        await communication_event_publisher.publish(
            routing_key="communication.message.created",
            payload={
                "message_id": message.id,
                "chat_id": message.chat_id,
                "sender_id": message.sender_id,
                "message_type": message.message_type,
                "text": message.text,
                "reply_to_message_id": (
                    message.reply_to_message_id
                ),
                "created_at": message.created_at,
                "recipient_user_ids": (
                    notification_user_ids
                )
            }
        )

        return message

    # =================================================
    # Изменить сообщение
    # =================================================

    async def update(
        self,
        message: Message,
        message_data: MessageUpdate
    ) -> Message:
        if message.is_deleted:
            raise ValueError(
                "Нельзя изменить удалённое сообщение"
            )

        await self._get_active_member(
            chat_id=message.chat_id,
            user_id=message_data.edited_by
        )

        if message.sender_id != message_data.edited_by:
            raise ValueError(
                "Изменить сообщение может "
                "только его автор"
            )

        if message.message_type == MessageType.SYSTEM:
            raise ValueError(
                "Системное сообщение нельзя изменить"
            )

        message = (
            await self.message_repository.update_text(
                message=message,
                text=message_data.text
            )
        )

        await websocket_manager.broadcast_to_chat(
            chat_id=message.chat_id,
            event=build_message_event(
                event_type="message.updated",
                message=message
            )
        )

        await communication_event_publisher.publish(
            routing_key="communication.message.updated",
            payload={
                "message_id": message.id,
                "chat_id": message.chat_id,
                "sender_id": message.sender_id,
                "text": message.text,
                "edited_at": message.edited_at
            }
        )

        return message

    # =================================================
    # Удалить сообщение
    # =================================================

    async def delete(
        self,
        message: Message,
        requested_by: int
    ) -> Message:
        if message.is_deleted:
            raise ValueError(
                "Сообщение уже удалено"
            )

        requester = await self._get_active_member(
            chat_id=message.chat_id,
            user_id=requested_by
        )

        can_delete = (
            message.sender_id == requested_by
            or requester.member_role in {
                ChatMemberRole.OWNER,
                ChatMemberRole.ADMIN
            }
        )

        if not can_delete:
            raise ValueError(
                "Недостаточно прав для удаления сообщения"
            )

        message = (
            await self.message_repository.soft_delete(
                message=message
            )
        )

        await websocket_manager.broadcast_to_chat(
            chat_id=message.chat_id,
            event=build_message_event(
                event_type="message.deleted",
                message=message
            )
        )

        await communication_event_publisher.publish(
            routing_key="communication.message.deleted",
            payload={
                "message_id": message.id,
                "chat_id": message.chat_id,
                "sender_id": message.sender_id,
                "deleted_at": message.deleted_at
            }
        )

        return message

    # =================================================
    # Закрепить сообщение
    # =================================================

    async def pin(
        self,
        message: Message,
        requested_by: int
    ) -> Message:
        if message.is_deleted:
            raise ValueError(
                "Нельзя закрепить удалённое сообщение"
            )

        requester = await self._get_active_member(
            chat_id=message.chat_id,
            user_id=requested_by
        )

        if requester.member_role not in {
            ChatMemberRole.OWNER,
            ChatMemberRole.ADMIN
        }:
            raise ValueError(
                "Закреплять сообщения могут "
                "владелец и администратор"
            )

        if message.is_pinned:
            raise ValueError(
                "Сообщение уже закреплено"
            )

        message = (
            await self.message_repository.set_pinned(
                message=message,
                is_pinned=True
            )
        )

        await websocket_manager.broadcast_to_chat(
            chat_id=message.chat_id,
            event=build_message_event(
                event_type="message.pinned",
                message=message
            )
        )

        return message

    # =================================================
    # Открепить сообщение
    # =================================================

    async def unpin(
        self,
        message: Message,
        requested_by: int
    ) -> Message:
        requester = await self._get_active_member(
            chat_id=message.chat_id,
            user_id=requested_by
        )

        if requester.member_role not in {
            ChatMemberRole.OWNER,
            ChatMemberRole.ADMIN
        }:
            raise ValueError(
                "Откреплять сообщения могут "
                "владелец и администратор"
            )

        if not message.is_pinned:
            raise ValueError(
                "Сообщение не закреплено"
            )

        message = (
            await self.message_repository.set_pinned(
                message=message,
                is_pinned=False
            )
        )

        await websocket_manager.broadcast_to_chat(
            chat_id=message.chat_id,
            event=build_message_event(
                event_type="message.unpinned",
                message=message
            )
        )

        return message

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