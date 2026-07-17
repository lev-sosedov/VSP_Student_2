from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Enum
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from content_service.db.db_base import Base

from common.utils.enum_attachment_type import AttachmentType


# =====================================================
# Вложения к материалу занятия
# =====================================================

class LessonAttachment(Base):
    __tablename__ = "lesson_attachments"

    # Личный идентификатор вложения
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # Материал занятия
    lesson_content_id: Mapped[int] = mapped_column(
        ForeignKey(
            "lesson_contents.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # Название файла
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Тип вложения
    attachment_type: Mapped[AttachmentType] = mapped_column(
        Enum(
            AttachmentType,
            name="attachment_type_enum"
        ),
        nullable=False,
        index=True
    )

    # URL файла
    file_url: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Имя файла
    file_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # MIME тип
    mime_type: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    # Размер файла в байтах
    file_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    # Порядок отображения
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    # Видимость студентам
    is_visible: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    # Кто загрузил
    uploaded_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    # Дата загрузки
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    lesson_content = relationship(
        "LessonContent",
        back_populates="attachments"
    )