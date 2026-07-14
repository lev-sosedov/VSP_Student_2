from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from academic_service.models.models_branch_address import BranchAddress
from academic_service.schemas.schemas_branch_address import BranchAddressCreate, BranchAddressPatch


class BranchAddressRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Создание адреса
    async def create(self, data: BranchAddressCreate) -> BranchAddress:
        address = BranchAddress(**data.model_dump())
        self.db.add(address)
        await self.db.commit()
        await self.db.refresh(address)

        return address

    # Получить адрес по id
    async def get_by_id(self, address_id: int):
        result = await self.db.execute(select(BranchAddress).where(BranchAddress.id == address_id))

        return result.scalar_one_or_none()

    # Получить все адреса
    async def get_all(self, limit: int = 20, offset: int = 0):
        result = await self.db.execute(select(BranchAddress).limit(limit).offset(offset))

        return result.scalars().all()

    # Обновление адреса
    async def update(self, address: BranchAddress, data):
        for key, value in data.model_dump().items():
            setattr(address, key, value)

        await self.db.commit()
        await self.db.refresh(address)

        return address

    # Изменить что-то в адресе
    async def patch(self, address: BranchAddress, data: BranchAddressPatch, ):
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(address, key, value)

        await self.db.commit()
        await self.db.refresh(address)

        return address

    # Полное удаление адреса
    async def delete(self, address_id: int):
        await self.db.execute(delete(BranchAddress).where(BranchAddress.id == address_id))

        await self.db.commit()

    # ---------------------------------------------------------------------------------------

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
