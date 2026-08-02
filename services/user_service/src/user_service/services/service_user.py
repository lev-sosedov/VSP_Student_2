from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from common.utils.enum_role import RoleType

from user_service.repositories.repository_user import (
    UserRepository
)
from user_service.models.model_user import User
from user_service.schemas.schemas_user import (
    UserCreate,
    UserUpdate
)
from user_service.schemas.schemas_events import (
    UserCreatedEvent
)
from user_service.repositories.repository_outbox import OutboxRepository


class UserService:

    def __init__(
        self,
        db: AsyncSession
    ):
        self.repo = UserRepository(db)
        self.outbox = OutboxRepository(db)

    async def _commit_event(self, user, event_type: str, **extra):
        await self.outbox.add(
            event_id=uuid4().hex,
            event_type=event_type,
            user_id=user.id,
            auth_id=user.auth_id,
            payload={"role": getattr(user.role, "value", str(user.role)), "is_active": user.is_active, **extra},
        )
        await self.repo.db.commit()

    async def create_user(
        self,
        data: UserCreate
    ):
        existing = await self.repo.get_by_phone(
            data.phone_number
        )

        if existing:
            raise ValueError(
                "User already exists"
            )

        user = User(
            phone_number=data.phone_number,
            user_name=data.user_name,
            role=RoleType.USER
        )

        await self.repo.create(user)
        await self._commit_event(user, "user.created")
        return user

    async def create_user_from_event(
        self,
        data: UserCreatedEvent
    ):
        existing = await self.repo.get_by_phone(
            data.phone_number
        )

        if existing:
            return existing

        user = User(
            auth_id=data.auth_id,
            phone_number=data.phone_number,
            user_name=data.user_name,
            role=RoleType.USER
        )

        await self.repo.create(user)
        await self.repo.db.commit()
        return user

    async def get_user(
        self,
        user_id: int
    ):
        return await self.repo.get_by_id(
            user_id
        )

    async def get_users(
        self,
        limit: int = 20,
        offset: int = 0
    ):
        return await self.repo.get_all(
            limit,
            offset
        )

    async def get_public_teachers(self):
        return await self.repo.get_public_teachers()

    async def get_user_by_phone(
        self,
        phone_number: str
    ):
        return await self.repo.get_by_phone(
            phone_number
        )

    async def update_user(
        self,
        user_id: int,
        data: UserUpdate
    ):
        user = await self.repo.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        user = await self.repo.update(
            user,
            data.model_dump(
                exclude_unset=True
            )
        )
        await self._commit_event(user, "user.updated")
        return user

    async def change_role(
        self,
        user_id: int,
        role: RoleType
    ):
        user = await self.repo.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        user.role = role

        await self.repo.save(user)
        await self._commit_event(user, "user.role.changed")
        return user

    async def activate_user(
        self,
        user_id: int
    ):
        user = await self.repo.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        user.is_active = True

        await self.repo.save(user)
        await self._commit_event(user, "user.activated")
        return user

    async def block_user(
        self,
        user_id: int
    ):
        user = await self.repo.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        user.is_active = False

        await self.repo.save(user)
        await self._commit_event(user, "user.blocked")
        return user

    async def verify_account(
        self,
        user_id: int
    ):
        user = await self.repo.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        user.is_account_verified = True

        await self.repo.save(user)
        await self._commit_event(user, "user.account_verified")
        return user

    async def verify_phone(
        self,
        user_id: int
    ):
        user = await self.repo.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        user.is_phone_verified = True

        await self.repo.save(user)
        await self._commit_event(user, "user.phone_verified")
        return user

    async def delete_user(
        self,
        user_id: int
    ):
        user = await self.repo.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        await self.repo.delete(user)
        await self.outbox.add(event_id=uuid4().hex, event_type="user.deleted", user_id=user_id, auth_id=user.auth_id, payload={})
        await self.repo.db.commit()

        return True
