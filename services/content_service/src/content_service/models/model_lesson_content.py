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
# Основной материал конкретного занятия
# =====================================================

class LessonContent(Base):
    __tablename__ = "lesson_contents"

    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            name="uq_lesson_contents_lesson_id"
        ),
    )

    # Личный идентификатор материала
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # ID занятия из schedule-service
    lesson_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
        index=True
    )

    # Заголовок материала
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Краткое описание занятия или материала
    summary: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    # Основной текст материала
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Опубликован ли материал для студентов
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    # ID пользователя, создавшего материал
    # Пользователь хранится в user-service,
    # поэтому ForeignKey здесь не ставим
    created_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    # ID пользователя, последним изменившего материал
    updated_by: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )

    # Дата создания материала
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

    # Прикреплённые файлы, изображения, видео и ссылки
    attachments = relationship(
        "LessonAttachment",
        back_populates="lesson_content",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    links = relationship(
        "LessonLink",
        back_populates="lesson_content",
        cascade="all, delete-orphan",
        passive_deletes=True
    )