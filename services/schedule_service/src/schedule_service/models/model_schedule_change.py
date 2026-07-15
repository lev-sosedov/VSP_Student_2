from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.utils.enum_schedule_change_type import ScheduleChangeType
from schedule_service.db.db_base import Base


# =====================================================
# История изменений конкретного занятия
# =====================================================

class ScheduleChange(Base):
    __tablename__ = "schedule_changes"

    # Личный идентификатор записи об изменении
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # ID изменённого занятия
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey(
            "lesson_schedules.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # Тип изменения:
    # rescheduled — перенос занятия
    # cancelled — отмена занятия
    # teacher_changed — замена преподавателя
    # room_changed — замена кабинета
    # updated — обычное изменение данных
    # restored — восстановление занятия
    change_type: Mapped[ScheduleChangeType] = mapped_column(
        Enum(
            ScheduleChangeType,
            name="schedule_change_type_enum"
        ),
        nullable=False,
        index=True
    )

    # Данные занятия до изменения
    old_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    # Данные занятия после изменения
    new_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    # Причина изменения
    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # ID пользователя, который внёс изменение
    changed_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    # Дополнительный комментарий администратора
    comment: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    # Дата и время изменения
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Связь с конкретным занятием
    lesson = relationship(
        "LessonSchedule",
        back_populates="changes"
    )