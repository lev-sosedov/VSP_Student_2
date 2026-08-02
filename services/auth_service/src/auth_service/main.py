from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from auth_service.api.api_auth import router as auth_router
from auth_service.db.db_session import engine
from auth_service.db.db_base import Base
from auth_service.models.models_auth_user import AuthUser
from auth_service.messaging.messaging_rabbit import publish_user_created
from auth_service.messaging.messaging_user_events import consume_user_events_forever
import asyncio
import os
from auth_service.models.models_processed_user_event import ProcessedUserEvent
from common.security.middleware import JWTAuthenticationMiddleware
from common.db_readiness import require_schema_table
from common.readiness import database_readiness


@asynccontextmanager
async def lifespan(app: FastAPI):

    if os.getenv("AUTO_CREATE_TABLES", "false").lower() == "true":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        async with engine.connect() as conn:
            await require_schema_table(conn, "auth_users")

    sync_task = asyncio.create_task(consume_user_events_forever())

    yield

    sync_task.cancel()
    try:
        await sync_task
    except asyncio.CancelledError:
        pass



app = FastAPI(
lifespan=lifespan, #-------------
    title="VSH Student - Auth Service",
    description="""
Auth Service микросервиса платформы ВШП Студент.

Отвечает за:
- регистрацию пользователей
- аутентификацию
- проверку паролей
- генерацию JWT токенов
- обновление access/refresh токенов
- управление сессиями

Не отвечает за:
- хранение профиля пользователя
- роли и права доступа
- пользовательские данные

User данные находятся в user-service.
""",
    version="1.0.0",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================
# API ROUTES
# ==========================

app.add_middleware(
    JWTAuthenticationMiddleware,
    public_paths={"/api/v1/auth/register", "/api/v1/auth/login", "/api/v1/auth/refresh"},
)

app.include_router(
    auth_router,
    prefix="/api/v1"
)


# ==========================
# HEALTH CHECK
# ==========================

@app.get(
    "/health",
    tags=["System"],
    summary="Проверка состояния сервиса",
    description="""
Используется:
- Docker healthcheck
- Kubernetes probe
- мониторинг
"""
)
async def health_check():

    return {
        "service": "auth-service",
        "status": "ok"
    }


@app.get("/ready", tags=["System"])
async def ready_check():
    return await database_readiness(engine, ("auth_users", "refresh_sessions", "processed_user_events"), {"rabbitmq": True, "redis": True})
