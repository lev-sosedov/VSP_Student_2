from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth_service.models.models_auth_user import AuthUser


class AuthRepository:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_user_by_phone(self, phone_number: str):
        result = await self.db.execute(select(AuthUser).where(AuthUser.phone_number == phone_number))

        return result.scalar_one_or_none()



    async def create_user(self, data: dict):
        user = AuthUser(
            phone_number=data["phone_number"],
            user_name=data.get("user_name"),
            hashed_password=data["hashed_password"]
        )

        self.db.add(user)

        await self.db.commit()
        await self.db.refresh(user)

        return user