from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from academic_service.services.branch_service import BranchService
from academic_service.repositories.branch_repository import BranchRepository
from academic_service.repositories.branch_address_repository import BranchAddressRepository

from academic_service.schemas.branch import (
    BranchCreate,
    BranchUpdate,
    BranchPatch,
    BranchFilter,
    BranchActivate,
    BranchClose
)

from academic_service.schemas.branch_address import BranchAddressUpdate
from academic_service.db.session import get_session

router = APIRouter(prefix="/branches", tags=["Branches"])


# =========================
# DI
# =========================
def get_service(session: AsyncSession = Depends(get_session)):
    return BranchService(
        BranchRepository(session),
        BranchAddressRepository(session)
    )


# =========================
# Создать филиал
# =========================
@router.post("")
async def create_branch(data: BranchCreate, service: BranchService = Depends(get_service)):
    return await service.create_branch(data)


# =========================
# Получить филиал по ID
# =========================
@router.get("/{branch_id}")
async def get_branch(
        branch_id: int,
        service: BranchService = Depends(get_service)
):
    return await service.get_branch(branch_id)


# =========================
# Список филиалов
# =========================
@router.get("")
async def get_branches(
        active_only: bool = True,
        service: BranchService = Depends(get_service)
):
    return await service.get_branches(active_only)


# =========================
# Обновить филиал (PUT)
# =========================
@router.put("/{branch_id}")
async def update_branch(
        branch_id: int,
        data: BranchUpdate,
        service: BranchService = Depends(get_service)
):
    return await service.update_branch(branch_id, data)


# =========================
# PATCH филиал
# =========================
@router.patch("/{branch_id}")
async def patch_branch(
        branch_id: int,
        data: BranchPatch,
        service: BranchService = Depends(get_service)
):
    return await service.patch_branch(branch_id, data)


# =========================
# Удалить филиал
# =========================
@router.delete("/{branch_id}")
async def delete_branch(
        branch_id: int,
        service: BranchService = Depends(get_service)
):
    return await service.delete_branch(branch_id)


# --------------------------------------------------------------


# ========================= +
# Детальный филиал (branch + address)
# =========================
@router.get("/{branch_id}/detail")
async def get_branch_detail(
        branch_id: int,
        service: BranchService = Depends(get_service)
):
    return await service.get_branch_detail(branch_id)


# =========================
# Поиск по городу
# =========================
@router.get("/city/{city}")
async def get_by_city(
        city: str,
        service: BranchService = Depends(get_service)
):
    return await service.get_by_city(city)


# =========================+
# ❗ ЗАКРЫТЬ ФИЛИАЛ (BranchClose)
# =========================
@router.post("/{branch_id}/close")
async def close_branch(
        branch_id: int,
        data: BranchClose,
        service: BranchService = Depends(get_service)
):
    # можно расширить логикой closed_at позже
    return await service.close_branch(branch_id)


# =========================+
# ❗ АКТИВИРОВАТЬ ФИЛИАЛ (BranchActivate)
# =========================
@router.post("/{branch_id}/activate")
async def activate_branch(
        branch_id: int,
        data: BranchActivate,
        service: BranchService = Depends(get_service)
):
    return await service.restore_branch(branch_id)



# ========================= +
# Получить только адрес филиала
# =========================
@router.get("/{branch_id}/address")
async def get_address(
        branch_id: int,
        service: BranchService = Depends(get_service)
):
    return await service.get_address(branch_id)


# ========================= +
# Обновить адрес
# =========================
@router.put("/{branch_id}/address")
async def update_address(
        branch_id: int,
        data: BranchAddressUpdate,
        service: BranchService = Depends(get_service)
):
    return await service.update_address(branch_id, data)



# ========================= потом
# Статистика
# =========================
@router.get("/stats/active-count")
async def count_active(
        service: BranchService = Depends(get_service)
):
    return {"active": await service.count_active()}


# ========================= потом
# Short list UI
# =========================
@router.get("/short")
async def short_list(
        service: BranchService = Depends(get_service)
):
    return await service.get_short_list()


# =========================+
# Фильтр
# =========================
@router.post("/filter")
async def filter_branches(
        filters: BranchFilter,
        service: BranchService = Depends(get_service)
):
    if filters.city:
        return await service.get_by_city(filters.city)

    return await service.get_branches(
        active_only=filters.is_active if filters.is_active is not None else True
    )
