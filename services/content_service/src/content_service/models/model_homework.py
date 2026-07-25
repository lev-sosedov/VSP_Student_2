from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from content_service.db.db_base import Base


# =====================================================
# Домашнее задание к конкретному занятию
# =====================================================

class Homework(Base):
    __tablename__ = "homeworks"

    __table_args__ = (UniqueConstraint("lesson_id", name="uq_homeworks_lesson_id"),)

    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    lesson_id: Mapped[int] = mapped_column(Integer,nullable=False,index=True) # ID занятия из schedule-service
    group_id: Mapped[int] = mapped_column(Integer,nullable=True, index=True) # ID группы из academic-service
    title: Mapped[str] = mapped_column(String(255),nullable=False) # Название домашнего задания
    description: Mapped[str] = mapped_column(Text, nullable=False) # Полное описание задания
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True) # Дополнительные инструкции
    max_score: Mapped[int] = mapped_column(Integer,default=100, nullable=False) # Максимальное количество баллов
    due_at: Mapped[datetime | None] = mapped_column(DateTime,nullable=True,index=True) # Крайний срок выполнения
    allow_late_submission: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False) # Можно ли сдавать задание после срока
    is_published: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False,index=True) # Опубликовано ли задание для студентов
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False,index=True) # Активно ли домашнее задание
    created_by: Mapped[int] = mapped_column(Integer,nullable=False,index=True) # ID преподавателя или администратора,
    updated_by: Mapped[int | None] = mapped_column(Integer,nullable=True,index=True) # ID пользователя, последним изменившего задание
    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,nullable=False) # Дата создания
    updated_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False) # Дата последнего изменения
    submissions = relationship("HomeworkSubmission",back_populates="homework",cascade="all, delete-orphan",passive_deletes=True) # Работы студентов по этому домашнему заданию
    attachments = relationship("HomeworkAttachment",back_populates="homework",cascade="all, delete-orphan",passive_deletes=True) # Файлы, приложенные преподавателем к заданию