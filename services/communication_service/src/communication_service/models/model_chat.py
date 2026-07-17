from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from common.utils.enum_chat_type import ChatType
from communication_service.db.db_base import Base


# =====================================================
# Чат
# =====================================================

class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    chat_type: Mapped[ChatType] = mapped_column(
        Enum(
            ChatType,
            name="chat_type_enum"
        ),
        nullable=False,
        index=True
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Для группового чата
    group_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )

    # Для чата конкретного занятия
    lesson_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )

    created_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    is_archived: Mapped[bool] = mapped_column(
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

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    members = relationship(
        "ChatMember",
        back_populates="chat",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        passive_deletes=True
    )