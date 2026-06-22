from sqlalchemy.ext.asyncio import (create_async_engine, AsyncSession, async_sessionmaker)

from auth_service.db.base import Base
from auth_service.core.core_config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True
)


async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():

    async with async_session() as session:
        yield session