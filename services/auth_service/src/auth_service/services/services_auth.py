from fastapi import HTTPException, status

from auth_service.core.core_security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from auth_service.schemas.schemas_auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    ChangePasswordRequest
)
from auth_service.repositories.repository_auth import AuthRepository
from auth_service.messaging.messaging_rabbit import publish_user_created


class AuthService:

    def __init__(self, db):
        self.repo = AuthRepository(db)

    async def register(self, data: RegisterRequest):
        existing = await self.repo.get_user_by_phone(
            data.phone_number
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )

        password_hash = hash_password(data.password)
        user = await self.repo.create_user(
            {
                "phone_number": data.phone_number,
                "user_name": data.user_name,
                "hashed_password": password_hash
            }
        )

        # RabbitMQ -> user-service
        await publish_user_created(
            {
                "auth_id": user.id,
                "phone_number": user.phone_number,
                "user_name": user.user_name
            }
        )

        return {
            "id": user.id,
            "phone_number": user.phone_number,
            "message": "User created"
        }

    async def login(self, data: LoginRequest):
        user = await self.repo.get_user_by_phone(
            data.phone_number
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="User blocked"
            )

        if not verify_password(
            data.password,
            user.hashed_password
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        payload = {
            "user_id": user.id,
            "role": user.role
        }

        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "token_type": "bearer"
        }

    async def refresh(self, data: RefreshRequest):
        payload = decode_token(data.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        new_payload = {
            "user_id": payload["user_id"],
            "role": payload["role"]
        }

        return {
            "access_token": create_access_token(new_payload),
            "refresh_token": create_refresh_token(new_payload),
            "token_type": "bearer"
        }

    async def change_password(
        self,
        user_id: int,
        data: ChangePasswordRequest
    ) -> dict:
        user = await self.repo.get_user_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Аккаунт заблокирован"
            )

        if not verify_password(
            data.current_password,
            user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Текущий пароль указан неверно"
            )

        if verify_password(
            data.new_password,
            user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Новый пароль должен отличаться "
                    "от текущего"
                )
            )

        await self.repo.update_password(
            user=user,
            hashed_password=hash_password(
                data.new_password
            )
        )

        return {
            "message": "Пароль успешно изменён"
        }
