"""Redis-backed, short-lived authorization state shared by backend services."""
import os
from urllib.parse import quote
from dataclasses import dataclass
from typing import Any

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


def _redis_url() -> str:
    # Compose may inject an empty value when REDIS_URL is omitted from .env.
    configured = os.getenv("REDIS_URL")
    if configured:
        return configured
    password = os.getenv("REDIS_PASSWORD")
    if password:
        return f"redis://:{quote(password, safe='')}@redis:6379/0"
    return "redis://redis:6379/0"


async def get_user_security_state(auth_user_id: int) -> UserSecurityState | None:
    redis: Any = Redis.from_url(_redis_url(), decode_responses=True)
    try:
        values = await redis.hgetall(_key(auth_user_id))
        if not values:
            return None
        return UserSecurityState(int(values["token_version"]), values["role"], values["status"])
    finally:
        await redis.aclose()


async def set_user_security_state(*, auth_user_id: int, token_version: int, role: str, status: str) -> None:
    redis: Any = Redis.from_url(_redis_url(), decode_responses=True)
    try:
        await redis.hset(_key(auth_user_id), mapping={
            "token_version": str(token_version), "role": role, "status": status,
        })
    finally:
        await redis.aclose()
