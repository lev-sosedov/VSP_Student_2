from fastapi import APIRouter, Depends, Query

from academic_service.services.service_direction import DirectionService
from academic_service.repositories.repository_direction import DirectionRepository
from academic_service.repositories.repository_education_plan import EducationPlanRepository

from academic_service.schemas.schemas_direction import (
    DirectionCreate,
    DirectionUpdate,
    DirectionPatch,
    DirectionResponse,
    DirectionListResponse,
    DirectionFilter,
    DirectionDetailResponse
)

router = APIRouter(
    prefix="/directions",
    tags=["Directions"]
)


def get_service():
    repo = DirectionRepository()
    plan_repo = EducationPlanRepository()

    return DirectionService(
        repo,
        plan_repo
    )


# Создание направления
@router.post(
    "/",
    response_model=DirectionResponse
)
async def create_direction(
        data: DirectionCreate,
        service: DirectionService = Depends(get_service)
):
    return await service.create_direction(data)


# Получить направление по ID
@router.get(
    "/{direction_id}",
    response_model=DirectionResponse
)
async def get_direction(
        direction_id: int,
        service: DirectionService = Depends(get_service)
):
    return await service.get_direction_by_id(direction_id)


# Список направлений
@router.get(
    "/",
    response_model=DirectionListResponse
)
async def get_directions(
        limit: int = Query(20),
        offset: int = Query(0),
        service: DirectionService = Depends(get_service)
):
    return await service.get_directions(
        limit,
        offset
    )


# Обновление направления
@router.put(
    "/{direction_id}",
    response_model=DirectionResponse
)
async def update_direction(
        direction_id: int,
        data: DirectionUpdate,
        service: DirectionService = Depends(get_service)
):
    return await service.update_direction(
        direction_id,
        data
    )


# Частичное обновление
@router.patch(
    "/{direction_id}",
    response_model=DirectionResponse
)
async def patch_direction(
        direction_id: int,
        data: DirectionPatch,
        service: DirectionService = Depends(get_service)
):
    return await service.patch_direction(
        direction_id,
        data
    )


# Удаление направления
@router.delete(
    "/{direction_id}"
)
async def delete_direction(
        direction_id: int,
        service: DirectionService = Depends(get_service)
):
    return await service.delete_direction(
        direction_id
    )


# ---------------------------------------------------------------------------------

# =========================
# Фильтр направлений
# =========================
@router.post(
    "/filter",
    response_model=list[DirectionResponse]
)
async def filter_directions(
        filters: DirectionFilter,
        service: DirectionService = Depends(get_service)
):
    return await service.filter_directions(filters)


# Получить направление с учебными планами +
@router.get(
    "/{direction_id}/plans"
)
async def get_direction_with_plans(
        direction_id: int,
        service: DirectionService = Depends(get_service)
):
    return await service.get_direction_with_plans(direction_id)


# Поиск направлений +
@router.get(
    "/search"
)
async def search_direction(
        q: str,
        service: DirectionService = Depends(get_service)
):
    return await service.search(q)


# Закрыть направление +
@router.post(
    "/{direction_id}/close",
    response_model=DirectionResponse
)
async def close_direction(
        direction_id: int,
        service: DirectionService = Depends(get_service)
):
    return await service.close_direction(
        direction_id
    )


# Активировать направление +
@router.post(
    "/{direction_id}/activate",
    response_model=DirectionResponse
)
async def activate_direction(
        direction_id: int,
        service: DirectionService = Depends(get_service)
):
    return await service.activate_direction(
        direction_id
    )


# Детальная информация о направлении +
@router.get("/{direction_id}/detail", response_model=DirectionDetailResponse)
async def get_direction_detail(
        direction_id: int,
        service: DirectionService = Depends(get_service)
):
    direction = await service.get_by_id(direction_id)

    return direction
