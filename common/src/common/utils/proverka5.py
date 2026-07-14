from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from academic_service.db.session import get_session
from academic_service.repositories.repository_education_plan_module import EducationPlanModuleRepository
from academic_service.repositories.repository_education_plan import EducationPlanRepository
from academic_service.repositories.repository_module import ModuleRepository
from academic_service.services.service_education_plan_module import EducationPlanModuleService
from academic_service.schemas.schemas_education_plan_module import (
    EducationPlanModuleCreate,
    EducationPlanModuleUpdate,
    EducationPlanModulePatch,
    EducationPlanModuleResponse,
    EducationPlanModuleListResponse,
    EducationPlanModuleExistsResponse,
    EducationPlanModuleReorder
)

router = APIRouter(prefix="/education-plan-modules", tags=["Education Plan Modules"])


# Получение сервиса
def get_service(session: AsyncSession = Depends(get_session)):
    return EducationPlanModuleService(
        EducationPlanModuleRepository(session),
        EducationPlanRepository(session),
        ModuleRepository(session))


# Создать связь план-модуль
@router.post("/", response_model=EducationPlanModuleResponse)
async def create_link(
        data: EducationPlanModuleCreate,
        service: EducationPlanModuleService = Depends(get_service)):
    try:

        return await service.add_module(data)

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
        plan_id: int,
        service: EducationPlanModuleService = Depends(get_service)
):
    return await service.get_plan_modules(
        plan_id
    )


# Получить конкретную связь
@router.get(
    "/plan/{plan_id}/module/{module_id}",
    response_model=EducationPlanModuleResponse
)
async def get_link(
        plan_id: int,
        module_id: int,
        service: EducationPlanModuleService = Depends(get_service)
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
        education_plan_id: int,
        module_id: int,
        service: EducationPlanModuleService = Depends(get_service)
):
    exists = await service.check_exists(
        education_plan_id,
        module_id
    )

    return {
        "exists": exists
    }


# Изменить порядок одного модуля
@router.patch(
    "/plan/{plan_id}/module/{module_id}/order"
)
async def update_order(
        plan_id: int,
        module_id: int,
        new_order: int,
        service: EducationPlanModuleService = Depends(get_service)
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
        plan_id: int,
        data: EducationPlanModuleReorder,
        service: EducationPlanModuleService = Depends(get_service)
):
    return await service.reorder_plan(
        plan_id,
        data
    )


# Удалить модуль из плана
@router.delete(
    "/plan/{plan_id}/module/{module_id}"
)
async def remove_module(
        plan_id: int,
        module_id: int,
        service: EducationPlanModuleService = Depends(get_service)
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
        plan_id: int,
        service: EducationPlanModuleService = Depends(get_service)
):
    return await service.clear_plan(
        plan_id
    )


# ---------------------------------------------


# Получить количество модулей
@router.get(
    "/plan/{plan_id}/count"
)
async def count_modules(
        plan_id: int,
        service: EducationPlanModuleService = Depends(get_service)
):
    count = await service.count_modules(
        plan_id
    )

    return {
        "count": count
    }


# Полное обновление связи
@router.put(
    "/plan/{plan_id}/module/{module_id}",
    response_model=EducationPlanModuleResponse
)
async def update_link(
        plan_id: int,
        module_id: int,
        data: EducationPlanModuleUpdate,
        service: EducationPlanModuleService = Depends(get_service)
):
    try:
        return await service.update(
            plan_id,
            module_id,
            data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# =========================
# PATCH связь план-модуль
# =========================

@router.patch(
    "/plan/{plan_id}/module/{module_id}",
    status_code=status.HTTP_200_OK,
    response_model=EducationPlanModuleResponse,
    summary="Частично обновить связь план-модуль",
    description="""
Частичное обновление связи между учебным планом и модулем.

Можно изменить:

- порядок прохождения модуля;
- активность связи.

Используется администраторами системы.
""",
    response_description="Обновленная связь план-модуль",
    responses={
        404: {
            "description": "Связь план-модуль не найдена"
        },
        422: {
            "description": "Ошибка валидации данных"
        },
        500: {
            "description": "Внутренняя ошибка сервера"
        }
    }
)
async def patch_link(
        plan_id: int,
        module_id: int,
        data: EducationPlanModulePatch,
        service: EducationPlanModuleService = Depends(get_service)
):
    try:
        return await service.patch(
            plan_id,
            module_id,
            data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
