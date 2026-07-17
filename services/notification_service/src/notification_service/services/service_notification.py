from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_notification_type import (
    NotificationType
)
from notification_service.models.model_notification import (
    Notification
)
from notification_service.models.model_notification_recipient import (
    NotificationRecipient
)
from notification_service.repositories.repository_notification import (
    NotificationRepository
)
from notification_service.repositories.repository_notification_preference import (
    NotificationPreferenceRepository
)
from notification_service.schemas.schemas_notification import (
    NotificationCreate
)


class NotificationService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.repository = NotificationRepository(
            session=session
        )

        self.preference_repository = (
            NotificationPreferenceRepository(
                session=session
            )
        )

    # =================================================
    # Получить уведомление
    # =================================================

    async def get_by_id(
        self,
        notification_id: int
    ) -> Notification | None:
        return await self.repository.get_by_id(
            notification_id=notification_id
        )

    # =================================================
    # Создать уведомление
    # =================================================

    async def create(
        self,
        notification_data: NotificationCreate
    ) -> tuple[
        Notification,
        list[NotificationRecipient]
    ]:
        if (
            notification_data.expires_at is not None
            and notification_data.expires_at
            <= datetime.utcnow()
        ):
            raise ValueError(
                "Дата истечения уведомления "
                "должна быть в будущем"
            )

        allowed_user_ids = []

        for user_id in notification_data.user_ids:
            preference = (
                await self.preference_repository
                .get_by_user_id(
                    user_id=user_id
                )
            )

            if preference is None:
                allowed_user_ids.append(user_id)
                continue

            if not preference.in_app_enabled:
                continue

            if not self._category_enabled(
                preference=preference,
                notification_type=(
                    notification_data.notification_type
                )
            ):
                continue

            allowed_user_ids.append(user_id)

        if not allowed_user_ids:
            raise ValueError(
                "У всех получателей отключены "
                "уведомления этой категории"
            )

        create_data = notification_data.model_dump(
            exclude={
                "user_ids",
                "channel"
            }
        )

        notification = (
            await self.repository.create_notification(
                notification_data=create_data
            )
        )

        recipients = (
            await self.repository.create_recipients(
                notification_id=notification.id,
                user_ids=allowed_user_ids,
                channel=notification_data.channel
            )
        )

        return notification, recipients

    # =================================================
    # Получить список пользователя
    # =================================================

    async def get_user_notifications(
        self,
        user_id: int,
        only_unread: bool | None = None,
        notification_type: (
            NotificationType | None
        ) = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[dict], int, int]:
        rows, total = (
            await self.repository.get_user_notifications(
                user_id=user_id,
                only_unread=only_unread,
                notification_type=notification_type,
                skip=skip,
                limit=limit
            )
        )

        unread_count = (
            await self.repository.get_unread_count(
                user_id=user_id
            )
        )

        items = []

        for notification, recipient in rows:
            items.append(
                {
                    "notification_id": notification.id,
                    "recipient_id": recipient.id,

                    "notification_type": (
                        notification.notification_type
                    ),
                    "priority": notification.priority,

                    "title": notification.title,
                    "message": notification.message,

                    "source_service": (
                        notification.source_service
                    ),
                    "event_type": notification.event_type,

                    "source_entity_type": (
                        notification.source_entity_type
                    ),
                    "source_entity_id": (
                        notification.source_entity_id
                    ),

                    "payload": notification.payload,

                    "channel": recipient.channel,
                    "status": recipient.status,

                    "is_read": (
                        recipient.read_at is not None
                    ),
                    "delivered_at": (
                        recipient.delivered_at
                    ),
                    "read_at": recipient.read_at,

                    "created_at": (
                        notification.created_at
                    ),
                    "expires_at": (
                        notification.expires_at
                    )
                }
            )

        return items, total, unread_count

    # =================================================
    # Получить уведомление пользователя
    # =================================================

    async def get_user_notification(
        self,
        notification_id: int,
        user_id: int
    ) -> dict | None:
        notification = await self.repository.get_by_id(
            notification_id=notification_id
        )

        if notification is None:
            return None

        recipient = await self.repository.get_recipient(
            notification_id=notification_id,
            user_id=user_id
        )

        if recipient is None:
            return None

        return {
            "notification_id": notification.id,
            "recipient_id": recipient.id,

            "notification_type": (
                notification.notification_type
            ),
            "priority": notification.priority,

            "title": notification.title,
            "message": notification.message,

            "source_service": notification.source_service,
            "event_type": notification.event_type,

            "source_entity_type": (
                notification.source_entity_type
            ),
            "source_entity_id": (
                notification.source_entity_id
            ),

            "payload": notification.payload,

            "channel": recipient.channel,
            "status": recipient.status,

            "is_read": recipient.read_at is not None,
            "delivered_at": recipient.delivered_at,
            "read_at": recipient.read_at,

            "created_at": notification.created_at,
            "expires_at": notification.expires_at
        }

    # =================================================
    # Счётчик непрочитанных
    # =================================================

    async def get_unread_count(
        self,
        user_id: int
    ) -> int:
        return await self.repository.get_unread_count(
            user_id=user_id
        )

    # =================================================
    # Прочитать одно уведомление
    # =================================================

    async def mark_as_read(
        self,
        notification_id: int,
        user_id: int
    ) -> NotificationRecipient:
        recipient = await self.repository.get_recipient(
            notification_id=notification_id,
            user_id=user_id
        )

        if recipient is None:
            raise ValueError(
                "Уведомление пользователя не найдено"
            )

        if recipient.read_at is not None:
            return recipient

        return await self.repository.mark_as_read(
            recipient=recipient
        )

    # =================================================
    # Прочитать все уведомления
    # =================================================

    async def mark_all_as_read(
        self,
        user_id: int
    ) -> int:
        return await self.repository.mark_all_as_read(
            user_id=user_id
        )

    # =================================================
    # Проверка категории настроек
    # =================================================

    @staticmethod
    def _category_enabled(
        preference,
        notification_type: NotificationType
    ) -> bool:
        mapping = {
            NotificationType.SCHEDULE: (
                preference.schedule_enabled
            ),
            NotificationType.LESSON: (
                preference.lesson_enabled
            ),
            NotificationType.HOMEWORK: (
                preference.homework_enabled
            ),
            NotificationType.HOMEWORK_RESULT: (
                preference.homework_result_enabled
            ),
            NotificationType.CHAT: (
                preference.chat_enabled
            ),
            NotificationType.NEWS: (
                preference.news_enabled
            )
        }

        return mapping.get(
            notification_type,
            True
        )