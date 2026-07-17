from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Integer,
    JSON,
    String,
    Text
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from common.utils.enum_notification_priority import (
    NotificationPriority
)
from common.utils.enum_notification_type import (
    NotificationType
)
from notification_service.db.db_base import Base


# =====================================================
# Уведомление
# =====================================================

class Notification(Base):
    __tablename__ = "notifications"

    # Внутренний ID уведомления
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # Тип уведомления
    notification_type: Mapped[
        NotificationType
    ] = mapped_column(
        Enum(
            NotificationType,
            name="notification_type_enum"
        ),
        nullable=False,
        index=True
    )

    # Приоритет
    priority: Mapped[
        NotificationPriority
    ] = mapped_column(
        Enum(
            NotificationPriority,
            name="notification_priority_enum"
        ),
        default=NotificationPriority.NORMAL,
        nullable=False,
        index=True
    )

    # Заголовок
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Основной текст
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Сервис, который создал событие
    #
    # Например:
    # content-service
    # schedule-service
    source_service: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    # Название исходного события
    #
    # Например:
    # content.homework.published
    event_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )

    # Тип связанной сущности
    #
    # homework, lesson, message, news
    source_entity_type: Mapped[str | None] = (
        mapped_column(
            String(100),
            nullable=True,
            index=True
        )
    )

    # ID связанной сущности
    source_entity_id: Mapped[int | None] = (
        mapped_column(
            Integer,
            nullable=True,
            index=True
        )
    )

    # Дополнительные данные события
    #
    # Например:
    # {
    #   "homework_id": 1,
    #   "lesson_id": 6,
    #   "group_id": 1
    # }
    payload: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    # Дата создания
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # После этой даты уведомление можно считать
    # устаревшим
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
    )

    # Получатели уведомления
    recipients = relationship(
        "NotificationRecipient",
        back_populates="notification",
        cascade="all, delete-orphan",
        passive_deletes=True
    )