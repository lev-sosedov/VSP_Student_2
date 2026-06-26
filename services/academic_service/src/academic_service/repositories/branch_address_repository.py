from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from academic_service.models.branch_address import BranchAddress


class BranchAddressRepository:

    def __init__(self, db: AsyncSession):
        self.db = db


    # Создание адреса
    async def create(self, address: BranchAddress):
        self.db.add(address)
        await self.db.commit()
        await self.db.refresh(address)

        return address


    # Получить адрес по id
    async def get_by_id(self, address_id: int):
        result = await self.db.execute(select(BranchAddress).where(BranchAddress.id == address_id))

        return result.scalar_one_or_none()


    # Получить все адреса
    async def get_all(self):
        result = await self.db.execute(select(BranchAddress).order_by(BranchAddress.id))

        return result.scalars().all()


    # Найти адреса по стране
    async def get_by_country(self, country: str):
        result = await self.db.execute(select(BranchAddress).where(BranchAddress.country == country))

        return result.scalars().all()


    # Найти адреса по городу
    async def get_by_city(self, city: str):
        result = await self.db.execute(select(BranchAddress).where(BranchAddress.city == city))

        return result.scalars().all()


    # Поиск по улице
    async def get_by_street(self, street: str):
        result = await self.db.execute(select(BranchAddress).where(BranchAddress.street == street))

        return result.scalars().all()


    # Поиск полного адреса
    async def search(self, text: str):
        result = await self.db.execute(select(BranchAddress).where(BranchAddress.street.ilike(f"%{text}%")))

        return result.scalars().all()


    # Проверка существования адреса
    async def exists(self, address_id: int):
        result = await self.db.execute(select(BranchAddress.id).where(BranchAddress.id == address_id))

        return result.scalar_one_or_none() is not None


    # Обновление адреса
    async def update(self, address_id: int, data: dict):
        await self.db.execute(update(BranchAddress).where(BranchAddress.id == address_id).values(**data))
        await self.db.commit()

        return await self.get_by_id(address_id)


    # Изменить только город
    async def change_city(self, address_id: int, city: str):
        await self.db.execute(update(BranchAddress).where(BranchAddress.id == address_id).values(city=city))
        await self.db.commit()

        return await self.get_by_id(address_id)


    # Изменить улицу
    async def change_street(self, address_id: int, street: str):
        await self.db.execute(update(BranchAddress).where(BranchAddress.id == address_id).values(street=street))
        await self.db.commit()

        return await self.get_by_id(address_id)


    # Полное удаление адреса
    async def delete(self, address_id: int):
        await self.db.execute(delete(BranchAddress).where(BranchAddress.id == address_id))

        await self.db.commit()