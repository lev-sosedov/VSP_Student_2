import asyncio, os
from logging.config import fileConfig
from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from content_service.db.db_base import Base
from content_service.models.model_event_outbox import EventOutbox  # noqa: F401
from content_service.db import db_init_models  # noqa: F401
config = context.config
if config.config_file_name is not None: fileConfig(config.config_file_name)
target_metadata = Base.metadata
database_url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
def run_migrations_offline() -> None:
    context.configure(url=database_url, target_metadata=target_metadata, literal_binds=True, compare_type=True)
    with context.begin_transaction(): context.run_migrations()
def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction(): context.run_migrations()
async def run_migrations_online() -> None:
    cfg = config.get_section(config.config_ini_section) or {}; cfg["sqlalchemy.url"] = database_url
    connectable = async_engine_from_config(cfg, prefix="sqlalchemy.", poolclass=pool.NullPool)
    async with connectable.connect() as connection: await connection.run_sync(do_run_migrations)
    await connectable.dispose()
if context.is_offline_mode(): run_migrations_offline()
else: asyncio.run(run_migrations_online())
