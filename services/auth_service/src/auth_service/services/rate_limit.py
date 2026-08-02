import hashlib
import time

from fastapi import HTTPException, Request, status
from redis.asyncio import Redis

from auth_service.core.core_config import settings


def _phone_hash(phone: str | None) -> str:
    return hashlib.sha256("".join((phone or "").split()).encode()).hexdigest()[:16]


async def enforce_auth_rate_limit(request: Request, action: str, phone: str | None = None) -> None:
    ip = request.client.host if request.client else "unknown"
    key = f"auth:rl:{action}:{ip}:{_phone_hash(phone)}"
    limit = getattr(settings, f"AUTH_RATE_LIMIT_{action.upper()}")
    retry = settings.AUTH_RATE_LIMIT_WINDOW_SECONDS
    try:
        redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, retry)
        await redis.aclose()
    except Exception:
        return  # fail-open keeps development usable; production should alert on Redis outage
    if count > limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Too many requests", headers={"Retry-After": str(retry)})
