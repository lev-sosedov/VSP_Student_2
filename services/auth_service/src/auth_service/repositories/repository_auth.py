from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from auth_service.models.models_auth_user import AuthUser


class AuthRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_phone(
        self,
        phone_number: str
    ):
        result = await self.db.execute(
            select(AuthUser).where(
                AuthUser.phone_number == phone_number
            )
        )

        return result.scalar_one_or_none()

    async def get_user_by_id(
        self,
        user_id: int
    ):
        result = await self.db.execute(
            select(AuthUser).where(
                AuthUser.id == user_id
            )
        )

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

    async def update_password(
        self,
        user: AuthUser,
        hashed_password: str
    ) -> AuthUser:
        user.hashed_password = hashed_password

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_token_version(self, auth_user_id: int) -> int | None:
        result = await self.db.execute(
            select(AuthUser.token_version).where(AuthUser.id == auth_user_id)
        )
        return result.scalar_one_or_none()

    async def increment_token_version(self, auth_user_id: int) -> int | None:
        """Atomically invalidate all previously issued tokens for an auth user."""
        result = await self.db.execute(
            update(AuthUser)
            .where(AuthUser.id == auth_user_id)
            .values(token_version=AuthUser.token_version + 1)
            .returning(AuthUser.token_version)
        )
        token_version = result.scalar_one_or_none()
        if token_version is not None:
            await self.db.commit()
        return token_version
