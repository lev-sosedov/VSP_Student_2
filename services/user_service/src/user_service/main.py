import asyncio

from contextlib import asynccontextmanager
from fastapi import FastAPI

from user_service.db.db_base import Base
from user_service.db.db_session import engine, AsyncSessionLocal
from user_service.api.api_users import router as user_router
from user_service.services.service_user import UserService
from user_service.messaging.messaging_rabbit import consume_user_events
from user_service.messaging.messaging_rpc_server import user_rpc_server


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("🚀 Starting User Service...")

    # =========================
    # Database
    # =========================

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("📦 Database tables created")

    # =========================
    # RabbitMQ event consumer
    # auth-service → user-service
    # =========================

    async def start_consumer():
        while True:
            try:
                async with AsyncSessionLocal() as session:
                    service = UserService(session)

                    await consume_user_events(service)

            except asyncio.CancelledError:
                print("[User Events] Consumer stopped")
                raise

            except Exception as e:
                print(
                    "[User Events] RabbitMQ not ready, retry in 5 seconds:",
                    e
                )

                await asyncio.sleep(5)

    # =========================
    # RabbitMQ RPC server
    # academic-service → user-service
    # =========================

    async def start_rpc_server():
        while True:
            try:
                await user_rpc_server.start()

                print("🔁 User RPC server started")
                return

            except asyncio.CancelledError:
                print("[User RPC] Startup task stopped")
                raise

            except Exception as e:
                print(
                    "[User RPC] RabbitMQ not ready, retry in 5 seconds:",
                    e
                )

                await asyncio.sleep(5)

    consumer_task = asyncio.create_task(
        start_consumer()
    )

    rpc_task = asyncio.create_task(
        start_rpc_server()
    )

    print("✅ User Service started")

    yield

    # =========================
    # Graceful shutdown
    # =========================

    print("🛑 Stopping User Service...")

    consumer_task.cancel()
    rpc_task.cancel()

    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

    try:
        await rpc_task
    except asyncio.CancelledError:
        pass

    try:
        await user_rpc_server.stop()

    except Exception as e:
        print(
            "[User RPC] Shutdown error:",
            e
        )

    print("✅ User Service stopped")


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


# =========================
# API ROUTES
# =========================

app.include_router(
    user_router,
    prefix="/api/v1"
)


# =========================
# HEALTH CHECK
# =========================

@app.get(
    "/health",
    tags=["System"],
    summary="Проверка состояния сервиса"
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