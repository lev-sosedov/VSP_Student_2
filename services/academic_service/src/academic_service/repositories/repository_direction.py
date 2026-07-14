from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from academic_service.models.models_direction import Direction


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
    async def get_all(self, limit: int = 20, offset: int = 0):
        result = await self.db.execute(select(Direction).order_by(Direction.id).limit(limit).offset(offset))

        return result.scalars().all()

    # Обновление всех данных
    async def update(self, direction: Direction):
        await self.db.commit()
        await self.db.refresh(direction)

        return direction

    # Изменить название
    async def update_name(self, direction_id: int, name: str):
        await self.db.execute(update(Direction).where(Direction.id == direction_id).values(name=name))
        await self.db.commit()

        return await self.get_by_id(direction_id)

    # Изменить описание
    async def update_description(self, direction_id: int, description: str):
        await self.db.execute(update(Direction).where(Direction.id == direction_id).values(description=description))
        await self.db.commit()

        return await self.get_by_id(direction_id)

    # Удаление
    async def delete(self, direction_id: int):
        await self.db.execute(delete(Direction).where(Direction.id == direction_id))

        await self.db.commit()

    # --------------------------------------------------

    # Получить направление по названию (перед создание проверяет есть такое направление или нет) +
    async def get_by_name(self, name: str):
        result = await self.db.execute(select(Direction).where(Direction.name == name))

        return result.scalar_one_or_none()

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

    # Фильтрация направлений
    async def filter(
            self,
            name: str | None = None,
            is_active: bool | None = None
    ):
        query = select(Direction)

        if name:
            query = query.where(Direction.name.ilike(f"%{name}%"))

        if is_active is not None:
            query = query.where(Direction.is_active == is_active)

        result = await self.db.execute(query)

        return result.scalars().all()

    # Закрыть направление
    async def deactivate(self, direction_id: int):
        direction = await self.get_by_id(direction_id)

        if direction:
            direction.is_active = False
            await self.db.commit()

        return direction

    # Открыть направление
    async def activate(self, direction_id: int):
        direction = await self.get_by_id(direction_id)

        if direction:
            direction.is_active = True
            await self.db.commit()

        return direction
