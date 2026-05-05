from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from user_service.app.models.user import User


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_phone(self, phone: str):
        result = await self.db.execute(
            select(User).where(User.phone_number == phone)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int):
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(self, user: User, data: dict):
        for field, value in data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user