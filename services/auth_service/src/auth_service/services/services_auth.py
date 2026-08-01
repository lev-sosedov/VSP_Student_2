from fastapi import HTTPException, status

from auth_service.core.core_security import (
    hash_password,
    verify_password,
    get_issuer,
    get_verifier,
)
from auth_service.schemas.schemas_auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    ChangePasswordRequest
)
from auth_service.repositories.repository_auth import AuthRepository
from auth_service.messaging.messaging_rabbit import publish_user_created
from auth_service.messaging.messaging_rpc_client import user_identity_rpc_client
from auth_service.services.identity_resolver import IdentityResolver
from common.identity import IdentityResolutionError
from common.security.exceptions import SecurityError


class AuthService:

    def __init__(self, db, identity_resolver=None):
        self.repo = AuthRepository(db)
        self.identity_resolver = identity_resolver or IdentityResolver(user_identity_rpc_client)

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

        try:
            identity = await self.identity_resolver.resolve(user)
        except IdentityResolutionError as exc:
            raise HTTPException(status_code=401, detail=exc.public_message) from exc
        return get_issuer().create_pair(identity)

    async def refresh(self, data: RefreshRequest):
        try:
            payload = get_verifier().verify_refresh_token(data.refresh_token)
        except SecurityError as exc:
            raise HTTPException(status_code=401, detail=exc.public_message) from exc
        auth_user = await self.repo.get_user_by_id(int(payload["auth_user_id"]))
        if auth_user is None or auth_user.token_version != int(payload["token_version"]):
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        try:
            identity = await self.identity_resolver.resolve(auth_user)
        except IdentityResolutionError as exc:
            raise HTTPException(status_code=401, detail=exc.public_message) from exc
        if identity.user_id != int(payload["sub"]):
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        return get_issuer().create_pair(identity)

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
        await self.repo.increment_token_version(user.id)

        return {
            "message": "Пароль успешно изменён"
        }
