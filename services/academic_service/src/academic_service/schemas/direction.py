from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# Базовые поля направления
class DirectionBase(BaseModel):
    name: str # название направления
    description: Optional[str] = None # описание


# Создание направления
class DirectionCreate(DirectionBase):
    pass


# Полное обновление
class DirectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Частичное обновление
class DirectionPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# Закрытие направления
class DirectionClose(BaseModel):
    closed_at: datetime


# Активация направления
class DirectionActivate(BaseModel):
    is_active: bool = True


# Ответ API
class DirectionResponse(BaseModel):
    id: int # ID направления
    name: str # название
    description: Optional[str]
    is_active: bool # активно
    created_at: datetime # дата создания
    closed_at: Optional[datetime] # дата закрытия
    model_config = ConfigDict(from_attributes=True)


# Короткий ответ
# например при создании группы
class DirectionShortResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


# Детальный ответ
class DirectionDetailResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    closed_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


# Фильтр направлений
class DirectionFilter(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


# Список направлений
class DirectionListResponse(BaseModel):
    items: list[DirectionResponse]
    total: int


# Проверка существования
class DirectionExistsResponse(BaseModel):
    exists: bool