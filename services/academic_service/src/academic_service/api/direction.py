from fastapi import APIRouter, Depends, Query

from academic_service.services.direction_service import DirectionService
from academic_service.repositories.direction_repository import DirectionRepository
from academic_service.repositories.education_plan_repository import EducationPlanRepository

from academic_service.schemas.direction import (
    DirectionCreate,
    DirectionUpdate,
    DirectionPatch,
    DirectionResponse,
    DirectionListResponse,
    DirectionExistsResponse,
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



# Получить направление с учебными планами
@router.get(
    "/{direction_id}/plans"
)
async def get_direction_with_plans(
        direction_id: int,
        service: DirectionService = Depends(get_service)
):
    return await service.get_direction_with_plans(direction_id)



# Получить по названию
@router.get(
    "/search/name"
)
async def get_by_name(
        name: str,
        service: DirectionService = Depends(get_service)
):
    return await service.get_direction_by_name(name)



# Поиск направлений
@router.get(
    "/search"
)
async def search_direction(
        q: str,
        service: DirectionService = Depends(get_service)
):
    return await service.search(q)



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



# Только активные направления
@router.get(
    "/active/list"
)
async def get_active(
        service: DirectionService = Depends(get_service)
):
    return await service.get_active_directions()



# Только закрытые направления
@router.get(
    "/closed/list"
)
async def get_closed(
        service: DirectionService = Depends(get_service)
):
    return await service.get_closed_directions()



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



# Закрыть направление
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



# Активировать направление
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



# Проверка существования
@router.get(
    "/{direction_id}/exists",
    response_model=DirectionExistsResponse
)
async def exists(
        direction_id: int,
        service: DirectionService = Depends(get_service)
):

    result = await service.exists(direction_id)

    return {
        "exists": result
    }



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