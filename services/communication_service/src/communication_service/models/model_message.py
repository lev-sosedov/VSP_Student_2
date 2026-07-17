from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from common.utils.enum_message_type import (
    MessageType
)
from communication_service.db.db_base import Base


# =====================================================
# Сообщение
# =====================================================

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    chat_id: Mapped[int] = mapped_column(
        ForeignKey(
            "chats.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    sender_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    message_type: Mapped[
        MessageType
    ] = mapped_column(
        Enum(
            MessageType,
            name="message_type_enum"
        ),
        default=MessageType.TEXT,
        nullable=False,
        index=True
    )

    text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    reply_to_message_id: Mapped[
        int | None
    ] = mapped_column(
        ForeignKey(
            "messages.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    is_edited: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    edited_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    chat = relationship(
        "Chat",
        back_populates="messages"
    )

    attachments = relationship(
        "MessageAttachment",
        back_populates="message",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    reads = relationship(
        "MessageRead",
        back_populates="message",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    reply_to = relationship(
        "Message",
        remote_side=[id],
        foreign_keys=[reply_to_message_id]
    )