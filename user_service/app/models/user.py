from sqlalchemy import Column, Integer, String, DateTime, Enum, Date, Boolean, func
from user_service.app.db.base import Base
from common.utils.enum_role import RoleType


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    # === ЛОГИН ===
    phone_number = Column(String(20), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # === ОСНОВНОЕ ===
    user_name = Column(String(20), unique=True, nullable=True)

    role = Column(Enum(RoleType), nullable=False, default=RoleType.STUDENT)

    # === ПРОФИЛЬ ===
    email = Column(String(100), unique=True, nullable=True)
    first_name = Column(String(20), nullable=True)
    last_name = Column(String(20), nullable=True)
    birthday = Column(Date, nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # === ФЛАГИ ===
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)

    # === ТЕХНИЧЕСКИЕ ===
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())