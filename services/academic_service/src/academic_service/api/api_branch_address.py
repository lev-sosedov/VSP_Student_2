from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from academic_service.db.session import get_session
from academic_service.repositories.repository_branch_address import BranchAddressRepository
from academic_service.services.service_branch_address import BranchAddressService

from academic_service.schemas.schemas_branch_address import (
    BranchAddressCreate,
    BranchAddressUpdate,
    BranchAddressPatch,
    BranchAddressFilter,
)

router = APIRouter(prefix="/branch-address",tags=["Branch Address"],)


# =====================================================
# Dependency Injection
# =====================================================

def get_service(session: AsyncSession = Depends(get_session),):
    repo = BranchAddressRepository(session)
    return BranchAddressService(repo)


# =====================================================
# Создать адрес
# =====================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Создание адреса филиала",
    description="""
Создает новый адрес филиала.

Используется администраторами при создании филиалов.

После создания адрес может быть привязан к одному или нескольким филиалам.
""",
    response_description="Созданный адрес филиала",
    responses={
        201: {
            "description": "Адрес успешно создан"
        },
        422: {
            "description": "Ошибка валидации данных"
        }
    }
)
async def create_address(data: BranchAddressCreate,service: BranchAddressService = Depends(get_service)):
    try:
        return await service.create_address(data)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# Получить адрес по ID
# =====================================================

@router.get(
    "/{address_id}",
    status_code=status.HTTP_200_OK,
    summary="Получить адрес по ID",
    description="""
Возвращает адрес филиала по его идентификатору.
""",
    response_description="Адрес филиала",
    responses={
        404: {
            "description": "Адрес не найден"
        }
    }
)
async def get_address(
    address_id: int,
    service: BranchAddressService = Depends(get_service)
):

    try:

        return await service.get_address(address_id)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# Список адресов
# =====================================================

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Получить список адресов",
    description="""
Возвращает список адресов филиалов.

Поддерживает пагинацию:

- limit
- offset
""",
    response_description="Список адресов"
)
async def get_addresses(
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Количество записей"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Смещение"
    ),
    service: BranchAddressService = Depends(get_service)
):

    try:

        return await service.get_addresses(limit, offset)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# Полное обновление адреса PUT
# =====================================================

@router.put(
    "/{address_id}",
    status_code=status.HTTP_200_OK,
    summary="Полностью обновить адрес",
    description="""
Полностью заменяет адрес филиала.

Все поля обязательны.
""",
    response_description="Обновленный адрес",
    responses={
        404: {
            "description": "Адрес не найден"
        }
    }
)
async def update_address(
    address_id: int,
    data: BranchAddressUpdate,
    service: BranchAddressService = Depends(get_service)
):

    try:

        return await service.update_address(address_id, data)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# Частичное обновление адреса PATCH
# =====================================================

@router.patch(
    "/{address_id}",
    status_code=status.HTTP_200_OK,
    summary="Частично обновить адрес",
    description="""
Изменяет только переданные поля.

Можно обновить одно или несколько полей адреса.
""",
    response_description="Обновленный адрес",
    responses={
        404: {
            "description": "Адрес не найден"
        }
    }
)
async def patch_address(
    address_id: int,
    data: BranchAddressPatch,
    service: BranchAddressService = Depends(get_service)
):

    try:

        return await service.patch_address(address_id, data)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================================================
# Удалить адрес
# =====================================================

@router.delete(
    "/{address_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить адрес филиала",
    description="""
Удаляет адрес филиала.

Если адрес используется филиалом, удаление может быть запрещено.
""",
    response_description="Результат удаления",
    responses={
        404: {
            "description": "Адрес не найден"
        }
    }
)
async def delete_address(
    address_id: int,
    service: BranchAddressService = Depends(get_service)
):

    try:

        return await service.delete_address(address_id)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

#
# # =====================================================
# # Поиск адресов по началу слова
# # =====================================================
#
# @router.get(
#     "/search/{query}",
#     status_code=status.HTTP_200_OK,
#     summary="Поиск адресов",
#     description="""
# Поиск адресов по совпадению строки.
#
# Поиск выполняется по:
#
# - стране
# - городу
# - улице
# """,
#     response_description="Найденные адреса"
# )
# async def search(
#     query: str,
#     service: BranchAddressService = Depends(get_service)
# ):
#
#     try:
#
#         return await service.search(query)
#
#     except HTTPException:
#         raise
#
#     except Exception as e:
#
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
#
#
# # =====================================================
# # Поиск по стране
# # =====================================================
#
# @router.get(
#     "/country/{country}",
#     status_code=status.HTTP_200_OK,
#     summary="Получить адреса по стране",
#     description="""
# Возвращает все адреса указанной страны.
# """,
#     response_description="Список адресов"
# )
# async def get_by_country(
#     country: str,
#     service: BranchAddressService = Depends(get_service)
# ):
#
#     try:
#
#         return await service.get_by_country(country)
#
#     except HTTPException:
#         raise
#
#     except Exception as e:
#
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
#
#
# # =====================================================
# # Поиск по городу
# # =====================================================
#
# @router.get(
#     "/city/{city}",
#     status_code=status.HTTP_200_OK,
#     summary="Получить адреса по городу",
#     description="""
# Возвращает все адреса указанного города.
# """,
#     response_description="Список адресов"
# )
# async def get_by_city(
#     city: str,
#     service: BranchAddressService = Depends(get_service)
# ):
#
#     try:
#
#         return await service.get_by_city(city)
#
#     except HTTPException:
#         raise
#
#     except Exception as e:
#
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
#
#
# # =====================================================
# # Фильтр (гибкий)
# # =====================================================
#
# @router.post(
#     "/filter",
#     status_code=status.HTTP_200_OK,
#     summary="Фильтрация адресов",
#     description="""
# Гибкий поиск адресов.
#
# Можно фильтровать по:
#
# - стране
# - городу
# - улице
# - дому
# - корпусу
# - почтовому индексу
#
# Допускается использование сразу нескольких параметров.
# """,
#     response_description="Список найденных адресов"
# )
# async def filter_addresses(
#     filters: BranchAddressFilter,
#     service: BranchAddressService = Depends(get_service)
# ):
#
#     try:
#
#         return await service.filter(filters)
#
#     except HTTPException:
#         raise
#
#     except Exception as e:
#
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
#
#
# # =====================================================
# # Красивый формат адреса
# # =====================================================
#
# @router.get(
#     "/{address_id}/full",
#     status_code=status.HTTP_200_OK,
#     summary="Получить полный адрес",
#     description="""
# Возвращает адрес в красивом текстовом формате.
#
# Например:
#
# Россия, Краснодар, ул. Красная, 25.
# """,
#     response_description="Полный адрес"
# )
# async def get_full_address(
#     address_id: int,
#     service: BranchAddressService = Depends(get_service)
# ):
#
#     try:
#
#         return {
#             "address": await service.get_full_address(address_id)
#         }
#
#     except HTTPException:
#         raise
#
#     except Exception as e:
#
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )