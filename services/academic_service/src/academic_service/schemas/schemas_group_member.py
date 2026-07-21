from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# Базовые поля участника группы
class GroupMemberBase(BaseModel):
    group_id: int # группа
    user_id: int # пользователь из user-service
    role: str # student / teacher


# Добавление участника
class GroupMemberCreate(GroupMemberBase):
    pass


# Полное обновление
class GroupMemberUpdate(BaseModel):
    group_id: Optional[int] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


# Частичное обновление
class GroupMemberPatch(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


# Ответ API
class GroupMemberResponse(BaseModel):
    id: int # ID записи
    group_id: int # группа
    user_id: int # пользователь
    role: str # роль
    joined_at: datetime # дата вступления
    left_at: Optional[datetime] # дата выхода
    is_active: bool # активен
    model_config = ConfigDict(from_attributes=True)


# Короткий ответ
# например при выводе состава группы
class GroupMemberShortResponse(BaseModel):
    user_id: int
    role: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


# Ответ списка участников
class GroupMemberListResponse(BaseModel):
    items: list[GroupMemberResponse]
    total: int


# Фильтр участников
class GroupMemberFilter(BaseModel):
    group_id: Optional[int] = None
    user_id: Optional[int] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# Выход из группы
class GroupMemberLeave(BaseModel):
    left_at: datetime


# Вернуть в группу
class GroupMemberActivate(BaseModel):
    is_active: bool = True


# Проверка участия
class GroupMemberExistsResponse(BaseModel):
    exists: bool


# Перенос пользователя в другую группу
class GroupMemberTransfer(BaseModel):
    old_group_id: int
    new_group_id: int
    user_id: int


# Студент группы с данными профиля из User Service
class GroupStudentResponse(BaseModel):
    membership_id: int
    group_id: int
    user_id: int

    user_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None

    is_active: bool


# Список студентов группы
class GroupStudentListResponse(BaseModel):
    total: int
    items: list[GroupStudentResponse]