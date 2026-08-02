"""Shared non-sensitive readiness response helpers."""
from __future__ import annotations

import asyncio
import os
from typing import Iterable
from urllib.parse import quote

import aio_pika
from fastapi.responses import JSONResponse
from sqlalchemy import text


async def probe_rabbitmq(timeout_seconds: float = 1.0) -> bool:
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = quote(os.getenv("RABBITMQ_USERNAME", ""), safe="")
    password = quote(os.getenv("RABBITMQ_PASSWORD", ""), safe="")
    vhost = os.getenv("RABBITMQ_VIRTUAL_HOST", "/").lstrip("/")
    connection = None
    try:
        connection = await asyncio.wait_for(
            aio_pika.connect_robust(f"amqp://{user}:{password}@{host}:{port}/{vhost}"),
            timeout=timeout_seconds,
        )
        channel = await asyncio.wait_for(connection.channel(), timeout=timeout_seconds)
        await channel.close()
        return True
    except Exception:
        return False
    finally:
        if connection is not None and not connection.is_closed:
            await connection.close()


async def probe_redis(timeout_seconds: float = 1.0) -> bool:
    try:
        import redis.asyncio as redis
    except ImportError:
        return False
    url = os.getenv("REDIS_URL")
    if not url:
        return False
    client = redis.from_url(url, socket_connect_timeout=timeout_seconds, socket_timeout=timeout_seconds)
    try:
        return bool(await asyncio.wait_for(client.ping(), timeout=timeout_seconds))
    except Exception:
        return False
    finally:
        await client.aclose()


async def database_readiness(engine, required_tables: Iterable[str], components: dict[str, bool | str] | None = None):
    checks: dict[str, bool] = {}
    try:
        async with engine.connect() as connection:
            for table in required_tables:
                if not table.isidentifier():
                    raise ValueError("invalid readiness table")
                result = await connection.execute(text("SELECT to_regclass(:name)"), {"name": f"public.{table}"})
                checks[f"table:{table}"] = result.scalar_one_or_none() is not None
    except Exception:
        checks["postgres"] = False
    else:
        checks["postgres"] = True
    for name, value in (components or {}).items():
        if value == "probe-rabbitmq":
            checks[name] = await probe_rabbitmq()
        elif value == "probe-redis":
            checks[name] = await probe_redis()
        else:
            checks[name] = bool(value)
    ready = all(checks.values())
    return JSONResponse(
        status_code=200 if ready else 503,
        content={"status": "ready" if ready else "not_ready", "checks": checks},
    )
