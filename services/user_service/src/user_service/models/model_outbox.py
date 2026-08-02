from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from user_service.db.db_base import Base


class UserEventOutbox(Base):
    """Transactional event record; a publisher may safely retry by event_id."""
    __tablename__ = "user_event_outbox"
    __table_args__ = (UniqueConstraint("event_id", name="uq_user_event_outbox_event_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    auth_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
