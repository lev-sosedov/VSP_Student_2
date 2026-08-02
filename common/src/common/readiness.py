"""Shared non-sensitive readiness response helpers."""
from __future__ import annotations

from typing import Any, Iterable

from fastapi.responses import JSONResponse
from sqlalchemy import text


async def database_readiness(engine, required_tables: Iterable[str], components: dict[str, bool] | None = None):
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
    checks.update(components or {})
    ready = all(checks.values())
    return JSONResponse(
        status_code=200 if ready else 503,
        content={"status": "ready" if ready else "not_ready", "checks": checks},
    )
