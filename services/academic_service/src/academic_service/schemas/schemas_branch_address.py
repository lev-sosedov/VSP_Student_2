from pydantic import BaseModel, ConfigDict
from typing import Optional


# Базовые поля адреса
class BranchAddressBase(BaseModel):
    country: str = "Россия" # Страна
    city: str = "Краснодар" # Город
    street: str # Улица
    house: str # Номер дома
    building: Optional[str] = None # Корпус
    postal_code: Optional[str] = None # Почтовый индекс


# Создание адреса филиала
class BranchAddressCreate(BranchAddressBase):
    pass


# Полное обновление адреса
class BranchAddressUpdate(BranchAddressBase):
    pass


# Частичное обновление адреса
class BranchAddressPatch(BaseModel):
    country: Optional[str] = None # Страна
    city: Optional[str] = None # Город
    street: Optional[str] = None # Улица
    house: Optional[str] = None # Дом
    building: Optional[str] = None # Корпус
    postal_code: Optional[str] = None # Индекс


# Ответ API
class BranchAddressResponse(BranchAddressBase):
    id: int # ID адреса
    model_config = ConfigDict(from_attributes=True)


# Краткий ответ
# например при выводе филиалов
class BranchAddressShortResponse(BaseModel):
    id: int
    country: str
    city: str
    street: str
    house: str
    model_config = ConfigDict(from_attributes=True)


# Фильтр поиска адресов
class BranchAddressFilter(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None


# Адрес для списка
class BranchAddressListResponse(BaseModel):
    items: list[BranchAddressResponse]
    total: int


# Проверка существования адреса
class BranchAddressExistsResponse(BaseModel):
    exists: bool