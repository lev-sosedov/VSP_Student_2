from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date


# Базовые поля группы
class GroupBase(BaseModel):
    name: str # название группы
    branch_id: int # филиал
    direction_id: int # направление обучения
    education_plan_id: int # учебный план
    start_date: date # начало обучения
    end_date: Optional[date] = None # окончание обучения


# Создание группы
class GroupCreate(GroupBase):
    pass


# Полное обновление группы
class GroupUpdate(BaseModel):
    name: Optional[str] = None
    branch_id: Optional[int] = None
    direction_id: Optional[int] = None
    education_plan_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# Частичное обновление
class GroupPatch(BaseModel):
    name: Optional[str] = None
    branch_id: Optional[int] = None
    direction_id: Optional[int] = None
    education_plan_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None



# Закрытие группы
class GroupClose(BaseModel):
    closed_at: datetime


# Ответ API
class GroupResponse(BaseModel):
    id: int # ID группы
    name: str # название
    branch_id: int # филиал
    direction_id: int # направление
    education_plan_id: int # план
    start_date: date
    end_date: Optional[date]
    is_active: bool
    created_at: datetime
    closed_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


# Короткий ответ
# например при выводе списка групп
class GroupShortResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


# Детальный ответ группы
class GroupDetailResponse(BaseModel):
    id: int
    name: str
    branch_id: int
    direction_id: int
    education_plan_id: int
    start_date: date
    end_date: Optional[date]
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Фильтр групп
class GroupFilter(BaseModel):
    branch_id: Optional[int] = None
    direction_id: Optional[int] = None
    education_plan_id: Optional[int] = None
    is_active: Optional[bool] = None


# Список групп
class GroupListResponse(BaseModel):
    items: list[GroupResponse]
    total: int


# Проверка существования
class GroupExistsResponse(BaseModel):
    exists: bool


# Перевод группы в статус завершена
class GroupComplete(BaseModel):
    end_date: date