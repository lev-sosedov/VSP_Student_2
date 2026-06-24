from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from user_service.db.base import Base
from user_service.api.users import router as user_router
from user_service.services.user_service import UserService
from user_service.messaging.rabbit import consume_user_events
from user_service.db.session import (engine, AsyncSessionLocal)


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Creating database tables...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


    async def start_consumer():

        while True:
            try:
                async with AsyncSessionLocal() as session:

                    service = UserService(session)

                    await consume_user_events(service)

            except Exception as e:

                print(
                    "RabbitMQ not ready, retry in 5 seconds:",
                    e
                )

                await asyncio.sleep(5)


    asyncio.create_task(start_consumer())


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