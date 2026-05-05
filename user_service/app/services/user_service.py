from sqlalchemy.ext.asyncio import AsyncSession
from user_service.app.repositories.user_repository import UserRepository
from user_service.app.models.user import User
from user_service.app import UserCreate, UserUpdate


class UserService:

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create_user(self, data: UserCreate):
        existing = await self.repo.get_by_phone(data.phone_number)
        if existing:
            raise ValueError("User already exists")

        user = User(
            phone_number=data.phone_number,
            hashed_password=data.password,  # уже хэш!
            user_name=data.user_name,
            role=data.role
        )

        return await self.repo.create(user)

    async def get_user(self, user_id: int):
        return await self.repo.get_by_id(user_id)

    async def update_user(self, user_id: int, data: UserUpdate):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return await self.repo.update(user, data.dict(exclude_unset=True))