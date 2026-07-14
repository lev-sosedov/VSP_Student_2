from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from academic_service.db.session import get_session
from academic_service.services.service_education_plan import EducationPlanService
from academic_service.repositories.repository_education_plan import EducationPlanRepository
from academic_service.repositories.repository_direction import DirectionRepository
from academic_service.repositories.repository_education_plan_module import EducationPlanModuleRepository
from academic_service.repositories.repository_module import ModuleRepository
from academic_service.schemas.schemas_education_plan import (
    EducationPlanCreate,
    EducationPlanUpdate,
    EducationPlanPatch,
    EducationPlanResponse,
    EducationPlanListResponse,
    EducationPlanFilter,
    EducationPlanActivate
)


router = APIRouter(prefix="/education-plans", tags=["Education Plans"])


# Получение сервиса
def get_service(
        session: AsyncSession = Depends(get_session)
):
    return EducationPlanService(
        EducationPlanRepository(session),
        DirectionRepository(session),
        EducationPlanModuleRepository(session),
        ModuleRepository(session)
    )


# Создание учебного плана
@router.post(
    "/",
    response_model=EducationPlanResponse
)
async def create_plan(
        data: EducationPlanCreate,
        service: EducationPlanService = Depends(get_service)
):
    try:
        return await service.create_education_plan(data)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# Получить по ID
@router.get(
    "/{plan_id}",
    response_model=EducationPlanResponse
)
async def get_plan(
        plan_id: int,
        service: EducationPlanService = Depends(get_service)
):
    try:
        return await service.get_plan_by_id(plan_id)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# Получить список учебных планов
@router.get(
    "/",
    response_model=EducationPlanListResponse
)
async def get_plans(
        limit: int = Query(20, ge=1),
        offset: int = Query(0, ge=0),
        service: EducationPlanService = Depends(get_service)
):
    plans = await service.get_all(
        limit,
        offset
    )

    return {
        "items": plans,
        "total": len(plans)
    }


# Полное обновление
@router.put(
    "/{plan_id}",
    response_model=EducationPlanResponse
)
async def update_plan(
        plan_id: int,
        data: EducationPlanUpdate,
        service: EducationPlanService = Depends(get_service)
):
    try:
        return await service.update_plan(
            plan_id,
            data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# Частичное обновление
@router.patch(
    "/{plan_id}",
    response_model=EducationPlanResponse
)
async def patch_plan(
        plan_id: int,
        data: EducationPlanPatch,
        service: EducationPlanService = Depends(get_service)
):
    try:
        return await service.patch_plan(
            plan_id,
            data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# Безопасное удаление плана
@router.delete(
    "/{plan_id}"
)
async def delete_plan(
        plan_id: int,
        service: EducationPlanService = Depends(get_service)
):
    try:
        return await service.delete_plan(plan_id)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ---------------------------------------------------


# Получить активные планы +
@router.get(
    "/active",
    response_model=list[EducationPlanResponse]
)
async def get_active_plans(
        service: EducationPlanService = Depends(get_service)
):
    return await service.plan_repo.get_active()


# Получить закрытые планы +
@router.get(
    "/closed",
    response_model=list[EducationPlanResponse]
)
async def get_closed_plans(
        service: EducationPlanService = Depends(get_service)
):
    return await service.plan_repo.get_closed()


# Фильтр планов +
@router.post(
    "/filter",
    response_model=list[EducationPlanResponse]
)
async def filter_plans(
        data: EducationPlanFilter,
        service: EducationPlanService = Depends(get_service)
):
    return await service.plan_repo.filter(
        direction_id=data.direction_id,
        duration_months=data.duration_months,
        is_active=data.is_active
    )


# Получить структуру учебного плана +
@router.get(
    "/{plan_id}/structure"
)
async def get_structure(
        plan_id: int,
        service: EducationPlanService = Depends(get_service)
):
    try:
        return await service.get_modules(plan_id)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# # Архивация учебного плана +
@router.patch(
    "/{plan_id}/activate",
    response_model=EducationPlanResponse
)
async def activate_plan(
        plan_id: int,
        data: EducationPlanActivate,
        service: EducationPlanService = Depends(get_service)
):
    plan = await service.get_plan_by_id(plan_id)

    plan.is_active = True
    plan.closed_at = None

    return await service.plan_repo.update(plan_id, {"is_active": True, "closed_at": None})


# Добавить модуль в план +
@router.post(
    "/{plan_id}/modules"
)
async def add_module(
        plan_id: int,
        module_id: int,
        order_number: int,
        service: EducationPlanService = Depends(get_service)
):
    try:
        return await service.add_module(
            plan_id,
            module_id,
            order_number
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# Удалить модуль из плана +
@router.delete(
    "/{plan_id}/modules/{module_id}"
)
async def remove_module(
        plan_id: int,
        module_id: int,
        service: EducationPlanService = Depends(get_service)
):
    return await service.remove_module(
        plan_id,
        module_id
    )


# Изменить порядок модулей +
@router.patch(
    "/{plan_id}/modules/reorder"
)
async def reorder_modules(
        plan_id: int,
        modules: list[dict],
        service: EducationPlanService = Depends(get_service)
):
    return await service.reorder_modules(
        plan_id,
        modules
    )
