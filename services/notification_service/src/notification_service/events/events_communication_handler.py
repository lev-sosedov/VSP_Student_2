from typing import Any

from common.utils.enum_notification_channel import (
    NotificationChannel
)
from common.utils.enum_notification_priority import (
    NotificationPriority
)
from common.utils.enum_notification_type import (
    NotificationType
)
from notification_service.schemas.schemas_notification import (
    NotificationCreate
)
from notification_service.services.service_notification import (
    NotificationService
)


class CommunicationEventHandler:
    # =================================================
    # Главный обработчик
    # =================================================

    async def handle(
        self,
        event_type: str,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        handlers = {
            "communication.message.created": (
                self.handle_message_created
            )
        }

        handler = handlers.get(event_type)

        if handler is None:
            return

        await handler(
            payload=payload,
            service=service
        )

    # =================================================
    # Новое сообщение
    # =================================================

    async def handle_message_created(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        message_id = payload.get("message_id")
        chat_id = payload.get("chat_id")
        sender_id = payload.get("sender_id")

        recipient_user_ids = payload.get(
            "recipient_user_ids",
            []
        )

        if (
            message_id is None
            or chat_id is None
            or sender_id is None
        ):
            raise ValueError(
                "message_id, chat_id и sender_id обязательны"
            )

        user_ids = []

        for user_id in recipient_user_ids:
            try:
                parsed_user_id = int(user_id)

            except (TypeError, ValueError):
                continue

            if (
                parsed_user_id > 0
                and parsed_user_id != int(sender_id)
                and parsed_user_id not in user_ids
            ):
                user_ids.append(parsed_user_id)

        # Все участники сейчас онлайн либо
        # получателей у сообщения нет.
        if not user_ids:
            print(
                f"[Notification] Message {message_id}: "
                f"no offline recipients",
                flush=True
            )
            return

        text = payload.get("text")
        message_type = str(
            payload.get(
                "message_type",
                "text"
            )
        )

        if text:
            preview = str(text).strip()

            if len(preview) > 150:
                preview = preview[:147] + "..."

        elif message_type == "image":
            preview = "Отправлено изображение"

        elif message_type == "video":
            preview = "Отправлено видео"

        elif message_type == "audio":
            preview = "Отправлено аудиосообщение"

        elif message_type == "file":
            preview = "Отправлен файл"

        else:
            preview = "Новое сообщение"

        notification_data = NotificationCreate(
            notification_type=NotificationType.MESSAGE,
            priority=NotificationPriority.NORMAL,
            title="Новое сообщение",
            message=preview,
            source_service="communication-service",
            event_type="communication.message.created",
            source_entity_type="message",
            source_entity_id=int(message_id),
            payload={
                **payload,
                "chat_id": int(chat_id),
                "sender_id": int(sender_id)
            },
            user_ids=user_ids,
            channel=NotificationChannel.IN_APP
        )

        await service.create(
            notification_data=notification_data
        )


communication_event_handler = CommunicationEventHandler()