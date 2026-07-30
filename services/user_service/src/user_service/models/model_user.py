from sqlalchemy import Column, Integer, String, DateTime, Enum, Date, Boolean, func
from user_service.db.db_base import Base
from common.utils.enum_role import RoleType

from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True) # личный идентификационный номер пользователя
    auth_id = Column(Integer, unique=True, nullable=True)

    # === ЛОГИН ===
    phone_number = Column(String(20), unique=True, nullable=False) # номер телефона пользователя

    # === ОСНОВНОЕ ===
    user_name = Column(String(50), nullable=True) # имя (не никнейм)
    role = Column(Enum(RoleType), nullable=False, default=RoleType.USER) # роль в системе

    # === ПРОФИЛЬ ===
    email = Column(String(255), unique=True, nullable=True) # почта
    first_name = Column(String(100), nullable=True) # фамилия
    last_name = Column(String(100), nullable=True) # отчество
    birthday = Column(Date, nullable=True) # дата рождения
    avatar_url = Column(String(500), nullable=True) # аватарка
    about = Column(String(1000), nullable=True)  # информация о пользователе

    # === ФЛАГИ ===
    is_active = Column(Boolean, default=True) # действующий аккаунт или нет
    is_account_verified = Column(Boolean, default=False) # подтвержденный аккаунт или нет
    is_phone_verified = Column(Boolean, default=False) # Телефон подтверждён кодом SMS

    # === ТЕХНИЧЕСКИЕ ===
    created_at = Column(DateTime, default=func.now()) # дата регистрации
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) # дата обновления данных

    # === СВЯЗИ РОДИТЕЛЕЙ И СТУДЕНТОВ ===

    # Если этот пользователь имеет роль parent,
    # здесь находятся его связи с детьми.
    children_links = relationship(
        "ParentStudentLink",
        foreign_keys="ParentStudentLink.parent_id",
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Если этот пользователь имеет роль student,
    # здесь находятся связи с его родителями.
    parent_links = relationship(
        "ParentStudentLink",
        foreign_keys="ParentStudentLink.student_id",
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )