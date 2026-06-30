from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from academic_service.models.direction import Direction


class DirectionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db


    # Создание направления
    async def create(self, direction: Direction):
        self.db.add(direction)
        await self.db.commit()
        await self.db.refresh(direction)

        return direction


    # Получение по id
    async def get_by_id(self, direction_id: int):
        result = await self.db.execute(select(Direction).where(Direction.id == direction_id))

        return result.scalar_one_or_none()


    # Получить все направления
    async def get_all(self):
        result = await self.db.execute(select(Direction).order_by(Direction.id))

        return result.scalars().all()


    # Только активные направления
    async def get_active(self):
        result = await self.db.execute(select(Direction).where(Direction.is_active == True).order_by(Direction.name))

        return result.scalars().all()


    # Только закрытые направления
    async def get_closed(self):
        result = await self.db.execute(select(Direction).where(Direction.is_active == False).order_by(Direction.name))

        return result.scalars().all()


    # Поиск по названию
    async def search_by_name(self, name: str):
        result = await self.db.execute(select(Direction).where(Direction.name.ilike(f"%{name}%")))

        return result.scalars().all()


    # Проверка существования
    async def exists(self, direction_id: int):
        result = await self.db.execute(select(Direction.id).where(Direction.id == direction_id))

        return result.scalar_one_or_none() is not None


    # Проверка существования по имени
    async def exists_by_name(self, name: str):
        result = await self.db.execute(select(Direction.id).where(Direction.name == name))

        return result.scalar_one_or_none() is not None


    # Обновление всех данных
    async def update(self,direction_id: int,data: dict):
        await self.db.execute(update(Direction).where(Direction.id == direction_id).values(**data))
        await self.db.commit()

        return await self.get_by_id(direction_id)


    # Изменить название
    async def update_name(self,direction_id: int,name: str):
        await self.db.execute(update(Direction).where(Direction.id == direction_id).values(name=name))
        await self.db.commit()

        return await self.get_by_id(direction_id)


    # Изменить описание
    async def update_description(self,direction_id: int,description: str):
        await self.db.execute(update(Direction).where(Direction.id == direction_id).values(description=description))
        await self.db.commit()

        return await self.get_by_id(direction_id)


    # Закрыть направление
    async def deactivate(self,direction_id: int):
        direction = await self.get_by_id(direction_id)

        if direction:
            direction.is_active = False
            await self.db.commit()

        return direction


    # Открыть направление
    async def activate(self,direction_id: int):
        direction = await self.get_by_id(direction_id)

        if direction:
            direction.is_active = True
            await self.db.commit()

        return direction


    # Удаление
    async def delete(self, direction_id: int):
        await self.db.execute( delete(Direction).where(Direction.id == direction_id))

        await self.db.commit()