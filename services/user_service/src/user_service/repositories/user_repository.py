from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from user_service.models.user import User


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

    async def get_by_email(
            self,
            email: str
    ):
        result = await self.db.execute(
            select(User)
            .where(User.email == email)
        )

        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int):
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
            self,
            limit: int = 20,
            offset: int = 0
    ):
        result = await self.db.execute(
            select(User)
            .limit(limit)
            .offset(offset)
        )

        return result.scalars().all()

    async def update(self, user: User, data: dict):
        for field, value in data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)

        return user


    async def save(self, user: User):
        self.db.add(user)

        await self.db.commit()
        await self.db.refresh(user)

        return user


    async def delete(self, user: User):
        await self.db.delete(user)
        await self.db.commit()
