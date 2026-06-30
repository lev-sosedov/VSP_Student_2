from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from academic_service.services.branch_address import BranchAddressService
from academic_service.repositories.branch_address_repository import BranchAddressRepository

from academic_service.schemas.branch_address import (
    BranchAddressCreate,
    BranchAddressUpdate,
    BranchAddressPatch,
    BranchAddressFilter
)

from academic_service.db.session import get_session


router = APIRouter(prefix="/branch-address", tags=["Branch Address"])


# DI
def get_service(session: AsyncSession = Depends(get_session)):
    repo = BranchAddressRepository(session)
    return BranchAddressService(repo)


# =========================
# Создать адрес
# =========================
@router.post("")
async def create_address(
    data: BranchAddressCreate,
    service: BranchAddressService = Depends(get_service)
):
    return await service.create_address(data)


# =========================
# Получить адрес по ID
# =========================
@router.get("/{address_id}")
async def get_address(
    address_id: int,
    service: BranchAddressService = Depends(get_service)
):
    return await service.get_address(address_id)


# =========================
# Список адресов (пагинация)
# =========================
@router.get("")
async def get_addresses(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: BranchAddressService = Depends(get_service)
):
    return await service.get_addresses(limit, offset)


# =========================
# Обновление адреса (PUT)
# =========================
@router.put("/{address_id}")
async def update_address(
    address_id: int,
    data: BranchAddressUpdate,
    service: BranchAddressService = Depends(get_service)
):
    return await service.update_address(address_id, data)


# =========================
# PATCH обновление
# =========================
@router.patch("/{address_id}")
async def patch_address(
    address_id: int,
    data: BranchAddressPatch,
    service: BranchAddressService = Depends(get_service)
):
    return await service.patch_address(address_id, data)


# =========================
# Удалить адрес
# =========================
@router.delete("/{address_id}")
async def delete_address(
    address_id: int,
    service: BranchAddressService = Depends(get_service)
):
    return await service.delete_address(address_id)


# =========================
# Проверка существования
# =========================
@router.get("/{address_id}/exists")
async def exists(
    address_id: int,
    service: BranchAddressService = Depends(get_service)
):
    return {"exists": await service.exists(address_id)}


# =========================
# Поиск адресов
# =========================
@router.get("/search/{query}")
async def search(
    query: str,
    service: BranchAddressService = Depends(get_service)
):
    return await service.search(query)


# =========================
# По стране
# =========================
@router.get("/country/{country}")
async def get_by_country(
    country: str,
    service: BranchAddressService = Depends(get_service)
):
    return await service.get_by_country(country)


# =========================
# По городу
# =========================
@router.get("/city/{city}")
async def get_by_city(
    city: str,
    service: BranchAddressService = Depends(get_service)
):
    return await service.get_by_city(city)


# =========================
# Фильтр (гибкий endpoint)
# =========================
@router.post("/filter")
async def filter_addresses(
    filters: BranchAddressFilter,
    service: BranchAddressService = Depends(get_service)
):
    # если в репозитории нет filter — можно расширить позже
    return await service.search(
        filters.city or filters.country or filters.street or ""
    )


# =========================
# Красивый формат адреса
# =========================
@router.get("/{address_id}/full")
async def get_full_address(
    address_id: int,
    service: BranchAddressService = Depends(get_service)
):
    return {
        "address": await service.get_full_address(address_id)
    }