from datetime import datetime

from sqlalchemy import (
    func,
    select,
    update
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from common.utils.enum_notification_channel import (
    NotificationChannel
)
from common.utils.enum_notification_status import (
    NotificationStatus
)
from notification_service.models.model_notification import (
    Notification
)
from notification_service.models.model_notification_recipient import (
    NotificationRecipient
)


class NotificationRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить уведомление по ID
    # =================================================

    async def get_by_id(
        self,
        notification_id: int
    ) -> Notification | None:
        query = (
            select(Notification)
            .options(
                selectinload(
                    Notification.recipients
                )
            )
            .where(
                Notification.id == notification_id
            )
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Получить запись получателя
    # =================================================

    async def get_recipient(
        self,
        notification_id: int,
        user_id: int
    ) -> NotificationRecipient | None:
        query = select(
            NotificationRecipient
        ).where(
            NotificationRecipient.notification_id
            == notification_id,
            NotificationRecipient.user_id == user_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Создать уведомление
    # =================================================

    async def create_notification(
        self,
        notification_data: dict
    ) -> Notification:
        notification = Notification(
            **notification_data
        )

        self.session.add(notification)

        await self.session.flush()
        await self.session.refresh(notification)

        return notification

    # =================================================
    # Создать получателей
    # =================================================

    async def create_recipients(
        self,
        notification_id: int,
        user_ids: list[int],
        channel: NotificationChannel
    ) -> list[NotificationRecipient]:
        recipients = []

        now = datetime.utcnow()

        for user_id in user_ids:
            recipient = NotificationRecipient(
                notification_id=notification_id,
                user_id=user_id,
                channel=channel,
                status=NotificationStatus.DELIVERED,
                delivered_at=now
            )

            self.session.add(recipient)
            recipients.append(recipient)

        await self.session.flush()

        for recipient in recipients:
            await self.session.refresh(recipient)

        return recipients

    # =================================================
    # Список уведомлений пользователя
    # =================================================

    async def get_user_notifications(
        self,
        user_id: int,
        only_unread: bool | None = None,
        notification_type=None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[tuple], int]:
        filters = [
            NotificationRecipient.user_id == user_id
        ]

        if only_unread is True:
            filters.append(
                NotificationRecipient.read_at.is_(None)
            )

        if only_unread is False:
            filters.append(
                NotificationRecipient.read_at.is_not(None)
            )

        if notification_type is not None:
            filters.append(
                Notification.notification_type
                == notification_type
            )

        query = (
            select(
                Notification,
                NotificationRecipient
            )
            .join(
                NotificationRecipient,
                NotificationRecipient.notification_id
                == Notification.id
            )
            .where(*filters)
            .order_by(
                Notification.created_at.desc(),
                Notification.id.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(
                func.count(
                    NotificationRecipient.id
                )
            )
            .join(
                Notification,
                Notification.id
                == NotificationRecipient.notification_id
            )
            .where(*filters)
        )

        result = await self.session.execute(query)
        count_result = await self.session.execute(
            count_query
        )

        items = list(result.all())
        total = count_result.scalar_one()

        return items, total

    # =================================================
    # Счётчик непрочитанных
    # =================================================

    async def get_unread_count(
        self,
        user_id: int
    ) -> int:
        query = select(
            func.count(
                NotificationRecipient.id
            )
        ).where(
            NotificationRecipient.user_id == user_id,
            NotificationRecipient.read_at.is_(None)
        )

        result = await self.session.execute(query)

        return result.scalar_one()

    # =================================================
    # Отметить одно уведомление прочитанным
    # =================================================

    async def mark_as_read(
        self,
        recipient: NotificationRecipient
    ) -> NotificationRecipient:
        now = datetime.utcnow()

        recipient.read_at = now
        recipient.status = NotificationStatus.READ

        await self.session.flush()
        await self.session.refresh(recipient)

        return recipient

    # =================================================
    # Отметить все уведомления прочитанными
    # =================================================

    async def mark_all_as_read(
        self,
        user_id: int
    ) -> int:
        now = datetime.utcnow()

        query = (
            update(NotificationRecipient)
            .where(
                NotificationRecipient.user_id == user_id,
                NotificationRecipient.read_at.is_(None)
            )
            .values(
                read_at=now,
                status=NotificationStatus.READ,
                updated_at=now
            )
        )

        result = await self.session.execute(query)

        await self.session.flush()

        return result.rowcount or 0