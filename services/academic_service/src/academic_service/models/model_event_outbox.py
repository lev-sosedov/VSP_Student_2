from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from academic_service.db.db_base import Base

class EventOutbox(Base):
    __tablename__ = "event_outbox"
    __table_args__ = (UniqueConstraint("event_id", name="uq_academic_event_outbox_event_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    event_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    producer: Mapped[str] = mapped_column(String(128), nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(64))
    causation_id: Mapped[str | None] = mapped_column(String(64))
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    published_at: Mapped[datetime | None] = mapped_column(DateTime)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_error_code: Mapped[str | None] = mapped_column(String(64))
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime)
    claimed_by: Mapped[str | None] = mapped_column(String(64))
