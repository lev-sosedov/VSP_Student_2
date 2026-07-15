from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from academic_service.db.db_session import get_session
from academic_service.repositories.repository_module import ModuleRepository
from academic_service.services.service_module import ModuleService
from academic_service.schemas.schemas_module import (
    ModuleCreate,
    ModuleUpdate,
    ModulePatch,
    ModuleResponse,
    ModuleListResponse,
    ModuleFilter,
    ModuleArchive,
    ModuleActivate
)

router = APIRouter(
    prefix="/modules",
    tags=["Modules"]
)


# =========================
# DI
# =========================
# Получение сервиса
def get_service(session: AsyncSession = Depends(get_session)):
    return ModuleService(ModuleRepository(session))


# =========================
# Создать модуль
# =========================
@router.post(
    "",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание модуля",
    description="""
Создание нового учебного модуля.

Используется при создании:
- нового курса;
- новой программы обучения;
- нового учебного раздела.

Проверяет:
- уникальность названия модуля.
""",
    response_description="Созданный модуль",
    responses={
        400: {
            "description": "Модуль уже существует"
        },
        422: {
            "description": "Ошибка валидации"
        }
    }
)
async def create_module(
        data: ModuleCreate,
        service: ModuleService = Depends(get_service)
):
    try:

        return await service.create_module(data)

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =========================
# Получить модуль по ID
# =========================
@router.get(
    "/{module_id}",
    response_model=ModuleResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить модуль",
    description="""
Получение информации о модуле по его идентификатору.
""",
    response_description="Информация о модуле",
    responses={
        404: {
            "description": "Модуль не найден"
        }
    }
)
async def get_module(
        module_id: int,
        service: ModuleService = Depends(get_service)
):
    try:

        return await service.get_module_by_id(module_id)

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# =========================
# Получить список модулей
# =========================
@router.get(
    "",
    response_model=ModuleListResponse,
    status_code=status.HTTP_200_OK,
    summary="Список модулей",
    description="""
Получение списка модулей.

Поддерживает пагинацию:
- limit
- offset
""",
    response_description="Список модулей"
)
async def get_modules(
        limit: int = Query(
            20,
            ge=1,
            le=100
        ),
        offset: int = Query(
            0,
            ge=0
        ),
        service: ModuleService = Depends(get_service)
):
    modules = await service.get_modules(
        limit,
        offset
    )

    return {
        "items": modules,
        "total": len(modules)
    }


# =========================
# Полностью обновить модуль
# =========================
@router.put(
    "/{module_id}",
    response_model=ModuleResponse,
    status_code=status.HTTP_200_OK,
    summary="Полностью обновить модуль",
    description="""
Полное обновление данных модуля.

Все поля объекта заменяются новыми значениями.
""",
    response_description="Обновленный модуль",
    responses={
        404: {
            "description": "Модуль не найден"
        }
    }
)
async def update_module(
        module_id: int,
        data: ModuleUpdate,
        service: ModuleService = Depends(get_service)
):
    try:

        return await service.update_module(
            module_id,
            data
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# =========================
# Частично обновить модуль
# =========================
@router.patch(
    "/{module_id}",
    response_model=ModuleResponse,
    status_code=status.HTTP_200_OK,
    summary="Частично обновить модуль",
    description="""
Изменяет только переданные поля модуля.

Остальные поля остаются без изменений.
""",
    response_description="Обновленный модуль",
    responses={
        404: {
            "description": "Модуль не найден"
        }
    }
)
async def patch_module(
        module_id: int,
        data: ModulePatch,
        service: ModuleService = Depends(get_service)
):
    try:

        return await service.patch_module(
            module_id,
            data
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# =========================
# Безопасное удаление модуля
# =========================
@router.delete(
    "/{module_id}",
    status_code=status.HTTP_200_OK,
    summary="Удаление модуля",
    description="""
Безопасное удаление учебного модуля.

Перед удалением выполняются проверки:
- существует ли модуль;
- можно ли удалить объект;
- есть ли зависимости.

Используется для административной панели.
""",
    response_description="Результат удаления",
    responses={
        400: {
            "description": "Ошибка удаления модуля"
        },
        404: {
            "description": "Модуль не найден"
        }
    }
)
async def delete_module(
        module_id: int,
        service: ModuleService = Depends(get_service)
):
    try:

        return await service.safe_delete_module(
            module_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

#
# # =====================================================
#
#
# # =========================
# # Поиск по имени
# # =========================
# @router.get(
#     "/search",
#     response_model=list[ModuleResponse],
#     status_code=status.HTTP_200_OK,
#     summary="Поиск модулей",
#     description="""
# Поиск учебных модулей по названию.
#
# Примеры:
# - Python
# - Web-разработка
# - Основы дизайна
#
# Используется для быстрого поиска в административной панели.
# """,
#     response_description="Список найденных модулей"
# )
# async def search_modules(
#     name: str,
#     service: ModuleService = Depends(get_service)
# ):
#
#     return await service.repo.search(name)
#
#
#
# # =========================
# # Фильтр модулей
# # =========================
# @router.post(
#     "/filter",
#     response_model=list[ModuleResponse],
#     status_code=status.HTTP_200_OK,
#     summary="Фильтрация модулей",
#     description="""
# Фильтрация модулей по заданным параметрам.
#
# Позволяет получать:
# - активные модули;
# - архивные модули;
# - модули по дополнительным условиям.
#
# Используется в административной панели.
# """,
#     response_description="Список модулей после фильтрации"
# )
# async def filter_modules(
#     data: ModuleFilter,
#     service: ModuleService = Depends(get_service)
# ):
#
#     return await service.repo.filter(data)
#
#
#
# # =========================
# # Проверка использования модуля
# # =========================
# @router.get(
#     "/{module_id}/used",
#     include_in_schema=False,
#     summary="Проверка использования модуля",
#     description="""
# Проверяет, используется ли модуль
# в других сущностях системы.
#
# Подготовлено для будущей логики:
# - запрет удаления используемых модулей;
# - проверка связей перед удалением.
# """,
#     response_description="Статус использования модуля"
# )
# async def module_used(
#     module_id: int,
#     service: ModuleService = Depends(get_service)
# ):
#
#     return {
#         "used": await service.is_module_used(module_id)
#     }
#
#
#
# # =====================================================
#
#
# # =========================
# # Архивировать модуль
# # =========================
# @router.patch(
#     "/{module_id}/archive",
#     response_model=ModuleResponse,
#     status_code=status.HTTP_200_OK,
#     summary="Архивировать модуль",
#     description="""
# Переводит модуль в архив.
#
# Изменяет:
# - is_active = False;
# - дату закрытия.
#
# Модуль сохраняется в базе данных,
# но перестает использоваться в обучении.
# """,
#     response_description="Архивированный модуль",
#     responses={
#         404: {
#             "description": "Модуль не найден"
#         }
#     }
# )
# async def archive_module(
#     module_id: int,
#     data: ModuleArchive,
#     service: ModuleService = Depends(get_service)
# ):
#
#     module = await service.get_module_by_id(
#         module_id
#     )
#
#     module.is_active = False
#     module.closed_at = data.closed_at
#
#     return await service.repo.update(module)
#
#
#
# # =========================
# # Активировать модуль
# # =========================
# @router.patch(
#     "/{module_id}/activate",
#     response_model=ModuleResponse,
#     status_code=status.HTTP_200_OK,
#     summary="Активировать модуль",
#     description="""
# Возвращает архивный модуль в активное состояние.
#
# Используется когда модуль снова требуется
# в образовательном процессе.
# """,
#     response_description="Активированный модуль",
#     responses={
#         404: {
#             "description": "Модуль не найден"
#         }
#     }
# )
# async def activate_module(
#     module_id: int,
#     data: ModuleActivate,
#     service: ModuleService = Depends(get_service)
# ):
#
#     return await service.activate_module(
#         module_id
#     )
