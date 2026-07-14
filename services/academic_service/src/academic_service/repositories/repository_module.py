from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_

from academic_service.models.module import Module


class ModuleRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Создание модуля
    async def create(self, module: Module):
        self.db.add(module)
        await self.db.commit()
        await self.db.refresh(module)

        return module

    # Получение модуля по id
    async def get_by_id(self, module_id: int):
        result = await self.db.execute(select(Module).where(Module.id == module_id))

        return result.scalar_one_or_none()

    # Все модули
    async def get_all(self, limit: int = 20, offset: int = 0):
        result = await self.db.execute(
            select(Module)

        )

        return result.scalars().all()

    # Обновление всех полей
    async def update(self, module: Module):
        await self.db.commit()
        await self.db.refresh(module)

        return module

    # Изменить название
    async def update_name(self, module_id: int, name: str):
        await self.db.execute(update(Module).where(Module.id == module_id).values(name=name))
        await self.db.commit()

        return await self.get_by_id(module_id)

    # Изменить описание
    async def update_description(self, module_id: int, description: str):
        await self.db.execute(update(Module).where(Module.id == module_id).values(description=description))
        await self.db.commit()

        return await self.get_by_id(module_id)

    # Удаление
    async def delete(self, module_id: int):
        await self.db.execute(delete(Module).where(Module.id == module_id))
        await self.db.commit()

        return {"message": "Module deleted"}

    # --------------------------------

    # Получение модуля по названию
    async def get_by_name(self, name: str):

        result = await self.db.execute(
            select(Module)
            .where(Module.name == name)
        )

        return result.scalar_one_or_none()

    async def filter(
            self,
            name=None,
            is_active=None,
            created_from=None,
            created_to=None
    ):

        query = select(Module)

        if name:
            query = query.where(
                Module.name.ilike(f"%{name}%")
            )

        if is_active is not None:
            query = query.where(
                Module.is_active == is_active
            )

        result = await self.db.execute(query)

        return result.scalars().all()

    # Только активные
    async def get_active(self):
        result = await self.db.execute(select(Module).where(Module.is_active == True).order_by(Module.order_number))

        return result.scalars().all()

    # Только закрытые
    async def get_closed(self):
        result = await self.db.execute(select(Module).where(Module.is_active == False).order_by(Module.order_number))

        return result.scalars().all()

    # Поиск по названию
    async def search_by_name(self, name: str):
        result = await self.db.execute(
            select(Module).where(Module.name.ilike(f"%{name}%")).order_by(Module.order_number))

        return result.scalars().all()

    # Проверка существования
    async def exists(self, module_id: int):
        result = await self.db.execute(select(Module.id).where(Module.id == module_id))

        return result.scalar_one_or_none() is not None

    # Проверка по названию
    async def exists_by_name(self, name: str):
        result = await self.db.execute(select(Module.id).where(Module.name == name))

        return result.scalar_one_or_none() is not None

    # Изменить порядок модуля
    async def update_order(self, module_id: int, order_number: int):
        await self.db.execute(update(Module).where(Module.id == module_id).values(order_number=order_number))
        await self.db.commit()

        return await self.get_by_id(module_id)

    # Закрыть модуль
    async def deactivate(self, module_id: int):
        module = await self.get_by_id(module_id)

        if module:
            module.is_active = False
            await self.db.commit()

        return module

    # Открыть модуль
    async def activate(self, module_id: int):
        module = await self.get_by_id(module_id)

        if module:
            module.is_active = True
            await self.db.commit()

        return module
