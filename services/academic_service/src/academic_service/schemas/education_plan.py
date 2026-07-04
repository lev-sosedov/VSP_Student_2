from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# Базовые поля учебного плана
class EducationPlanBase(BaseModel):
    direction_id: int # направление обучения
    name: str # название плана (например: "Базовый 24 месяца")
    duration_months: int # длительность (24 / 36 / 60)
    lessons_per_week: int # количество занятий в неделю


# Создание учебного плана
class EducationPlanCreate(EducationPlanBase):
    pass


# Обновление (полное)
class EducationPlanUpdate(BaseModel):
    direction_id: Optional[int] = None
    name: Optional[str] = None
    duration_months: Optional[int] = None
    lessons_per_week: Optional[int] = None


# Частичное обновление
class EducationPlanPatch(BaseModel):
    direction_id: Optional[int] = None
    name: Optional[str] = None
    duration_months: Optional[int] = None
    lessons_per_week: Optional[int] = None
    is_active: Optional[bool] = None


# Закрытие учебного плана
class EducationPlanClose(BaseModel):
    closed_at: datetime


# Активация учебного плана
class EducationPlanActivate(BaseModel):
    is_active: bool = True


# Ответ API
class EducationPlanResponse(BaseModel):
    id: int # ID плана
    direction_id: int # направление
    name: str # название
    duration_months: int # длительность
    lessons_per_week: int # занятия в неделю
    is_active: bool # активен
    created_at: datetime # дата создания
    closed_at: Optional[datetime] # дата закрытия
    model_config = ConfigDict(from_attributes=True)


# Краткий ответ
class EducationPlanShortResponse(BaseModel):
    id: int
    name: str
    duration_months: int
    model_config = ConfigDict(from_attributes=True)


# Детальный ответ
class EducationPlanDetailResponse(BaseModel):
    id: int
    direction_id: int
    name: str
    duration_months: int
    lessons_per_week: int
    is_active: bool
    created_at: datetime
    closed_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


# Фильтр
class EducationPlanFilter(BaseModel):
    direction_id: Optional[int] = None
    duration_months: Optional[int] = None
    is_active: Optional[bool] = None


# Список планов
class EducationPlanListResponse(BaseModel):
    items: list[EducationPlanResponse]
    total: int


# Проверка существования
class EducationPlanExistsResponse(BaseModel):
    exists: bool