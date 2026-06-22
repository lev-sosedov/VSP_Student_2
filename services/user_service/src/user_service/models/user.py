from sqlalchemy import Column, Integer, String, DateTime, Enum, Date, Boolean, func
from user_service.db.base import Base
from common.utils.enum_role import RoleType


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True) # личный идентификационный номер пользователя

    # === ЛОГИН ===
    phone_number = Column(String(20), unique=True, nullable=False) # номер телефона пользователя
    hashed_password = Column(String(255), nullable=False) # пароль

    # === ОСНОВНОЕ ===
    user_name = Column(String(20), unique=True, nullable=True) # имя (не никнейм)
    role = Column(Enum(RoleType), nullable=False, default=RoleType.USER) # роль в системе

    # === ПРОФИЛЬ ===
    email = Column(String(100), unique=True, nullable=True) # почта
    first_name = Column(String(20), nullable=True) # фамилия
    last_name = Column(String(20), nullable=True) # отчество
    birthday = Column(Date, nullable=True) # дата рождения
    avatar_url = Column(String(500), nullable=True) # аватарка

    # === ФЛАГИ ===
    is_active = Column(Boolean, default=True) # действующий аккаунт или нет
    is_account_verified = Column(Boolean, default=False) # подтвержденный аккаунт или нет
    is_phone_verified = Column(Boolean, default=False) # Телефон подтверждён кодом SMS

    # === ТЕХНИЧЕСКИЕ ===
    created_at = Column(DateTime, default=func.now()) # дата регистрации
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) # дата обновления данных