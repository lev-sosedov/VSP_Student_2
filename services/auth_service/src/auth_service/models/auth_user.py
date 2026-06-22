from sqlalchemy import (Column, Integer, String, Boolean, DateTime)

from datetime import datetime

from auth_service.db.base import Base


class AuthUser(Base):

    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    user_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="USER", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)