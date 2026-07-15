from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_role import RoleType

from user_service.repositories.repository_user import UserRepository
from user_service.models.model_user import User
from user_service.schemas.schemas_user import UserCreate, UserUpdate
from user_service.schemas.schemas_events import UserCreatedEvent


class UserService:


    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)


    async def create_user(self, data: UserCreate):
        existing = await self.repo.get_by_phone(data.phone_number)
        if existing:
            raise ValueError("User already exists")

        user = User(
            phone_number=data.phone_number,
            user_name=data.user_name,
            role=RoleType.USER
        )

        return await self.repo.create(user)

    async def create_user_from_event(self, data: UserCreatedEvent):
        existing = await self.repo.get_by_phone(data.phone_number)

        if existing:
            return existing

        user = User(
            auth_id=data.auth_id,
            phone_number=data.phone_number,
            user_name=data.user_name,
            role=RoleType.USER
        )

        return await self.repo.create(user)


    async def get_user(self, user_id: int):
        return await self.repo.get_by_id(user_id)


    async def get_users(self, limit: int = 20, offset: int = 0):
        return await self.repo.get_all(limit, offset)


    # для регистрации, поиск по номеру телефона
    async def get_user_by_phone(self, phone_number: str):
        return await self.repo.get_by_phone(phone_number)


    async def update_user(self, user_id: int, data: UserUpdate):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return await self.repo.update(user, data.dict(exclude_unset=True))


    async def change_role(self, user_id: int, role: RoleType):
        user = await self.repo.get_by_id(user_id)

        if not user:
            raise ValueError("Not found")

        user.role = role

        return await self.repo.save(user)

    async def activate_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)

        if not user:
            raise ValueError(
                "User not found"
            )

        user.is_active = True

        return await self.repo.save(user)

    async def block_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        user.is_active = False

        return await self.repo.update(user, {})

    async def verify_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)

        if not user:
            raise ValueError(
                "User not found"
            )

        user.is_account_verified = True

        return await self.repo.save(user)

    async def delete_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        await self.repo.delete(user)

        return True

