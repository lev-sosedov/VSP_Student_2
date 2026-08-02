from sqlalchemy import Column, Integer, String, DateTime, func
from auth_service.db.db_base import Base


class ProcessedUserEvent(Base):
    __tablename__ = "processed_user_events"
    id = Column(Integer, primary_key=True)
    event_id = Column(String(64), unique=True, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=False, server_default=func.now())
