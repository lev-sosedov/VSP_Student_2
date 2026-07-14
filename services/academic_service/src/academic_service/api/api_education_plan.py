from fastapi import APIRouter, Depends, HTTPException, Query, status
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


router = APIRouter(prefix="/education-plans",tags=["Education Plans"])


# =========================
# DI
# =========================
def get_service(session: AsyncSession = Depends(get_session)):
    return EducationPlanService(
        EducationPlanRepository(session),
        DirectionRepository(session),
        EducationPlanModuleRepository(session),
        ModuleRepository(session))


# =========================
# Создать учебный план
# =========================
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Создание учебного плана",
    description="""
Создание нового учебного плана.

Во время создания:

- проверяется существование направления;
- проверяется активность направления;
- создается программа обучения.

Используется администраторами системы.
""",
    response_description="Созданный учебный план",
    responses={
        201: {
            "description": "Учебный план успешно создан"
        },
        400: {
            "description": "Ошибка создания учебного плана"
        },
        422: {
            "description": "Ошибка валидации данных"
        }
    }
)
async def create_plan(
        data: EducationPlanCreate,
        service: EducationPlanService = Depends(get_service)
):
    try:
        return await service.create_education_plan(data)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Получить учебный план по ID
# =========================
@router.get(
    "/{plan_id}",
    status_code=status.HTTP_200_OK,
    response_model=EducationPlanResponse,
    summary="Получить учебный план",
    description="""
Получение учебного плана по идентификатору.

Возвращает:

- название плана;
- направление обучения;
- длительность;
- количество занятий;
- статус активности.
""",
    response_description="Информация об учебном плане",
    responses={
        404: {
            "description": "Учебный план не найден"
        }
    }
)
async def get_plan(
        plan_id: int,
        service: EducationPlanService = Depends(get_service)
):
    try:
        return await service.get_plan_by_id(plan_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Список учебных планов
# =========================
@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=EducationPlanListResponse,
    summary="Получить список учебных планов",
    description="""
Возвращает список учебных планов.

Поддерживается пагинация:

- limit — количество записей;
- offset — смещение.
""",
    response_description="Список учебных планов"
)
async def get_plans(
        limit: int = Query(20, ge=1),
        offset: int = Query(0, ge=0),
        service: EducationPlanService = Depends(get_service)
):
    try:
        plans = await service.get_all(
            limit,
            offset
        )

        return {
            "items": plans,
            "total": len(plans)
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Полное обновление учебного плана
# =========================
@router.put(
    "/{plan_id}",
    status_code=status.HTTP_200_OK,
    response_model=EducationPlanResponse,
    summary="Полностью обновить учебный план",
    description="""
Полное обновление данных учебного плана.

Можно изменить:

- направление;
- название;
- срок обучения;
- количество занятий в неделю.
""",
    response_description="Обновленный учебный план",
    responses={
        404: {
            "description": "Учебный план не найден"
        }
    }
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

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# PATCH учебного плана
# =========================
@router.patch(
    "/{plan_id}",
    status_code=status.HTTP_200_OK,
    response_model=EducationPlanResponse,
    summary="Частично обновить учебный план",
    description="""
Частичное изменение учебного плана.

Передаются только изменяемые поля.
""",
    response_description="Обновленный учебный план",
    responses={
        404: {
            "description": "Учебный план не найден"
        }
    }
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

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Удалить учебный план
# =========================
@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить учебный план",
    description="""
Удаление учебного плана.

Удаление возможно только если план
не используется другими объектами системы.
""",
    response_description="Результат удаления",
    responses={
        404: {
            "description": "Учебный план не найден"
        },
        400: {
            "description": "План невозможно удалить"
        }
    }
)
async def delete_plan(
        plan_id: int,
        service: EducationPlanService = Depends(get_service)
):
    try:
        return await service.delete_plan(plan_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# # ---------------------------------------------------
#
# # =========================
# # Получить активные планы
# # =========================
# @router.get(
#     "/active",
#     status_code=status.HTTP_200_OK,
#     response_model=list[EducationPlanResponse],
#     summary="Получить активные учебные планы",
#     description="""
# Возвращает список активных учебных планов.
#
# Активные планы доступны для назначения студентам.
# """,
#     response_description="Список активных учебных планов",
# )
# async def get_active_plans(
#         service: EducationPlanService = Depends(get_service)
# ):
#     try:
#         return await service.plan_repo.get_active()
#
#     except HTTPException:
#         raise
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
#
#
# # =========================
# # Получить закрытые планы
# # =========================
# @router.get(
#     "/closed",
#     status_code=status.HTTP_200_OK,
#     response_model=list[EducationPlanResponse],
#     summary="Получить закрытые учебные планы",
#     description="""
# Возвращает учебные планы, которые были закрыты.
#
# Закрытые планы сохраняются в истории и не используются
# для новых групп.
# """,
#     response_description="Список закрытых учебных планов",
# )
# async def get_closed_plans(
#         service: EducationPlanService = Depends(get_service)
# ):
#     try:
#         return await service.plan_repo.get_closed()
#
#     except HTTPException:
#         raise
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
#
#
# # =========================
# # Фильтр учебных планов
# # =========================
# @router.post(
#     "/filter",
#     status_code=status.HTTP_200_OK,
#     response_model=list[EducationPlanResponse],
#     summary="Фильтрация учебных планов",
#     description="""
# Поиск учебных планов по параметрам.
#
# Можно фильтровать:
#
# - направление обучения;
# - длительность курса;
# - активность плана.
# """,
#     response_description="Отфильтрованный список учебных планов",
#     responses={
#         422: {
#             "description": "Ошибка валидации данных"
#         }
#     }
# )
# async def filter_plans(
#         data: EducationPlanFilter,
#         service: EducationPlanService = Depends(get_service)
# ):
#     try:
#         return await service.plan_repo.filter(
#             direction_id=data.direction_id,
#             duration_months=data.duration_months,
#             is_active=data.is_active
#         )
#
#     except HTTPException:
#         raise
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
#
#
# # =========================
# # Получить структуру учебного плана
# # =========================
# @router.get(
#     "/{plan_id}/structure",
#     status_code=status.HTTP_200_OK,
#     summary="Получить структуру учебного плана",
#     description="""
# Возвращает список модулей,
# входящих в учебный план.
#
# Включает:
#
# - модули;
# - порядок прохождения;
# - связь с учебным планом.
# """,
#     response_description="Структура учебного плана",
#     responses={
#         404: {
#             "description": "Учебный план не найден"
#         }
#     }
# )
# async def get_structure(
#         plan_id: int,
#         service: EducationPlanService = Depends(get_service)
# ):
#     try:
#         return await service.get_modules(plan_id)
#
#     except HTTPException:
#         raise
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
#
#
# # =========================
# # Активировать учебный план
# # =========================
# @router.patch(
#     "/{plan_id}/activate",
#     status_code=status.HTTP_200_OK,
#     response_model=EducationPlanResponse,
#     summary="Активировать учебный план",
#     description="""
# Активирует закрытый учебный план.
#
# После активации:
#
# - план становится доступным;
# - дата закрытия очищается.
# """,
#     response_description="Активированный учебный план",
#     responses={
#         404: {
#             "description": "Учебный план не найден"
#         }
#     }
# )
# async def activate_plan(
#         plan_id: int,
#         data: EducationPlanActivate,
#         service: EducationPlanService = Depends(get_service)
# ):
#     try:
#         plan = await service.get_plan_by_id(plan_id)
#
#         plan.is_active = True
#         plan.closed_at = None
#
#         return await service.plan_repo.update(
#             plan_id,
#             {
#                 "is_active": True,
#                 "closed_at": None
#             }
#         )
#
#     except HTTPException:
#         raise
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
