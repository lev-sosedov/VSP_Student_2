from datetime import datetime, time

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Time,
    UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from notification_service.db.db_base import Base


# =====================================================
# Настройки уведомлений пользователя
# =====================================================

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            name="uq_notification_preference_user"
        ),
    )

    # ID настройки
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # ID пользователя из user-service
    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
        index=True
    )

    # Каналы доставки
    in_app_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    email_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    push_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    telegram_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Категории
    schedule_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    lesson_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    homework_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    homework_result_enabled: Mapped[bool] = (
        mapped_column(
            Boolean,
            default=True,
            nullable=False
        )
    )

    chat_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    news_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Тихие часы
    quiet_hours_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    quiet_hours_start: Mapped[
        time | None
    ] = mapped_column(
        Time,
        nullable=True
    )

    quiet_hours_end: Mapped[
        time | None
    ] = mapped_column(
        Time,
        nullable=True
    )

    # Часовой пояс пользователя
    timezone: Mapped[str] = mapped_column(
        String(100),
        default="Europe/Moscow",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )