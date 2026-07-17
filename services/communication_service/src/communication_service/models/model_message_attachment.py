from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from common.utils.enum_message_attachment_type import (
    MessageAttachmentType
)
from communication_service.db.db_base import Base


# =====================================================
# Вложение сообщения
# =====================================================

class MessageAttachment(Base):
    __tablename__ = "message_attachments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    message_id: Mapped[int] = mapped_column(
        ForeignKey(
            "messages.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    attachment_type: Mapped[
        MessageAttachmentType
    ] = mapped_column(
        Enum(
            MessageAttachmentType,
            name="message_attachment_type_enum"
        ),
        nullable=False,
        index=True
    )

    file_url: Mapped[str] = mapped_column(
        String(3000),
        nullable=False
    )

    file_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    file_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    message = relationship(
        "Message",
        back_populates="attachments"
    )