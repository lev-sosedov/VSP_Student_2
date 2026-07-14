from fastapi import APIRouter, Depends, Query,HTTPException, status

from academic_service.services.service_group import GroupService
from academic_service.schemas.schemas_group import (
    GroupCreate,
    GroupUpdate,
    GroupPatch,
    GroupResponse,
    GroupDetailResponse,
    GroupListResponse,
    GroupExistsResponse
)

from academic_service.core.dependencies import get_group_service

router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)


# =========================
# Создание группы
# =========================

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=GroupResponse,
    summary="Создать группу",
    description="""
Создает новую учебную группу.

Перед созданием проверяется:

- существование филиала;
- существование направления;
- существование учебного плана;
- отсутствие группы с таким названием.
""",
    response_description="Созданная группа",
    responses={
        400: {
            "description": "Некорректные данные или группа уже существует"
        },
        422: {
            "description": "Ошибка валидации данных"
        },
        500: {
            "description": "Внутренняя ошибка сервера"
        }
    }
)
async def create_group(
        data: GroupCreate,
        service: GroupService = Depends(get_group_service)
):
    return await service.create_group(data)


# =========================
# Получить группу
# =========================

@router.get(
    "/{group_id}",
    status_code=status.HTTP_200_OK,
    response_model=GroupResponse,
    summary="Получить группу",
    description="""
Возвращает группу по её идентификатору.
""",
    response_description="Информация о группе",
    responses={
        404: {
            "description": "Группа не найдена"
        },
        500: {
            "description": "Внутренняя ошибка сервера"
        }
    }
)
async def get_group(
        group_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.get_group(group_id)


# =========================
# Список групп
# =========================

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=GroupListResponse,
    summary="Получить список групп",
    description="""
Возвращает список всех учебных групп.

Поддерживается постраничный вывод.
""",
    response_description="Список групп",
    responses={
        500: {
            "description": "Внутренняя ошибка сервера"
        }
    }
)
async def get_groups(
        limit: int = Query(
            20,
            ge=1,
            description="Количество записей"
        ),
        offset: int = Query(
            0,
            ge=0,
            description="Смещение"
        ),
        service: GroupService = Depends(get_group_service)
):
    groups = await service.get_groups(
        limit=limit,
        offset=offset
    )

    return {
        "items": groups,
        "total": len(groups)
    }


# =========================
# Полное обновление группы
# =========================

@router.put(
    "/{group_id}",
    status_code=status.HTTP_200_OK,
    response_model=GroupResponse,
    summary="Полностью обновить группу",
    description="""
Полностью обновляет данные учебной группы.

Можно изменить:

- название;
- филиал;
- направление;
- учебный план;
- даты обучения.
""",
    response_description="Обновленная группа",
    responses={
        404: {
            "description": "Группа не найдена"
        },
        422: {
            "description": "Ошибка валидации данных"
        },
        500: {
            "description": "Внутренняя ошибка сервера"
        }
    }
)
async def update_group(
        group_id: int,
        data: GroupUpdate,
        service: GroupService = Depends(get_group_service)
):
    return await service.update_group(
        group_id,
        data
    )


# =========================
# Частичное обновление группы
# =========================

@router.patch(
    "/{group_id}",
    status_code=status.HTTP_200_OK,
    response_model=GroupResponse,
    summary="Частично обновить группу",
    description="""
Позволяет изменить только переданные поля группы.

Например:

- название;
- даты обучения;
- филиал;
- направление;
- учебный план.
""",
    response_description="Обновленная группа",
    responses={
        404: {
            "description": "Группа не найдена"
        },
        422: {
            "description": "Ошибка валидации данных"
        },
        500: {
            "description": "Внутренняя ошибка сервера"
        }
    }
)
async def patch_group(
        group_id: int,
        data: GroupPatch,
        service: GroupService = Depends(get_group_service)
):
    return await service.patch_group(
        group_id,
        data
    )


# =========================
# Удаление группы
# =========================

@router.delete(
    "/{group_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить группу",
    description="""
Полностью удаляет группу из базы данных.
""",
    response_description="Группа успешно удалена",
    responses={
        404: {
            "description": "Группа не найдена"
        },
        500: {
            "description": "Внутренняя ошибка сервера"
        }
    }
)
async def delete_group(
        group_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.delete_group(group_id)


# =========================
# Безопасное удаление группы
# =========================

@router.delete(
    "/{group_id}/safe",
    status_code=status.HTTP_200_OK,
    summary="Безопасное удаление группы",
    description="""
Выполняет безопасное удаление группы.

Используется, если необходимо предварительно проверить возможность удаления или выполнить дополнительные проверки.
""",
    response_description="Группа успешно удалена",
    responses={
        404: {
            "description": "Группа не найдена"
        },
        500: {
            "description": "Внутренняя ошибка сервера"
        }
    }
)
async def safe_delete_group(
        group_id: int,
        service: GroupService = Depends(get_group_service)
):
    return await service.safe_delete_group(group_id)
# ----------------------------------------------------------
# =========================
# Детальная информация о группе
# =========================
@router.get(
    "/{group_id}/detail",
    status_code=status.HTTP_200_OK,
    response_model=GroupDetailResponse,
    summary="Получить подробную информацию о группе",
    description="""
Возвращает полную информацию о группе.

Содержит сведения о группе, филиале,
направлении обучения и учебном плане.
""",
    response_description="Подробная информация о группе",
    responses={
        404: {"description": "Группа не найдена"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_group_detail(
    group_id: int,
    service: GroupService = Depends(get_group_service),
):
    try:
        return await service.get_group_details(group_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# =========================
# Активные группы
# =========================
@router.get(
    "/active/list",
    status_code=status.HTTP_200_OK,
    response_model=list[GroupResponse],
    summary="Получить активные группы",
    description="""
Возвращает список всех активных учебных групп.
""",
    response_description="Список активных групп",
)
async def get_active_groups(
    service: GroupService = Depends(get_group_service),
):
    return await service.get_active_groups()


# =========================
# Закрытые группы
# =========================
@router.get(
    "/closed/list",
    status_code=status.HTTP_200_OK,
    response_model=list[GroupResponse],
    summary="Получить закрытые группы",
    description="""
Возвращает список завершённых (неактивных) групп.
""",
    response_description="Список закрытых групп",
)
async def get_closed_groups(
    service: GroupService = Depends(get_group_service),
):
    return await service.get_closed_groups()


# =========================
# Закрыть группу
# =========================
@router.post(
    "/{group_id}/close",
    status_code=status.HTTP_200_OK,
    response_model=GroupResponse,
    summary="Закрыть группу",
    description="""
Переводит группу в статус закрытой.

После закрытия набор новых студентов невозможен.
""",
    response_description="Закрытая группа",
    responses={
        404: {"description": "Группа не найдена"},
    },
)
async def close_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
):
    try:
        return await service.close_group(group_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =========================
# Восстановить группу
# =========================
@router.post(
    "/{group_id}/restore",
    status_code=status.HTTP_200_OK,
    response_model=GroupResponse,
    summary="Восстановить группу",
    description="""
Повторно активирует ранее закрытую группу.
""",
    response_description="Активная группа",
    responses={
        404: {"description": "Группа не найдена"},
    },
)
async def restore_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
):
    try:
        return await service.restore_group(group_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =========================
# Проверка существования группы
# =========================
@router.get(
    "/{group_id}/exists",
    status_code=status.HTTP_200_OK,
    response_model=GroupExistsResponse,
    summary="Проверить существование группы",
    description="""
Проверяет, существует ли группа по указанному ID.
""",
    response_description="Результат проверки",
)
async def exists_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
):
    result = await service.exists(group_id)

    return {
        "exists": result
    }


# =========================
# Поиск групп
# =========================
@router.get(
    "/search/name",
    status_code=status.HTTP_200_OK,
    response_model=list[GroupResponse],
    summary="Поиск групп по названию",
    description="""
Возвращает список групп, название которых содержит указанную строку.
""",
    response_description="Найденные группы",
)
async def search_groups(
    name: str,
    service: GroupService = Depends(get_group_service),
):
    return await service.search(name)


# =========================
# Группы филиала
# =========================
@router.get(
    "/branch/{branch_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[GroupResponse],
    summary="Получить группы филиала",
    description="""
Возвращает все группы выбранного филиала.
""",
    response_description="Список групп филиала",
)
async def get_groups_by_branch(
    branch_id: int,
    service: GroupService = Depends(get_group_service),
):
    return await service.get_by_branch(branch_id)


# =========================
# Группы направления
# =========================
@router.get(
    "/direction/{direction_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[GroupResponse],
    summary="Получить группы направления",
    description="""
Возвращает все группы выбранного направления обучения.
""",
    response_description="Список групп направления",
)
async def get_groups_by_direction(
    direction_id: int,
    service: GroupService = Depends(get_group_service),
):
    return await service.get_by_direction(direction_id)


# =========================
# Группы учебного плана
# =========================
@router.get(
    "/plan/{plan_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[GroupResponse],
    summary="Получить группы учебного плана",
    description="""
Возвращает все группы, работающие по выбранному учебному плану.
""",
    response_description="Список групп учебного плана",
)
async def get_groups_by_plan(
    plan_id: int,
    service: GroupService = Depends(get_group_service),
):
    return await service.get_by_plan(plan_id)
