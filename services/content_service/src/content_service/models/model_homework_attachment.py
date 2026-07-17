from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.utils.enum_attachment_type import AttachmentType
from content_service.db.db_base import Base


# =====================================================
# Вложение преподавателя к домашнему заданию
# =====================================================

class HomeworkAttachment(Base):
    __tablename__ = "homework_attachments"

    # Личный идентификатор вложения
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # ID домашнего задания внутри content-service
    homework_id: Mapped[int] = mapped_column(
        ForeignKey(
            "homeworks.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # Название вложения
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

    # URL файла в объектном хранилище
    file_url: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Исходное имя файла
    file_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # MIME-тип файла
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

    # Видно ли вложение студентам
    is_visible: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    # Кто загрузил файл
    #
    # Пользователь хранится в user-service,
    # поэтому ForeignKey не ставим.
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

    # Связь с домашним заданием
    homework = relationship(
        "Homework",
        back_populates="attachments"
    )