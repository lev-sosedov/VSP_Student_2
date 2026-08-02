"""Non-mutating startup checks for Alembic-managed service schemas."""
from sqlalchemy import text


async def require_schema_table(connection, table_name: str) -> None:
    if not table_name.isidentifier():
        raise ValueError("invalid schema readiness table")
    result = await connection.execute(
        text("SELECT to_regclass(:table_name)"),
        {"table_name": f"public.{table_name}"},
    )
    if result.scalar_one_or_none() is None:
        raise RuntimeError(
            f"database schema is not ready: table {table_name!r} is missing; "
            "run Alembic upgrade head before starting the service"
        )
