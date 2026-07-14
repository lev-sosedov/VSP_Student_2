from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# Базовая модель модуля
class ModuleBase(BaseModel):
    name: str # название модуля
    description: Optional[str] = None # описание модуля


# Создание модуля
class ModuleCreate(ModuleBase):
    pass


# Обновление модуля (полное)
class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Частичное обновление модуля
class ModulePatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# Ответ API (основной)
class ModuleResponse(BaseModel):
    id: int # ID модуля
    name: str # название модуля
    description: Optional[str] # описание
    is_active: bool # активен или нет
    created_at: datetime # дата создания
    closed_at: Optional[datetime] # дата закрытия (если архивирован)
    model_config = ConfigDict(from_attributes=True)


# Краткий ответ (для списков)
class ModuleShortResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


# Детальный ответ
class ModuleDetailResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    closed_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


# Фильтр модулей
class ModuleFilter(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None


# Список модулей
class ModuleListResponse(BaseModel):
    items: list[ModuleResponse]
    total: int


# Проверка существования
class ModuleExistsResponse(BaseModel):
    exists: bool


# Архивация модуля
class ModuleArchive(BaseModel):
    closed_at: datetime


# Активация модуля
class ModuleActivate(BaseModel):
    is_active: bool = True