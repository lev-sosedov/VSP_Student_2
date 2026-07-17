from contextlib import asynccontextmanager

from fastapi import FastAPI

from notification_service.db import db_init_models
from notification_service.db.db_base import Base
from notification_service.db.db_session import engine
from notification_service.api.api_notification_preference import (
    router as notification_preference_router
)
from notification_service.api.api_notification import (
    router as notification_router
)
from notification_service.events.events_consumer import (
    notification_event_consumer
)
from notification_service.messaging.messaging_rabbit import (
    RabbitConnection
)
from notification_service.messaging.messaging_rpc_client import (
    notification_rpc_client
)


API_PREFIX = "/api/v1"


# =====================================================
# LIFESPAN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        "🚀 Starting Notification Service...",
        flush=True
    )

    # =========================
    # Database
    # =========================

    try:
        async with engine.begin() as conn:
            await conn.run_sync(
                Base.metadata.create_all
            )

        print(
            "📦 Database tables created",
            flush=True
        )

    except Exception as error:
        print(
            f"❌ Database startup failed: {error}",
            flush=True
        )

        raise

    # =========================
    # RabbitMQ RPC client
    # =========================

    try:
        await notification_rpc_client.start()

        print(
            "🔁 Notification RPC client started",
            flush=True
        )

    except Exception as error:
        print(
            f"❌ Notification RPC client failed: {error}",
            flush=True
        )

    # =========================
    # RabbitMQ event consumer
    # =========================

    try:
        await notification_event_consumer.start()

        print(
            "🐰 Notification event consumer started",
            flush=True
        )

    except Exception as error:
        print(
            f"❌ Notification consumer failed: {error}",
            flush=True
        )

    print(
        "✅ Notification Service started",
        flush=True
    )

    yield

    # =========================
    # Graceful shutdown
    # =========================

    print(
        "🛑 Stopping Notification Service...",
        flush=True
    )

    # =========================
    # Stop event consumer
    # =========================

    try:
        await notification_event_consumer.stop()

    except Exception as error:
        print(
            f"Consumer shutdown error: {error}",
            flush=True
        )

    # =========================
    # Stop RPC client
    # =========================

    try:
        await notification_rpc_client.stop()

    except Exception as error:
        print(
            f"RPC client shutdown error: {error}",
            flush=True
        )

    # =========================
    # Close RabbitMQ
    # =========================

    try:
        await RabbitConnection.close()

    except Exception as error:
        print(
            f"RabbitMQ shutdown error: {error}",
            flush=True
        )

    # =========================
    # Close database
    # =========================

    try:
        await engine.dispose()

    except Exception as error:
        print(
            f"Database shutdown error: {error}",
            flush=True
        )

    print(
        "✅ Notification Service stopped",
        flush=True
    )


# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="Notification Service",
    description="""
Notification Service микросервиса платформы ВШП Студент.

Отвечает за:
- уведомления внутри сайта;
- получателей уведомлений;
- статусы доставки;
- прочитанные и непрочитанные уведомления;
- настройки уведомлений пользователей;
- тихие часы;
- обработку событий RabbitMQ;
- подготовку email, push и Telegram-уведомлений.

Не отвечает за:
- пользователей;
- авторизацию;
- расписание;
- учебные материалы;
- домашние задания;
- чаты;
- новости.

Пользователи получаются из user-service.
Группы получаются из academic-service.
События принимаются через RabbitMQ.
""",
    version="1.0.0",
    lifespan=lifespan
)

# =====================================================
# ROUTES
# =====================================================

app.include_router(
    notification_preference_router,
    prefix=API_PREFIX
)

app.include_router(
    notification_router,
    prefix=API_PREFIX
)


# =====================================================
# ROOT
# =====================================================

@app.get("/")
async def root():
    return {
        "service": "notification-service",
        "status": "ok"
    }


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
async def health():
    return {
        "service": "notification-service",
        "status": "ok",
        "rpc_client_started": (
            notification_rpc_client.started
        ),
        "event_consumer_started": (
            notification_event_consumer.started
        )
    }