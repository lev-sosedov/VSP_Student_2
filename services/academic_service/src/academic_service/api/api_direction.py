from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

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

from academic_service.db.db_session import get_session

router = APIRouter(
    prefix="/directions",
    tags=["Directions"]
)


# =========================
# DI
# =========================
def get_service(session: AsyncSession = Depends(get_session)):
    return DirectionService(
        DirectionRepository(session),
        EducationPlanRepository(session)
    )


# =========================
# Создать направление
# =========================
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Создание направления",
    description="""
Создание нового направления обучения.

Во время создания:

- создается направление;
- сохраняется описание;
- направление становится активным.

Используется администраторами системы.
""",
    response_description="Созданное направление",
    responses={
        201: {
            "description": "Направление успешно создано"
        },
        400: {
            "description": "Ошибка создания направления"
        },
        422: {
            "description": "Ошибка валидации"
        }
    }
)
async def create_direction(
        data: DirectionCreate,
        service: DirectionService = Depends(get_service)
):
    try:
        return await service.create_direction(data)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Получить направление по ID
# =========================
@router.get(
    "/{direction_id}",
    status_code=status.HTTP_200_OK,
    summary="Получить направление",
    description="""
Получение направления по идентификатору.

Возвращает:

- название направления;
- описание;
- статус активности.
""",
    response_description="Информация о направлении",
    responses={
        404: {
            "description": "Направление не найдено"
        }
    }
)
async def get_direction(
        direction_id: int,
        service: DirectionService = Depends(get_service)
):
    try:
        return await service.get_by_id(direction_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Список направлений
# =========================
@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Получить список направлений",
    description="""
Возвращает список направлений.

Поддерживается постраничная навигация
через параметры limit и offset.
""",
    response_description="Список направлений"
)
async def get_directions(
        limit: int = Query(20),
        offset: int = Query(0),
        service: DirectionService = Depends(get_service)
):
    try:
        return await service.get_all(
            limit,
            offset
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Обновить направление (PUT)
# =========================
@router.put(
    "/{direction_id}",
    status_code=status.HTTP_200_OK,
    summary="Полностью обновить направление",
    description="""
Полное обновление данных направления.

Можно изменить:

- название;
- описание;
- остальные основные поля.

Используется администраторами.
""",
    response_description="Обновленное направление",
    responses={
        404: {
            "description": "Направление не найдено"
        }
    }
)
async def update_direction(
        direction_id: int,
        data: DirectionUpdate,
        service: DirectionService = Depends(get_service)
):
    try:
        return await service.update(
            direction_id,
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
# PATCH направление
# =========================
@router.patch(
    "/{direction_id}",
    status_code=status.HTTP_200_OK,
    summary="Частично обновить направление",
    description="""
Частичное изменение информации о направлении.

Передаются только изменяемые поля.
""",
    response_description="Обновленное направление",
    responses={
        404: {
            "description": "Направление не найдено"
        }
    }
)
async def patch_direction(
        direction_id: int,
        data: DirectionPatch,
        service: DirectionService = Depends(get_service)
):
    try:
        return await service.patch(
            direction_id,
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
# Удалить направление
# =========================
@router.delete(
    "/{direction_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить направление",
    description="""
Удаление направления из системы.

Используется администраторами.
""",
    response_description="Результат удаления",
    responses={
        404: {
            "description": "Направление не найдено"
        }
    }
)
async def delete_direction(
        direction_id: int,
        service: DirectionService = Depends(get_service)
):
    try:
        return await service.safe_delete(
            direction_id
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# # ---------------------------------------------------------------------------------
# # =========================
# # Фильтр направлений
# # =========================
# @router.post(
#     "/filter",
#     status_code=status.HTTP_200_OK,
#     response_model=list[DirectionResponse],
#     summary="Фильтр направлений",
#     description="""
# Поиск направлений по заданным параметрам.
#
# Можно фильтровать по:
#
# - названию;
# - активности;
# - дате создания;
# - другим доступным полям.
#
# Используется в административной панели.
# """,
#     response_description="Список найденных направлений"
# )
# async def filter_directions(
#         filters: DirectionFilter,
#         service: DirectionService = Depends(get_service)
# ):
#     try:
#         return await service.filter_directions(filters)
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
# # Получить направление с учебными планами
# # =========================
# @router.get(
#     "/{direction_id}/plans",
#     status_code=status.HTTP_200_OK,
#     summary="Получить направление с учебными планами",
#     description="""
# Возвращает направление вместе со всеми связанными учебными планами.
#
# Используется при просмотре структуры обучения.
# """,
#     response_description="Направление и связанные учебные планы",
#     responses={
#         404: {
#             "description": "Направление не найдено"
#         }
#     }
# )
# async def get_direction_with_plans(
#         direction_id: int,
#         service: DirectionService = Depends(get_service)
# ):
#     try:
#         return await service.get_direction_with_plans(direction_id)
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
# # Поиск направлений
# # =========================
# @router.get(
#     "/search",
#     status_code=status.HTTP_200_OK,
#     summary="Поиск направлений",
#     description="""
# Поиск направлений по части названия.
#
# Используется при выборе направления в интерфейсе.
# """,
#     response_description="Список найденных направлений"
# )
# async def search_direction(
#         q: str,
#         service: DirectionService = Depends(get_service)
# ):
#     try:
#         return await service.search(q)
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
# # Закрыть направление
# # =========================
# @router.post(
#     "/{direction_id}/close",
#     status_code=status.HTTP_200_OK,
#     response_model=DirectionResponse,
#     summary="Закрыть направление",
#     description="""
# Переводит направление в архив.
#
# После закрытия направление становится неактивным и недоступным для новых учебных планов.
# """,
#     response_description="Закрытое направление",
#     responses={
#         404: {
#             "description": "Направление не найдено"
#         }
#     }
# )
# async def close_direction(
#         direction_id: int,
#         service: DirectionService = Depends(get_service)
# ):
#     try:
#         return await service.close_direction(direction_id)
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
# # Активировать направление
# # =========================
# @router.post(
#     "/{direction_id}/activate",
#     status_code=status.HTTP_200_OK,
#     response_model=DirectionResponse,
#     summary="Активировать направление",
#     description="""
# Повторно открывает ранее закрытое направление.
#
# После активации направление снова становится доступным для использования.
# """,
#     response_description="Активированное направление",
#     responses={
#         404: {
#             "description": "Направление не найдено"
#         }
#     }
# )
# async def activate_direction(
#         direction_id: int,
#         service: DirectionService = Depends(get_service)
# ):
#     try:
#         return await service.activate_direction(direction_id)
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
# # Детальная информация о направлении
# # =========================
# @router.get(
#     "/{direction_id}/detail",
#     status_code=status.HTTP_200_OK,
#     response_model=DirectionDetailResponse,
#     summary="Получить подробную информацию о направлении",
#     description="""
# Возвращает расширенную информацию о направлении.
#
# Может включать:
#
# - основные данные;
# - статистику;
# - связанные сущности;
# - дополнительную информацию.
#
# Используется в административной панели.
# """,
#     response_description="Подробная информация о направлении",
#     responses={
#         404: {
#             "description": "Направление не найдено"
#         }
#     }
# )
# async def get_direction_detail(
#         direction_id: int,
#         service: DirectionService = Depends(get_service)
# ):
#     try:
#         return await service.get_direction_detail(direction_id)
#
#     except HTTPException:
#         raise
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
