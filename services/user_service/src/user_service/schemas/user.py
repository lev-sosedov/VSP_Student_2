from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

from common.utils.enum_role import RoleType


# создание пользователя (из user_service)
class UserCreate(BaseModel):
    phone_number: str
    user_name: Optional[str] = None


# обновление профиля
class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthday: Optional[date] = None
    avatar_url: Optional[str] = None


# ответ пользователю
class UserResponse(BaseModel):
    id: int
    phone_number: str
    user_name: Optional[str]

    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    birthday: Optional[date]
    avatar_url: Optional[str]

    role: RoleType

    is_active: bool
    is_account_verified: bool
    is_phone_verified: bool

    created_at: datetime
    updated_at: Optional[datetime]


    class Config:
        from_attributes = True


# изменение роли (только admin)
class UserRoleUpdate(BaseModel):
    role: RoleType


# Список пользователей (для admin)
class UserListResponse(BaseModel):
    id: int
    phone_number: str
    user_name: Optional[str]

    role: RoleType

    is_active: bool
    is_account_verified: bool


    class Config:
        from_attributes = True


# подтверждение аккаунта (admin)
class UserVerifyUpdate(BaseModel):
    is_account_verified: bool


# блокировка пользователя (admin)
class UserStatusUpdate(BaseModel):
    is_active: bool


# смена пароля (позже auth-service)
class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str