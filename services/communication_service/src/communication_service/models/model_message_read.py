from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from communication_service.db.db_base import Base


# =====================================================
# Прочтение сообщения пользователем
# =====================================================

class MessageRead(Base):
    __tablename__ = "message_reads"

    __table_args__ = (
        UniqueConstraint(
            "message_id",
            "user_id",
            name="uq_message_read_message_user"
        ),
    )

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

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    read_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    message = relationship(
        "Message",
        back_populates="reads"
    )