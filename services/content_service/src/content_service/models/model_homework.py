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

    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            name="uq_homeworks_lesson_id"
        ),
    )

    # Личный идентификатор домашнего задания
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # ID занятия из schedule-service
    #
    # ForeignKey не ставим, потому что занятие
    # находится в другом микросервисе и другой базе.
    lesson_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    # Название домашнего задания
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Полное описание задания
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Дополнительные инструкции
    instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Максимальное количество баллов
    #
    # Пока можно использовать 100.
    # Даже если на сайте не будет обычных оценок,
    # баллы пригодятся для расчёта процента выполнения.
    max_score: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False
    )

    # Крайний срок выполнения
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
    )

    # Можно ли сдавать задание после срока
    allow_late_submission: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Опубликовано ли задание для студентов
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    # Активно ли домашнее задание
    #
    # Вместо физического удаления лучше деактивировать.
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    # ID преподавателя или администратора,
    # создавшего домашнее задание.
    #
    # Пользователь находится в user-service,
    # поэтому ForeignKey не ставим.
    created_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    # ID пользователя, последним изменившего задание
    updated_by: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )

    # Дата создания
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

    # Работы студентов по этому домашнему заданию
    submissions = relationship(
        "HomeworkSubmission",
        back_populates="homework",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # Файлы, приложенные преподавателем к заданию
    attachments = relationship(
        "HomeworkAttachment",
        back_populates="homework",
        cascade="all, delete-orphan",
        passive_deletes=True
    )