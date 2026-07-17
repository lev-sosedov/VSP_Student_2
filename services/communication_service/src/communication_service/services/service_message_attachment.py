from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_chat_member_role import (
    ChatMemberRole
)
from communication_service.models.model_message_attachment import (
    MessageAttachment
)
from communication_service.repositories.repository_chat_member import (
    ChatMemberRepository
)
from communication_service.repositories.repository_message import (
    MessageRepository
)
from communication_service.repositories.repository_message_attachment import (
    MessageAttachmentRepository
)
from communication_service.schemas.schemas_message_attachment import (
    MessageAttachmentCreate
)
from communication_service.websocket.websocket_manager import (
    websocket_manager
)
from communication_service.messaging.messaging_event_publisher import (
    communication_event_publisher
)


class MessageAttachmentService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.message_repository = MessageRepository(
            session=session
        )

        self.member_repository = (
            ChatMemberRepository(
                session=session
            )
        )

        self.attachment_repository = (
            MessageAttachmentRepository(
                session=session
            )
        )

    # =================================================
    # Получить вложение
    # =================================================

    async def get_by_id(
        self,
        attachment_id: int,
        requested_by: int
    ) -> MessageAttachment | None:
        attachment = (
            await self.attachment_repository.get_by_id(
                attachment_id=attachment_id
            )
        )

        if attachment is None:
            return None

        message = await self.message_repository.get_by_id(
            message_id=attachment.message_id
        )

        if message is None:
            return None

        await self._get_active_member(
            chat_id=message.chat_id,
            user_id=requested_by
        )

        return attachment

    # =================================================
    # Получить вложение без проверки доступа
    # Используется внутри API перед удалением
    # =================================================

    async def get_raw_by_id(
        self,
        attachment_id: int
    ) -> MessageAttachment | None:
        return await self.attachment_repository.get_by_id(
            attachment_id=attachment_id
        )

    # =================================================
    # Получить список вложений сообщения
    # =================================================

    async def get_by_message(
        self,
        message_id: int,
        requested_by: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[MessageAttachment], int]:
        message = await self.message_repository.get_by_id(
            message_id=message_id
        )

        if message is None:
            raise ValueError(
                "Сообщение не найдено"
            )

        await self._get_active_member(
            chat_id=message.chat_id,
            user_id=requested_by
        )

        return await (
            self.attachment_repository.get_by_message(
                message_id=message_id,
                skip=skip,
                limit=limit
            )
        )

    # =================================================
    # Создать вложение
    # =================================================

    async def create(
        self,
        attachment_data: MessageAttachmentCreate
    ) -> MessageAttachment:
        message = await self.message_repository.get_by_id(
            message_id=attachment_data.message_id
        )

        if message is None:
            raise ValueError(
                "Сообщение не найдено"
            )

        if message.is_deleted:
            raise ValueError(
                "Нельзя добавить вложение "
                "к удалённому сообщению"
            )

        await self._get_active_member(
            chat_id=message.chat_id,
            user_id=attachment_data.uploaded_by
        )

        if message.sender_id != attachment_data.uploaded_by:
            raise ValueError(
                "Добавить вложение может "
                "только автор сообщения"
            )

        create_data = attachment_data.model_dump(
            exclude={
                "uploaded_by"
            }
        )

        attachment = (
            await self.attachment_repository.create(
                attachment_data=create_data
            )
        )

        await websocket_manager.broadcast_to_chat(
            chat_id=message.chat_id,
            event={
                "event": "message.attachment.created",
                "data": {
                    "id": attachment.id,
                    "message_id": attachment.message_id,
                    "attachment_type": (
                        attachment.attachment_type.value
                    ),
                    "file_url": attachment.file_url,
                    "file_name": attachment.file_name,
                    "mime_type": attachment.mime_type,
                    "file_size": attachment.file_size,
                    "created_at": (
                        attachment.created_at.isoformat()
                    )
                }
            }
        )

        await communication_event_publisher.publish(
            routing_key=(
                "communication.message.attachment.created"
            ),
            payload={
                "attachment_id": attachment.id,
                "message_id": attachment.message_id,
                "chat_id": message.chat_id,
                "uploaded_by": attachment_data.uploaded_by,
                "attachment_type": (
                    attachment.attachment_type
                ),
                "file_url": attachment.file_url,
                "file_name": attachment.file_name,
                "mime_type": attachment.mime_type,
                "file_size": attachment.file_size,
                "created_at": attachment.created_at
            }
        )

        return attachment

    # =================================================
    # Удалить вложение
    # =================================================

    async def delete(
        self,
        attachment: MessageAttachment,
        requested_by: int
    ) -> dict:
        message = await self.message_repository.get_by_id(
            message_id=attachment.message_id
        )

        if message is None:
            raise ValueError(
                "Сообщение не найдено"
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
                "Недостаточно прав для удаления вложения"
            )

        attachment_id = attachment.id
        message_id = attachment.message_id
        chat_id = message.chat_id

        await self.attachment_repository.delete(
            attachment=attachment
        )

        await websocket_manager.broadcast_to_chat(
            chat_id=chat_id,
            event={
                "event": "message.attachment.deleted",
                "data": {
                    "attachment_id": attachment_id,
                    "message_id": message_id
                }
            }
        )

        return {
            "attachment_id": attachment_id,
            "message_id": message_id,
            "deleted": True
        }

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

