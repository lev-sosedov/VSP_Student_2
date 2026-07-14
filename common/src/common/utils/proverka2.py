from fastapi import APIRouter, Depends, HTTPException, Query

from academic_service.services.service_module import ModuleService
from academic_service.schemas.schemas_module import (
    ModuleCreate,
    ModuleUpdate,
    ModulePatch,
    ModuleResponse,
    ModuleListResponse,
    ModuleExistsResponse,
    ModuleFilter,
    ModuleArchive,
    ModuleActivate
)

router = APIRouter(prefix="/modules", tags=["Modules"])


# Получение сервиса
def get_service() -> ModuleService:
    pass


# Создание модуля
@router.post(
    "/",
    response_model=ModuleResponse
)
async def create_module(
        data: ModuleCreate,
        service: ModuleService = Depends(get_service)
):
    try:
        return await service.create_module(data)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# Получение по ID
@router.get(
    "/{module_id}",
    response_model=ModuleResponse
)
async def get_module(
        module_id: int,
        service: ModuleService = Depends(get_service)
):
    try:
        return await service.get_module_by_id(module_id)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# Получение списка модулей
@router.get(
    "/",
    response_model=ModuleListResponse
)
async def get_modules(
        limit: int = Query(20, ge=1),
        offset: int = Query(0, ge=0),
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


# Полное обновление
@router.put(
    "/{module_id}",
    response_model=ModuleResponse
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
            status_code=404,
            detail=str(e)
        )


# Частичное обновление
@router.patch(
    "/{module_id}",
    response_model=ModuleResponse
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
            status_code=404,
            detail=str(e)
        )


# Безопасное удаление
@router.delete(
    "/{module_id}"
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
            status_code=400,
            detail=str(e)
        )


# ---------------------------------------------

# Поиск по имени +
@router.get(
    "/search",
    response_model=list[ModuleResponse]
)
async def search_modules(
        name: str,
        service: ModuleService = Depends(get_service)
):
    return await service.repo.search(name)


# Фильтр модулей +
@router.post(
    "/filter",
    response_model=list[ModuleResponse]
)
async def filter_modules(
        data: ModuleFilter,
        service: ModuleService = Depends(get_service)
):
    return await service.repo.filter(data)


# Проверка используется ли модуль где ни-будь?
@router.get(
    "/{module_id}/used"
)
async def module_used(
        module_id: int,
        service: ModuleService = Depends(get_service)
):
    return {
        "used":
            await service.is_module_used(module_id)
    }


# ----------------------------------------------

# Архивация модуля +
@router.patch(
    "/{module_id}/archive",
    response_model=ModuleResponse
)
async def archive_module(
        module_id: int,
        data: ModuleArchive,
        service: ModuleService = Depends(get_service)
):
    module = await service.get_module_by_id(module_id)

    module.is_active = False
    module.closed_at = data.closed_at

    return await service.repo.update(module)


# Активация модуля
@router.patch(
    "/{module_id}/activate",
    response_model=ModuleResponse
)
async def activate_module(
        module_id: int,
        data: ModuleActivate,
        service: ModuleService = Depends(get_service)
):
    return await service.activate_module(
        module_id
    )
