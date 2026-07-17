from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from common.utils.enum_chat_member_role import (
    ChatMemberRole
)
from communication_service.db.db_base import Base


# =====================================================
# Участник чата
# =====================================================

class ChatMember(Base):
    __tablename__ = "chat_members"

    __table_args__ = (
        UniqueConstraint(
            "chat_id",
            "user_id",
            name="uq_chat_member_chat_user"
        ),
    )

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

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    member_role: Mapped[
        ChatMemberRole
    ] = mapped_column(
        Enum(
            ChatMemberRole,
            name="chat_member_role_enum"
        ),
        default=ChatMemberRole.MEMBER,
        nullable=False,
        index=True
    )

    added_by: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    left_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    is_muted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    last_read_message_id: Mapped[int | None] = (
        mapped_column(
            Integer,
            nullable=True
        )
    )

    chat = relationship(
        "Chat",
        back_populates="members"
    )