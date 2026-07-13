from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from academic_service.models.branch import Branch
from academic_service.schemas.branch import BranchCreate


class BranchRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Создание филиала
    async def create(self, data: BranchCreate):
        branch = Branch(branch_address_id=data.branch_address_id, phone=data.phone, email=data.email)
        self.db.add(branch)
        await self.db.commit()
        await self.db.refresh(branch)

        return branch

    # Получение филиала по email !!!
    async def get_by_email(self, email: str):

        result = await self.db.execute(
            select(Branch)
            .where(Branch.email == email)
        )

        return result.scalar_one_or_none()

    # Получение филиала по id
    async def get_by_id(self, branch_id: int):
        result = await self.db.execute(select(Branch).where(Branch.id == branch_id))

        return result.scalar_one_or_none()

    # Получение всех филиалов
    async def get_all(self):
        result = await self.db.execute(select(Branch).order_by(Branch.id))

        return result.scalars().all()

    # Получение только активных филиалов
    async def get_active(self):
        result = await self.db.execute(select(Branch).where(Branch.is_active == True).order_by(Branch.id))

        return result.scalars().all()

    # Обновление филиала
    async def update(self, branch: Branch):
        await self.db.commit()
        await self.db.refresh(branch)

        return branch

    # Полное удаление (использоваться не будет, историю филиалов надо хранить.)
    async def delete(self, branch_id: int):
        await self.db.execute(delete(Branch).where(Branch.id == branch_id))

        await self.db.commit()

    # ----------------------------------------------------------------------

    # Получение филиалов по городу
    async def get_by_city(self, city: str):
        result = await self.db.execute(
            select(Branch).join(Branch.branch_address).where(Branch.branch_address.city == city))

        return result.scalars().all()

    # Получение филиала по адресу
    async def get_by_address_id(self, address_id: int):
        result = await self.db.execute(select(Branch).where(Branch.branch_address_id == address_id))

        return result.scalar_one_or_none()

    # Проверка существования филиала
    async def exists(self, branch_id: int):
        result = await self.db.execute(select(Branch.id).where(Branch.id == branch_id))

        return result.scalar_one_or_none() is not None

    # Закрыть филиал
    async def deactivate(self, branch_id: int):
        branch = await self.get_by_id(branch_id)

        if branch:
            branch.is_active = False
            await self.db.commit()

        return branch

    # Открыть филиал обратно
    async def activate(self, branch_id: int):
        branch = await self.get_by_id(branch_id)

        if branch:
            branch.is_active = True
            await self.db.commit()

        return branch
