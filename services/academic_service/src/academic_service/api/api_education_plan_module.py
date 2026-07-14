from fastapi import APIRouter, Depends, HTTPException, status
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
    EducationPlanModuleExistsResponse,
    EducationPlanModuleReorder
)

router = APIRouter(
    prefix="/education-plan-modules",
    tags=["Education Plan Modules"]
)


# =========================
# DI
# =========================

def get_service(
        session: AsyncSession = Depends(get_session)
):
    return EducationPlanModuleService(
        EducationPlanModuleRepository(session),
        EducationPlanRepository(session),
        ModuleRepository(session)
    )


# =========================
# Создать связь план-модуль
# =========================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=EducationPlanModuleResponse,
    summary="Добавить модуль в учебный план",
    description="""
Создание связи между учебным планом и модулем.

Во время создания:

- проверяется существование учебного плана;
- проверяется существование модуля;
- создается связь;
- сохраняется порядок прохождения модуля.

Используется администраторами системы.
""",
    response_description="Созданная связь план-модуль",
    responses={
        400: {
            "description": "Модуль уже добавлен или данные некорректны"
        },
        422: {
            "description": "Ошибка валидации данных"
        }
    }
)
async def create_link(
        data: EducationPlanModuleCreate,
        service: EducationPlanModuleService = Depends(get_service)
):
    try:
        return await service.add_module(data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Получить модули плана
# =========================

@router.get(
    "/plan/{plan_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[EducationPlanModuleResponse],
    summary="Получить модули учебного плана",
    description="""
Возвращает список всех модулей,
которые входят в выбранный учебный план.

Модули отсортированы
по порядку прохождения.
""",
    response_description="Список модулей учебного плана",
    responses={
        404: {
            "description": "Учебный план не найден"
        }
    }
)
async def get_plan_modules(
        plan_id: int,
        service: EducationPlanModuleService = Depends(get_service)
):
    try:
        return await service.get_plan_modules(plan_id)

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


# =========================
# Получить конкретную связь
# =========================

@router.get(
    "/plan/{plan_id}/module/{module_id}",
    status_code=status.HTTP_200_OK,
    response_model=EducationPlanModuleResponse,
    summary="Получить связь план-модуль",
    description="""
Получение конкретной связи:

- учебный план;
- модуль;
- порядок прохождения.
""",
    response_description="Информация о связи план-модуль",
    responses={
        404: {
            "description": "Связь не найдена"
        }
    }
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )

    return link


# =========================
# Проверка существования связи
# =========================

@router.get(
    "/exists",
    status_code=status.HTTP_200_OK,
    response_model=EducationPlanModuleExistsResponse,
    summary="Проверить наличие связи план-модуль",
    description="""
Проверяет существует ли связь
между выбранным учебным планом и модулем.
""",
    response_description="Результат проверки"
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


# =========================
# Изменить порядок одного модуля
# =========================

@router.patch(
    "/plan/{plan_id}/module/{module_id}/order",
    status_code=status.HTTP_200_OK,
    summary="Изменить порядок модуля",
    description="""
Изменяет порядок прохождения
одного модуля внутри учебного плана.
""",
    response_description="Обновленная связь",
    responses={
        404: {
            "description": "Модуль не найден в плане"
        }
    }
)
async def update_order(
        plan_id: int,
        module_id: int,
        new_order: int,
        service: EducationPlanModuleService = Depends(get_service)
):
    try:
        return await service.update_module_order(
            plan_id,
            module_id,
            new_order
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# =========================
# Полная перестройка порядка
# =========================

@router.patch(
    "/plan/{plan_id}/reorder",
    status_code=status.HTTP_200_OK,
    summary="Изменить порядок всех модулей",
    description="""
Полностью изменяет последовательность
модулей внутри учебного плана.

Используется при изменении структуры курса.
""",
    response_description="Обновленный список модулей",
    responses={
        404: {
            "description": "Модуль не найден в плане"
        }
    }
)
async def reorder(
        plan_id: int,
        data: EducationPlanModuleReorder,
        service: EducationPlanModuleService = Depends(get_service)
):
    try:
        return await service.reorder_plan(
            plan_id,
            data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# =========================
# Удалить модуль из плана
# =========================

@router.delete(
    "/plan/{plan_id}/module/{module_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить модуль из учебного плана",
    description="""
Удаляет связь между учебным планом
и выбранным модулем.

Сам модуль остается в системе.
""",
    response_description="Результат удаления",
    responses={
        404: {
            "description": "Связь не найдена"
        }
    }
)
async def remove_module(
        plan_id: int,
        module_id: int,
        service: EducationPlanModuleService = Depends(get_service)
):
    try:
        return await service.remove_module(
            plan_id,
            module_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# =========================
# Очистить весь план
# =========================

@router.delete(
    "/plan/{plan_id}",
    status_code=status.HTTP_200_OK,
    summary="Очистить учебный план",
    description="""
Удаляет все связи модулей
с выбранным учебным планом.

Модули не удаляются из системы.
""",
    response_description="Результат очистки",
    responses={
        404: {
            "description": "Учебный план не найден"
        }
    }
)
async def clear_plan(
        plan_id: int,
        service: EducationPlanModuleService = Depends(get_service)
):
    try:
        return await service.clear_plan(
            plan_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ---------------------------------------------
# =========================
# Количество модулей учебного плана
# =========================

@router.get(
    "/plan/{plan_id}/count",
    status_code=status.HTTP_200_OK,
    summary="Получить количество модулей",
    description="""
Возвращает количество модулей,
добавленных в выбранный учебный план.

Используется для отображения
структуры курса.
""",
    response_description="Количество модулей",
    responses={
        404: {
            "description": "Учебный план не найден"
        }
    }
)
async def count_modules(
        plan_id: int,
        service: EducationPlanModuleService = Depends(get_service)
):
    try:
        count = await service.count_modules(
            plan_id
        )

        return {
            "count": count
        }

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


# =========================
# PUT связь план-модуль
# =========================

@router.put(
    "/plan/{plan_id}/module/{module_id}",
    status_code=status.HTTP_200_OK,
    response_model=EducationPlanModuleResponse,
    summary="Полностью обновить связь план-модуль",
    description="""
Полное обновление связи между учебным планом и модулем.

Можно изменить:

- учебный план;
- модуль;
- порядок прохождения.

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
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
