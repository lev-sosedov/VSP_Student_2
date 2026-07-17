from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from common.utils.enum_notification_channel import (
    NotificationChannel
)
from common.utils.enum_notification_status import (
    NotificationStatus
)
from notification_service.db.db_base import Base


# =====================================================
# Получатель уведомления
# =====================================================

class NotificationRecipient(Base):
    __tablename__ = "notification_recipients"

    __table_args__ = (
        UniqueConstraint(
            "notification_id",
            "user_id",
            "channel",
            name=(
                "uq_notification_recipient_"
                "notification_user_channel"
            )
        ),
    )

    # ID записи доставки
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # ID уведомления
    notification_id: Mapped[int] = mapped_column(
        ForeignKey(
            "notifications.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # ID пользователя из user-service
    #
    # ForeignKey не ставим:
    # пользователь находится в другой базе.
    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    # Канал доставки
    channel: Mapped[
        NotificationChannel
    ] = mapped_column(
        Enum(
            NotificationChannel,
            name="notification_channel_enum"
        ),
        default=NotificationChannel.IN_APP,
        nullable=False,
        index=True
    )

    # Статус доставки
    status: Mapped[
        NotificationStatus
    ] = mapped_column(
        Enum(
            NotificationStatus,
            name="notification_status_enum"
        ),
        default=NotificationStatus.PENDING,
        nullable=False,
        index=True
    )

    # Дата успешной доставки
    delivered_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime,
        nullable=True
    )

    # Дата прочтения
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
    )

    # Ошибка доставки
    error_message: Mapped[str | None] = (
        mapped_column(
            String(1000),
            nullable=True
        )
    )

    # Дата создания записи
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Дата последнего изменения
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Связь с уведомлением
    notification = relationship(
        "Notification",
        back_populates="recipients"
    )