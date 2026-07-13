from fastapi import APIRouter, Depends, HTTPException, Query

from academic_service.services.education_plan_service import EducationPlanService

from academic_service.schemas.education_plan import (
    EducationPlanCreate,
    EducationPlanUpdate,
    EducationPlanPatch,
    EducationPlanResponse,
    EducationPlanListResponse,
    EducationPlanExistsResponse,
    EducationPlanFilter,
    EducationPlanClose,
    EducationPlanActivate
)

router = APIRouter(
    prefix="/education-plans",
    tags=["Education Plans"]
)


# Получение сервиса
def get_service() -> EducationPlanService:
    pass


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
    plans = await service.get_all_plans(
        limit,
        offset
    )

    return {
        "items": plans,
        "total": len(plans)
    }


# Получить активные планы
@router.get(
    "/active",
    response_model=list[EducationPlanResponse]
)
async def get_active_plans(
        service: EducationPlanService = Depends(get_service)
):
    return await service.plan_repo.get_active()


# Получить закрытые планы
@router.get(
    "/closed",
    response_model=list[EducationPlanResponse]
)
async def get_closed_plans(
        service: EducationPlanService = Depends(get_service)
):
    return await service.plan_repo.get_closed()


# Фильтр планов
@router.post(
    "/filter",
    response_model=list[EducationPlanResponse]
)
async def filter_plans(
        data: EducationPlanFilter,
        service: EducationPlanService = Depends(get_service)
):
    return await service.plan_repo.filter(data)


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
        return await service.get_education_plan(plan_id)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# Получить структуру учебного плана
@router.get(
    "/{plan_id}/structure"
)
async def get_structure(
        plan_id: int,
        service: EducationPlanService = Depends(get_service)
):
    try:
        return await service.get_plan_structure(plan_id)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


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


# Архивация учебного плана
@router.patch(
    "/{plan_id}/archive",
    response_model=EducationPlanResponse
)
async def close_plan(
        plan_id: int,
        data: EducationPlanClose,
        service: EducationPlanService = Depends(get_service)
):
    plan = await service.get_education_plan(plan_id)

    plan.is_active = False
    plan.closed_at = data.closed_at

    return await service.plan_repo.update(plan)


# Активировать план
@router.patch(
    "/{plan_id}/activate",
    response_model=EducationPlanResponse
)
async def activate_plan(
        plan_id: int,
        data: EducationPlanActivate,
        service: EducationPlanService = Depends(get_service)
):
    plan = await service.get_education_plan(plan_id)

    plan.is_active = True
    plan.closed_at = None

    return await service.plan_repo.update(plan)


# Проверка существования
@router.get(
    "/{plan_id}/exists",
    response_model=EducationPlanExistsResponse
)
async def exists_plan(
        plan_id: int,
        service: EducationPlanService = Depends(get_service)
):
    plan = await service.plan_repo.get_by_id(plan_id)

    return {
        "exists": plan is not None
    }


# Добавить модуль в план
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
        return await service.add_module_to_plan(
            plan_id,
            module_id,
            order_number
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# Удалить модуль из плана
@router.delete(
    "/{plan_id}/modules/{module_id}"
)
async def remove_module(
        plan_id: int,
        module_id: int,
        service: EducationPlanService = Depends(get_service)
):
    return await service.remove_module_from_plan(
        plan_id,
        module_id
    )


# Изменить порядок модулей
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


# Массовое добавление модулей
@router.post(
    "/{plan_id}/modules/bulk"
)
async def bulk_modules(
        plan_id: int,
        modules: list[dict],
        service: EducationPlanService = Depends(get_service)
):
    return await service.add_module_to_plan(
        plan_id,
        modules
    )


# Удалить все модули плана
@router.delete(
    "/{plan_id}/modules"
)
async def clear_plan(
        plan_id: int,
        service: EducationPlanService = Depends(get_service)
):
    return await service.plan_module_repo.delete_by_plan_id(
        plan_id
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
