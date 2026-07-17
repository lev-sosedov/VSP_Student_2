from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from content_service.db.db_base import Base


# =====================================================
# Полезная ссылка к материалу занятия
# =====================================================

class LessonLink(Base):
    __tablename__ = "lesson_links"

    # Личный идентификатор ссылки
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # ID основного материала занятия
    lesson_content_id: Mapped[int] = mapped_column(
        ForeignKey(
            "lesson_contents.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # Название ссылки
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # URL
    url: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Необязательное описание
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Порядок отображения
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    # Видна ли ссылка студентам
    is_visible: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    # ID пользователя, добавившего ссылку
    added_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    # Дата добавления
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Дата изменения
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Связь с основным материалом занятия
    lesson_content = relationship(
        "LessonContent",
        back_populates="links"
    )