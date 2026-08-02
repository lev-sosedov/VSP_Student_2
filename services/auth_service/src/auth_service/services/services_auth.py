from fastapi import HTTPException, status
from datetime import datetime, timezone
import uuid
import jwt

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
from auth_service.repositories.repository_refresh_session import RefreshSessionRepository, hash_refresh_token
from auth_service.repositories.repository_login_attempt import LoginAttemptRepository
from common.security.user_state import set_user_security_state


class AuthService:

    def __init__(self, db, identity_resolver=None):
        self.repo = AuthRepository(db)
        self.sessions = RefreshSessionRepository(db)
        self.audit = LoginAttemptRepository(db)
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

    async def _audit(self, data, *, success, reason, user=None, request=None):
        try:
            await self.audit.record(phone=data.phone_number, success=success,
                reason_code=reason, auth_user_id=getattr(user, "id", None),
                ip_address=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None)
        except Exception:
            await self.repo.db.rollback()

    async def login(self, data: LoginRequest, request=None):
        user = await self.repo.get_user_by_phone(
            data.phone_number
        )

        if not user:
            await self._audit(data, success=False, reason="user_not_found", request=request)
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        if not user.is_active:
            await self._audit(data, success=False, reason="user_inactive", user=user, request=request)
            raise HTTPException(
                status_code=403,
                detail="User blocked"
            )

        if not verify_password(
            data.password,
            user.hashed_password
        ):
            await self._audit(data, success=False, reason="invalid_password", user=user, request=request)
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        try:
            identity = await self.identity_resolver.resolve(user)
        except IdentityResolutionError as exc:
            await self._audit(data, success=False, reason="identity_resolution_failed", user=user, request=request)
            raise HTTPException(status_code=401, detail=exc.public_message) from exc
        if not identity.is_active or not identity.is_account_verified:
            await self._audit(data, success=False, reason="account_not_verified", user=user, request=request)
            raise HTTPException(status_code=403, detail="Account is not active or verified")
        pair = get_issuer().create_pair(identity)
        await self._store_refresh_session(pair, identity, data)
        await set_user_security_state(auth_user_id=identity.auth_user_id, token_version=identity.token_version, role=identity.role.value, status="active")
        await self._audit(data, success=True, reason="success", user=user, request=request)
        return pair

    async def _store_refresh_session(self, pair, identity, request_data=None, family_id=None):
        claims = jwt.decode(pair["refresh_token"], options={"verify_signature": False})
        return await self.sessions.create(
            auth_user_id=identity.auth_user_id,
            # New logins start a refresh-token family.  Passing None would
            # bypass the repository default and violate the NOT NULL column.
            family_id=family_id or uuid.uuid4().hex,
            user_id=identity.user_id,
            refresh_jti=claims["jti"],
            refresh_token_hash=hash_refresh_token(pair["refresh_token"]),
            token_version=identity.token_version,
            expires_at=datetime.fromtimestamp(claims["exp"], tz=timezone.utc).replace(tzinfo=None),
        )

    async def refresh(self, data: RefreshRequest):
        try:
            payload = get_verifier().verify_refresh_token(data.refresh_token)
        except SecurityError as exc:
            raise HTTPException(status_code=401, detail=exc.public_message) from exc
        auth_user = await self.repo.get_user_by_id(int(payload["auth_user_id"]))
        if auth_user is None or auth_user.token_version != int(payload["token_version"]):
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        session = await self.sessions.get_active(payload["jti"])
        if session is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        if session.refresh_token_hash != hash_refresh_token(data.refresh_token):
            await self.sessions.revoke_family(session.family_id, "refresh_reuse")
            await self.repo.increment_token_version(auth_user.id)
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        try:
            identity = await self.identity_resolver.resolve(auth_user)
        except IdentityResolutionError as exc:
            raise HTTPException(status_code=401, detail=exc.public_message) from exc
        if identity.user_id != int(payload["sub"]):
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        await self.sessions.revoke(session, "rotated")
        pair = get_issuer().create_pair(identity)
        new_session = await self._store_refresh_session(pair, identity, data, session.family_id)
        await set_user_security_state(auth_user_id=identity.auth_user_id, token_version=identity.token_version, role=identity.role.value, status="active")
        session.replaced_by_session_id = new_session.id
        await self.repo.db.commit()
        return pair

    async def logout_all(self, user_id: int) -> None:
        await self.sessions.revoke_user(user_id, "logout_all")
        await self.repo.increment_token_version(user_id)

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
        new_version = await self.repo.increment_token_version(user.id)
        await self.sessions.revoke_user(user.id, "password_changed")
        await set_user_security_state(
            auth_user_id=user.id,
            token_version=new_version or user.token_version,
            role=str(user.role),
            status="active",
        )

        return {
            "message": "Пароль успешно изменён"
        }
