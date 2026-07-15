from datetime import date, datetime, time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.utils.enum_lesson_status import LessonStatus
from common.utils.enum_lesson_type import LessonType
from schedule_service.db.db_base import Base


# =====================================================
# Конкретное занятие
# =====================================================

class LessonSchedule(Base):
    __tablename__ = "lesson_schedules"

    __table_args__ = (CheckConstraint("end_time > start_time", name="check_lesson_schedule_time"),)

    # Личный идентификатор занятия
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # ID группы из academic-service
    group_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # ID преподавателя из user-service
    teacher_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # ID кабинета
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False, index=True)

    # ID шаблона расписания.
    # Может отсутствовать у дополнительного занятия.
    template_id: Mapped[int | None] = mapped_column(ForeignKey("schedule_templates.id", ondelete="SET NULL"),
                                                    nullable=True, index=True)

    # Дата занятия
    lesson_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Время начала
    start_time: Mapped[time] = mapped_column(Time, nullable=False)

    # Время окончания
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    # Статус занятия
    status: Mapped[LessonStatus] = mapped_column(Enum(LessonStatus, name="lesson_status_enum"),
                                                 default=LessonStatus.SCHEDULED, nullable=False, index=True)

    # Тип занятия
    lesson_type: Mapped[LessonType] = mapped_column(Enum(LessonType, name="lesson_type_enum"),
                                                    default=LessonType.REGULAR, nullable=False)

    # Тема занятия
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Описание занятия
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Является ли занятие дополнительным
    is_extra: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ID пользователя, создавшего занятие
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    # Дата создания
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Дата последнего изменения
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                                                 nullable=False)

    # Связь с кабинетом
    room = relationship("Room", back_populates="lessons")

    # Связь с недельным шаблоном
    template = relationship("ScheduleTemplate", back_populates="lessons")

    # Связь с историей изменений конкретного занятия
    changes = relationship("ScheduleChange",back_populates="lesson",cascade="all, delete-orphan",passive_deletes=True,order_by="ScheduleChange.created_at")
