from sqlalchemy import (Boolean, CheckConstraint, Column, DateTime, Integer, String)
from sqlalchemy.orm import validates

from datetime import datetime

from auth_service.db.db_base import Base


class AuthUser(Base):

    __tablename__ = "auth_users"
    __table_args__ = (
        CheckConstraint("token_version >= 1", name="ck_auth_users_token_version_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    user_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="USER", nullable=False)
    is_active = Column(Boolean, default=True)
    token_version = Column(Integer, nullable=False, default=1, server_default="1")
    created_at = Column(DateTime, default=datetime.utcnow)

    @validates("token_version")
    def validate_token_version(self, _key: str, value: int) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError("token_version must be a positive integer")
        return value
