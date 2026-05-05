from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from common.utils.enum_role import RoleType


# 📥 создание пользователя (из auth_service)
class UserCreate(BaseModel):
    phone_number: str
    password: str  # уже ХЭШ!
    user_name: Optional[str] = None
    role: RoleType = RoleType.STUDENT


# 📝 обновление профиля
class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthday: Optional[date] = None
    avatar_url: Optional[str] = None


# 📤 ответ пользователю
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

    created_at: datetime

    class Config:
        from_attributes = True