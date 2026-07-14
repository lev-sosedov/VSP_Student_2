from datetime import datetime

from academic_service.models.module import Module
from academic_service.repositories.repository_module import ModuleRepository
from academic_service.schemas.schemas_module import (
    ModuleCreate,
    ModuleUpdate,
    ModulePatch,
    ModuleFilter,
    ModuleArchive,
    ModuleActivate)


class ModuleService:

    def __init__(self, repo: ModuleRepository):
        self.repo = repo

    # создание модуля
    async def create_module(self, data: ModuleCreate):
        existing = await self.repo.get_by_name(data.name)

        if existing:
            raise ValueError("Module with this name already exists")

        module = Module(name=data.name, description=data.description)

        return await self.repo.create(module)

    # получить по id
    async def get_module_by_id(self, module_id: int):
        module = await self.repo.get_by_id(module_id)

        if not module:
            raise ValueError("Module not found")

        return module

    # список всех
    async def get_modules(self, limit: int = 20, offset: int = 0):

        return await self.repo.get_all(limit, offset)

    # полное обновление PUT
    async def update_module(self, module_id: int, data: ModuleUpdate):
        module = await self.repo.get_by_id(module_id)

        if not module:
            raise ValueError("Module not found")

        if data.name is not None:
            exists = await self.repo.get_by_name(data.name)
            if exists and exists.id != module.id:
                raise ValueError("Module name already exists")
            module.name = data.name

        if data.description is not None:
            module.description = data.description

        return await self.repo.update(module)

    # Частичное обновление PATCH
    async def patch_module(self, module_id: int, data: ModulePatch):
        module = await self.repo.get_by_id(module_id)

        if not module:
            raise ValueError("Module not found")

        if data.name is not None:
            module.name = data.name

        if data.description is not None:
            module.description = data.description

        if data.is_active is not None:
            module.is_active = data.is_active
            if data.is_active:
                module.closed_at = None

        return await self.repo.update(module)

    # используется ли модуль (проверка перед удалением модуля)
    async def is_module_used(self, module_id: int):

        # return await self.repo.is_used_in_education_plans(module_id) # временная заглушка, пока таблицы пустые.
        return False

    # безопасное удаление
    async def safe_delete_module(self, module_id: int):
        used = await self.is_module_used(module_id)

        if used:
            raise ValueError("Module is used and cannot be deleted")

        return await self.repo.delete(module_id)

    # -----------------------------------------------------------------

    # Поиск модулей по названию
    async def search_modules(self, name: str):

        return await self.repo.search_by_name(name)

    # получить по названию
    async def get_module_by_name(self, name: str):

        return await self.repo.get_by_name(name)

    # фильтр
    async def filter_modules(self, filters: ModuleFilter):

        return await self.repo.filter(
            name=filters.name,
            is_active=filters.is_active,
            created_from=filters.created_from,
            created_to=filters.created_to)

    # архивировать
    async def archive_module(self, module_id: int, data: ModuleArchive):
        module = await self.repo.get_by_id(module_id)

        if not module:
            raise ValueError("Module not found")

        module.is_active = False
        module.closed_at = data.closed_at

        return await self.repo.update(module)

    # закрыть сегодня
    async def deactivate_module(self, module_id: int):
        module = await self.repo.get_by_id(module_id)

        if not module:
            raise ValueError("Module not found")

        module.is_active = False
        module.closed_at = datetime.utcnow()

        return await self.repo.update(module)

    # активировать
    async def activate_module(self, module_id: int, data: ModuleActivate | None = None):
        module = await self.repo.get_by_id(module_id)

        if not module:
            raise ValueError("Module not found")

        module.is_active = True
        module.closed_at = None

        return await self.repo.update(module)

    # восстановить
    async def restore_module(self, module_id: int):
        module = await self.repo.get_by_id(module_id)

        if not module:
            raise ValueError("Module not found")

        module.is_active = True
        module.closed_at = None

        return await self.repo.update(module)

    # существует ли модуль
    async def exists(self, module_id: int):
        module = await self.repo.get_by_id(module_id)

        return bool(module)

    # количество активных модулей
    async def count_active(self):
        modules = await self.repo.get_all()

        return len([m for m in modules if m.is_active])

    # полное удаление, не проверяет, используется или нет.
    async def delete_module(self, module_id: int):
        module = await self.repo.get_by_id(module_id)

        if not module:
            raise ValueError("Module not found")

        return await self.repo.delete(module_id)
