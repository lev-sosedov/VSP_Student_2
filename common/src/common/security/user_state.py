"""Redis-backed, short-lived authorization state shared by backend services."""
import os
from dataclasses import dataclass

try:
    from redis.asyncio import Redis
except ImportError:  # optional for lightweight service test environments
    class Redis:  # type: ignore[no-redef]
        @classmethod
        def from_url(cls, *_args, **_kwargs):
            raise RuntimeError("redis package is not installed")


@dataclass(frozen=True)
class UserSecurityState:
    token_version: int
    role: str
    status: str


def _key(auth_user_id: int) -> str:
    return f"security:user:{auth_user_id}"


async def get_user_security_state(auth_user_id: int) -> UserSecurityState | None:
    redis = Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"), decode_responses=True)
    try:
        values = await redis.hgetall(_key(auth_user_id))
        if not values:
            return None
        return UserSecurityState(int(values["token_version"]), values["role"], values["status"])
    finally:
        await redis.aclose()


async def set_user_security_state(*, auth_user_id: int, token_version: int, role: str, status: str) -> None:
    redis = Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"), decode_responses=True)
    try:
        await redis.hset(_key(auth_user_id), mapping={
            "token_version": str(token_version), "role": role, "status": status,
        })
    finally:
        await redis.aclose()
