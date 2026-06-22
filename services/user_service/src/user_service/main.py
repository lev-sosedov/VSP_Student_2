from fastapi import FastAPI
from contextlib import asynccontextmanager

from user_service.db.session import engine
from user_service.db.base import Base

from user_service.models.user import User


from user_service.api.users import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Creating database tables...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables ready")

    yield


app = FastAPI(
    title="VSH Student - User Service",
    description="""
User Service микросервиса платформы ВШП Студент.

Отвечает за:
- пользователей
- профили
- роли
- статусы аккаунтов
- управление доступом

Не отвечает за:
- авторизацию
- JWT генерацию
- регистрацию

Auth выполняется через auth-service.
""",
    version="1.0.0",
    lifespan=lifespan
)


# ==========================
# API ROUTES
# ==========================

app.include_router(
    user_router,
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
        "service": "user-service",
        "status": "ok"
    }


@app.get(
    "/",
    tags=["System"],
    summary="Корень сервиса"
)
async def root():

    return {
        "status": "ok",
        "service": "user-service"
    }