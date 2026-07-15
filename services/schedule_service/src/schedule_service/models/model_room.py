from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schedule_service.db.db_base import Base


# =====================================================
# Кабинеты школы
# =====================================================

class Room(Base):
    __tablename__ = "rooms"

    # Личный идентификатор кабинета
    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True)

    # ID филиала из academic-service
    branch_id: Mapped[int] = mapped_column(Integer,nullable=False,index=True)

    # Название или номер кабинета
    name: Mapped[str] = mapped_column(String(100),nullable=False)

    # Вместимость кабинета
    capacity: Mapped[int | None] = mapped_column(Integer,nullable=True)

    # Дополнительное описание
    description: Mapped[str | None] = mapped_column(Text,nullable=True)

    # Активен ли кабинет
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False)

    # Дата создания
    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,nullable=False)

    # Дата последнего изменения
    updated_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

    # Недельные шаблоны, использующие кабинет
    schedule_templates = relationship("ScheduleTemplate",back_populates="room",passive_deletes=True)

    # Конкретные занятия в кабинете
    lessons = relationship("LessonSchedule",back_populates="room",passive_deletes=True)