from fastapi import APIRouter, Depends, HTTPException, Query

from academic_service.services.education_plan_module_service import (
    EducationPlanModuleService
)

from academic_service.schemas.education_plan_module import (
    EducationPlanModuleCreate,
    EducationPlanModuleUpdate,
    EducationPlanModulePatch,
    EducationPlanModuleResponse,
    EducationPlanModuleListResponse,
    EducationPlanModuleExistsResponse,
    EducationPlanModuleReorder
)


router = APIRouter(
    prefix="/education-plan-modules",
    tags=["Education Plan Modules"]
)




# Получение сервиса
def get_service() -> EducationPlanModuleService:
    pass





# Создать связь план-модуль
@router.post(
    "/",
    response_model=EducationPlanModuleResponse
)
async def create_link(
        data:EducationPlanModuleCreate,
        service:EducationPlanModuleService = Depends(get_service)
):

    try:

        return await service.add_module(
            data.education_plan_id,
            data.module_id,
            data.order_number
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )






# Получить все модули конкретного плана
@router.get(
    "/plan/{plan_id}",
    response_model=list[EducationPlanModuleResponse]
)
async def get_plan_modules(
        plan_id:int,
        service:EducationPlanModuleService = Depends(get_service)
):

    return await service.get_plan_modules(
        plan_id
    )







# Получить количество модулей
@router.get(
    "/plan/{plan_id}/count"
)
async def count_modules(
        plan_id:int,
        service:EducationPlanModuleService = Depends(get_service)
):

    count = await service.count_modules(
        plan_id
    )

    return {
        "count": count
    }








# Получить конкретную связь
@router.get(
    "/plan/{plan_id}/module/{module_id}",
    response_model=EducationPlanModuleResponse
)
async def get_link(
        plan_id:int,
        module_id:int,
        service:EducationPlanModuleService = Depends(get_service)
):

    link = await service.repo.get_by_plan_and_module(
        plan_id,
        module_id
    )

    if not link:
        raise HTTPException(
            status_code=404,
            detail="Link not found"
        )

    return link







# Проверка существования связи
@router.get(
    "/exists",
    response_model=EducationPlanModuleExistsResponse
)
async def exists_link(
        education_plan_id:int,
        module_id:int,
        service:EducationPlanModuleService = Depends(get_service)
):

    exists = await service.check_exists(
        education_plan_id,
        module_id
    )

    return {
        "exists": exists
    }







# Полное обновление связи
@router.put(
    "/plan/{plan_id}/module/{module_id}",
    response_model=EducationPlanModuleResponse
)
async def update_link(
        plan_id:int,
        module_id:int,
        data:EducationPlanModuleUpdate,
        service:EducationPlanModuleService = Depends(get_service)
):

    link = await service.repo.get_by_plan_and_module(
        plan_id,
        module_id
    )


    if not link:
        raise HTTPException(
            status_code=404,
            detail="Link not found"
        )


    if data.order_number is not None:
        link.order_number = data.order_number


    return await service.repo.update(
        link
    )








# Частичное обновление связи
@router.patch(
    "/plan/{plan_id}/module/{module_id}",
    response_model=EducationPlanModuleResponse
)
async def patch_link(
        plan_id:int,
        module_id:int,
        data:EducationPlanModulePatch,
        service:EducationPlanModuleService = Depends(get_service)
):

    link = await service.repo.get_by_plan_and_module(
        plan_id,
        module_id
    )


    if not link:
        raise HTTPException(
            status_code=404,
            detail="Link not found"
        )


    if data.order_number is not None:
        link.order_number = data.order_number


    if data.is_active is not None:
        link.is_active = data.is_active


    return await service.repo.update(
        link
    )









# Изменить порядок одного модуля
@router.patch(
    "/plan/{plan_id}/module/{module_id}/order"
)
async def update_order(
        plan_id:int,
        module_id:int,
        new_order:int,
        service:EducationPlanModuleService = Depends(get_service)
):

    return await service.update_module_order(
        plan_id,
        module_id,
        new_order
    )








# Полная перестройка порядка
@router.patch(
    "/plan/{plan_id}/reorder"
)
async def reorder(
        plan_id:int,
        data:EducationPlanModuleReorder,
        service:EducationPlanModuleService = Depends(get_service)
):

    return await service.reorder_plan(
        plan_id,
        data
    )









# Массовое добавление модулей
@router.post(
    "/plan/{plan_id}/bulk"
)
async def bulk_add(
        plan_id:int,
        modules:list[dict],
        service:EducationPlanModuleService = Depends(get_service)
):

    return await service.bulk_add_modules(
        plan_id,
        modules
    )









# Полностью заменить список модулей
@router.put(
    "/plan/{plan_id}/replace"
)
async def replace_modules(
        plan_id:int,
        modules:list[dict],
        service:EducationPlanModuleService = Depends(get_service)
):

    return await service.replace_modules(
        plan_id,
        modules
    )








# Удалить модуль из плана
@router.delete(
    "/plan/{plan_id}/module/{module_id}"
)
async def remove_module(
        plan_id:int,
        module_id:int,
        service:EducationPlanModuleService = Depends(get_service)
):

    return await service.remove_module(
        plan_id,
        module_id
    )








# Очистить весь план
@router.delete(
    "/plan/{plan_id}"
)
async def clear_plan(
        plan_id:int,
        service:EducationPlanModuleService = Depends(get_service)
):

    return await service.clear_plan(
        plan_id
    )