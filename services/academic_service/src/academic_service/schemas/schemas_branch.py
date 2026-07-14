from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


from academic_service.schemas.schemas_branch_address import (BranchAddressResponse)
from academic_service.schemas.schemas_branch_address import BranchAddressCreate


# Базовые поля филиала
class BranchBase(BaseModel):
    branch_address_id: int # адрес филиала
    phone: Optional[str] = None # телефон
    email: Optional[str] = None # почта


# Создание филиала
class BranchCreate(BranchBase):
    # address: BranchAddressCreate
    pass


# Полное обновление филиала
class BranchUpdate(BaseModel):
    branch_address_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None


# Частичное обновление
class BranchPatch(BaseModel):
    branch_address_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


# Закрытие филиала
class BranchClose(BaseModel):
    closed_at: datetime


# Открытие филиала
class BranchActivate(BaseModel):
    is_active: bool = True


# Ответ API (без адреса)
class BranchResponse(BaseModel):
    id: int # ID филиала
    branch_address_id: int # адрес
    phone: Optional[str]
    email: Optional[str]
    is_active: bool
    created_at: datetime
    closed_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


# Полный ответ с адресом
class BranchDetailResponse(BaseModel):
    id: int
    phone: Optional[str]
    email: Optional[str]
    address: BranchAddressResponse
    is_active: bool
    created_at: datetime
    closed_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


# Краткая информация
# например в списках групп
class BranchShortResponse(BaseModel):
    id: int
    city: str
    street: str
    house: str
    model_config = ConfigDict(from_attributes=True)


# Фильтр филиалов
class BranchFilter(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = None


# Список филиалов
class BranchListResponse(BaseModel):
    items: list[BranchResponse]
    total: int


# Проверка существования
class BranchExistsResponse(BaseModel):
    exists: bool