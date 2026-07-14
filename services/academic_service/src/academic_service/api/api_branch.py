from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from academic_service.services.service_branch import BranchService
from academic_service.repositories.repository_branch import BranchRepository
from academic_service.repositories.repository_branch_address import BranchAddressRepository

from academic_service.schemas.schemas_branch import (
    BranchCreate,
    BranchUpdate,
    BranchPatch,
    BranchFilter,
    BranchActivate,
    BranchClose
)

from academic_service.schemas.schemas_branch_address import BranchAddressUpdate
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
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Создание филиала",
    description="""
Создание нового филиала.

Во время создания:

- создается филиал;
- привязывается существующий адрес;
- сохраняются контакты филиала.

Используется администраторами системы.
""",
    response_description="Созданный филиал",
    responses={
        201: {
            "description": "Филиал успешно создан"
        },
        400: {
            "description": "Ошибка создания филиала"
        },
        422: {
            "description": "Ошибка валидации"
        }
    }
)
async def create_branch(
        data: BranchCreate,
        service: BranchService = Depends(get_service)
):
    try:
        return await service.create_branch(data)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Получить филиал по ID
# =========================
@router.get(
    "/{branch_id}",
    status_code=status.HTTP_200_OK,
    summary="Получить филиал",
    description="""
Получение филиала по идентификатору.

Возвращает:

- информацию о филиале;
- телефон;
- email;
- статус активности.
""",
    response_description="Информация о филиале",
    responses={
        404: {
            "description": "Филиал не найден"
        }
    }
)
async def get_branch(
        branch_id: int,
        service: BranchService = Depends(get_service)
):
    try:
        return await service.get_branch(branch_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Список филиалов
# =========================
@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Получить список филиалов",
    description="""
Возвращает список филиалов.

По умолчанию отображаются только активные филиалы.

Можно получить также все филиалы.
""",
    response_description="Список филиалов"
)
async def get_branches(
        active_only: bool = True,
        service: BranchService = Depends(get_service)
):
    try:
        return await service.get_branches(active_only)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Обновить филиал (PUT)
# =========================
@router.put(
    "/{branch_id}",
    status_code=status.HTTP_200_OK,
    summary="Полностью обновить филиал",
    description="""
Полное обновление данных филиала.

Можно изменить:

- адрес;
- телефон;
- email.

Используется администраторами.
""",
    response_description="Обновленный филиал",
    responses={
        404: {
            "description": "Филиал не найден"
        }
    }
)
async def update_branch(
        branch_id: int,
        data: BranchUpdate,
        service: BranchService = Depends(get_service)
):
    try:
        return await service.update_branch(branch_id, data)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# PATCH филиал
# =========================
@router.patch(
    "/{branch_id}",
    status_code=status.HTTP_200_OK,
    summary="Частично обновить филиал",
    description="""
Частичное изменение информации о филиале.

Передаются только изменяемые поля.
""",
    response_description="Обновленный филиал",
    responses={
        404: {
            "description": "Филиал не найден"
        }
    }
)
async def patch_branch(
        branch_id: int,
        data: BranchPatch,
        service: BranchService = Depends(get_service)
):
    try:
        return await service.patch_branch(branch_id, data)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# Удалить филиал
# =========================
@router.delete(
    "/{branch_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить филиал",
    description="""
Удаление филиала из системы.

Используется администраторами.
""",
    response_description="Результат удаления",
    responses={
        404: {
            "description": "Филиал не найден"
        }
    }
)
async def delete_branch(
        branch_id: int,
        service: BranchService = Depends(get_service)
):
    try:
        return await service.delete_branch(branch_id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# --------------------------------------------------------------
#
#
# # =========================
# # Детальный филиал
# # =========================
# @router.get(
#     "/{branch_id}/detail",
#     status_code=status.HTTP_200_OK,
#     summary="Получить подробную информацию о филиале",
#     description="""
# Возвращает подробную информацию.
#
# Включает:
#
# - данные филиала;
# - адрес филиала.
# """,
#     response_description="Подробная информация о филиале",
#     responses={
#         404: {
#             "description": "Филиал не найден"
#         }
#     }
# )
# async def get_branch_detail(
#         branch_id: int,
#         service: BranchService = Depends(get_service)
# ):
#     try:
#         return await service.get_branch_detail(branch_id)
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
# # Поиск филиалов по стране
# # =========================
# @router.get(
#     "/country/{country}",
#     status_code=status.HTTP_200_OK,
#     summary="Поиск филиалов по стране",
#     description="""
# Возвращает список филиалов,
# расположенных в указанной стране.
# """,
#     response_description="Список филиалов"
# )
# async def get_by_country(
#         country: str,
#         service: BranchService = Depends(get_service)
# ):
#     try:
#         return await service.get_by_country(country)
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
# # Поиск филиалов по городу
# # =========================
# @router.get(
#     "/city/{city}",
#     status_code=status.HTTP_200_OK,
#     summary="Получить филиалы по городу",
#     description="""
# Возвращает список филиалов,
# расположенных в указанном городе.
#
# Используется:
# - выбор филиала
# - поиск филиалов
# - мобильное приложение
# """,
#     response_description="Список филиалов",
#     responses={
#         200: {"description": "Список филиалов"},
#         404: {"description": "Филиалы не найдены"}
#     }
# )
# async def get_by_city(
#         city: str,
#         service: BranchService = Depends(get_service)
# ):
#     try:
#         return await service.get_by_city(city)
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
# # Закрыть филиал
# # =========================
# @router.post(
#     "/{branch_id}/close",
#     status_code=status.HTTP_200_OK,
#     summary="Закрыть филиал",
#     description="""
# Переводит филиал в неактивное состояние.
#
# Используется:
# - закрытие филиала
# - скрытие филиала из списка
# """,
#     response_description="Филиал закрыт",
#     responses={
#         404: {"description": "Филиал не найден"}
#     }
# )
# async def close_branch(
#         branch_id: int,
#         data: BranchClose,
#         service: BranchService = Depends(get_service)
# ):
#     try:
#         return await service.close_branch(branch_id)
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
# # Активировать филиал
# # =========================
# @router.post(
#     "/{branch_id}/activate",
#     status_code=status.HTTP_200_OK,
#     summary="Активировать филиал",
#     description="""
# Возвращает филиал в рабочее состояние.
#
# Используется:
# - повторное открытие филиала
# """,
#     response_description="Филиал активирован",
#     responses={
#         404: {"description": "Филиал не найден"}
#     }
# )
# async def activate_branch(
#         branch_id: int,
#         data: BranchActivate,
#         service: BranchService = Depends(get_service)
# ):
#     try:
#         return await service.restore_branch(branch_id)
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
# # Получить адрес филиала
# # =========================
# @router.get(
#     "/{branch_id}/address",
#     status_code=status.HTTP_200_OK,
#     summary="Получить адрес филиала",
#     description="""
# Возвращает адрес,
# привязанный к филиалу.
#
# Используется:
# - карточка филиала
# - отображение адреса
# """,
#     response_description="Адрес филиала",
#     responses={
#         404: {"description": "Филиал не найден"}
#     }
# )
# async def get_address(
#         branch_id: int,
#         service: BranchService = Depends(get_service)
# ):
#     try:
#         return await service.get_address(branch_id)
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
# # Обновить адрес филиала
# # =========================
# @router.put(
#     "/{branch_id}/address",
#     status_code=status.HTTP_200_OK,
#     summary="Обновить адрес филиала",
#     description="""
# Полностью обновляет
# адрес выбранного филиала.
#
# Используется:
# - изменение адреса
# - перенос филиала
# """,
#     response_description="Обновленный адрес",
#     responses={
#         404: {"description": "Филиал не найден"},
#         422: {"description": "Ошибка валидации"}
#     }
# )
# async def update_address(
#         branch_id: int,
#         data: BranchAddressUpdate,
#         service: BranchService = Depends(get_service)
# ):
#     try:
#         return await service.update_address(branch_id, data)
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
# # Статистика филиалов
# # =========================
# @router.get(
#     "/stats/active-count",
#     status_code=status.HTTP_200_OK,
#     summary="Количество активных филиалов",
#     description="""
# Возвращает количество
# активных филиалов.
#
# Используется:
# - админ-панель
# - статистика
# """,
#     response_description="Количество активных филиалов"
# )
# async def count_active(
#         service: BranchService = Depends(get_service)
# ):
#     try:
#         return {"active": await service.count_active()}
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
# # Короткий список филиалов
# # =========================
# @router.get(
#     "/short",
#     status_code=status.HTTP_200_OK,
#     summary="Краткий список филиалов",
#     description="""
# Возвращает сокращенный список филиалов.
#
# Используется:
# - выпадающие списки
# - выбор филиала
# """,
#     response_description="Краткий список филиалов"
# )
# async def short_list(
#         service: BranchService = Depends(get_service)
# ):
#     try:
#         return await service.get_short_list()
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
# # Фильтрация филиалов
# # =========================
# @router.post(
#     "/filter",
#     status_code=status.HTTP_200_OK,
#     summary="Фильтр филиалов",
#     description="""
# Поиск филиалов
# по различным параметрам.
#
# Можно фильтровать:
# - город
# - активность
#
# Используется:
# - поиск
# - админ-панель
# """,
#     response_description="Список найденных филиалов",
#     responses={
#         422: {"description": "Ошибка валидации"}
#     }
# )
# async def filter_branches(
#         filters: BranchFilter,
#         service: BranchService = Depends(get_service)
# ):
#     try:
#         if filters.city:
#             return await service.get_by_city(filters.city)
#
#         return await service.get_branches(
#             active_only=filters.is_active if filters.is_active is not None else True
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
