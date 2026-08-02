from datetime import datetime, timezone
import hashlib
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models.models_refresh_session import RefreshSession


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class RefreshSessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **data) -> RefreshSession:
        data.setdefault("family_id", uuid.uuid4().hex)
        session = RefreshSession(**data)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_active(self, jti: str) -> RefreshSession | None:
        result = await self.db.execute(select(RefreshSession).where(
            RefreshSession.refresh_jti == jti,
        ).with_for_update())
        return result.scalar_one_or_none()

    async def revoke(self, session: RefreshSession, reason: str) -> None:
        session.revoked_at = datetime.now(timezone.utc).replace(tzinfo=None)
        session.revoke_reason = reason
        session.last_used_at = session.revoked_at
        await self.db.commit()

    async def revoke_family(self, family_id: str, reason: str) -> None:
        await self.db.execute(update(RefreshSession).where(
            RefreshSession.family_id == family_id,
            RefreshSession.revoked_at.is_(None),
        ).values(
            revoked_at=datetime.now(timezone.utc).replace(tzinfo=None),
            revoke_reason=reason,
        ))
        await self.db.commit()

    async def revoke_user(self, auth_user_id: int, reason: str) -> None:
        await self.db.execute(update(RefreshSession).where(
            RefreshSession.auth_user_id == auth_user_id,
            RefreshSession.revoked_at.is_(None),
        ).values(
            revoked_at=datetime.now(timezone.utc).replace(tzinfo=None),
            revoke_reason=reason,
        ))
        await self.db.commit()

    async def list_user(self, auth_user_id: int) -> list[RefreshSession]:
        result = await self.db.execute(select(RefreshSession).where(
            RefreshSession.auth_user_id == auth_user_id,
            RefreshSession.revoked_at.is_(None),
        ).order_by(RefreshSession.created_at.desc()))
        return list(result.scalars().all())
