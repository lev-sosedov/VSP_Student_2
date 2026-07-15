from datetime import datetime, time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Time,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.utils.enum_lesson_type import LessonType
from schedule_service.db.db_base import Base


# =====================================================
# Недельный шаблон расписания группы
# =====================================================

class ScheduleTemplate(Base):
    __tablename__ = "schedule_templates"

    __table_args__ = (
        CheckConstraint("weekday >= 0 AND weekday <= 6",name="check_schedule_template_weekday"),
        CheckConstraint("end_time > start_time",name="check_schedule_template_time"),
        UniqueConstraint("group_id","weekday","start_time",name="uq_schedule_template_group_weekday_time"),)

    # Личный идентификатор шаблона расписания
    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True)

    # ID группы из academic-service
    group_id: Mapped[int] = mapped_column(Integer,nullable=False,index=True)

    # ID преподавателя из user-service
    teacher_id: Mapped[int] = mapped_column(Integer,nullable=False,index=True)

    # ID кабинета из schedule-service
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="RESTRICT"),nullable=False,index=True)

    # День недели: 0 — понедельник, 6 — воскресенье
    weekday: Mapped[int] = mapped_column(Integer,nullable=False,index=True)

    # Время начала занятия
    start_time: Mapped[time] = mapped_column(Time,nullable=False)

    # Время окончания занятия
    end_time: Mapped[time] = mapped_column(Time,nullable=False)

    # Тип занятия
    lesson_type: Mapped[LessonType] = mapped_column(Enum(LessonType,name="lesson_type_enum"),default=LessonType.REGULAR,nullable=False)

    # Активен ли шаблон расписания
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False,index=True)

    # Дата создания шаблона
    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,nullable=False)

    # Дата последнего изменения
    updated_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # Связь с кабинетом
    room = relationship("Room",back_populates="schedule_templates")

    # Связь с конкретными занятиями
    lessons = relationship("LessonSchedule",back_populates="template")