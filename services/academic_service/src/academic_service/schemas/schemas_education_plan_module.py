from pydantic import BaseModel, ConfigDict
from typing import Optional


# Базовая связь учебного плана и модуля
class EducationPlanModuleBase(BaseModel):
    education_plan_id: int # учебный план
    module_id: int # модуль
    order_number: int # порядок прохождения (ВАЖНО)


# Создание связи
class EducationPlanModuleCreate(EducationPlanModuleBase):
    pass


# Обновление связи
class EducationPlanModuleUpdate(BaseModel):
    education_plan_id: Optional[int] = None
    module_id: Optional[int] = None
    order_number: Optional[int] = None


# Частичное обновление
class EducationPlanModulePatch(BaseModel):
    order_number: Optional[int] = None
    # is_active: Optional[bool] = None


# Ответ API
class EducationPlanModuleResponse(BaseModel):
    id: int # ID связи
    education_plan_id: int # план
    module_id: int # модуль
    order_number: int # порядок
    # is_active: bool # активна связь
    model_config = ConfigDict(from_attributes=True)


# Краткий ответ
class EducationPlanModuleShortResponse(BaseModel):
    module_id: int
    order_number: int
    model_config = ConfigDict(from_attributes=True)


# Список модулей учебного плана
class EducationPlanModuleListResponse(BaseModel):
    items: list[EducationPlanModuleResponse]
    total: int


# Проверка существования связи
class EducationPlanModuleExistsResponse(BaseModel):
    exists: bool


# Сортировка модулей в плане
class EducationPlanModuleReorder(BaseModel):
    education_plan_id: int
    modules: list[dict]