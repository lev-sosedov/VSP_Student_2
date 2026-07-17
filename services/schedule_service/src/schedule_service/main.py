from contextlib import asynccontextmanager

from fastapi import FastAPI

from schedule_service.api.api_lesson_generation import (
    router as lesson_generation_router
)
from schedule_service.api.api_lesson_schedule import (
    router as lesson_schedule_router
)
from schedule_service.api.api_room import (
    router as room_router
)
from schedule_service.api.api_schedule_change import (
    router as schedule_change_router
)
from schedule_service.api.api_schedule_template import (
    router as schedule_template_router
)
from schedule_service.db import db_init_models
from schedule_service.db.db_base import Base
from schedule_service.db.db_session import engine
from schedule_service.messaging.messaging_rabbit import (
    RabbitConnection
)
from schedule_service.messaging.messaging_rpc_client import (
    rabbit_rpc_client
)
from schedule_service.messaging.messaging_rpc_server import (
    schedule_rpc_server
)
from schedule_service.messaging.messaging_event_publisher import (
    schedule_event_publisher
)


API_PREFIX = "/api/v1"


# =====================================================
# LIFESPAN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        "🚀 Starting Schedule Service...",
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
    # RPC client
    # =========================

    try:
        await rabbit_rpc_client.start()

        print(
            "🔁 RabbitMQ RPC client started",
            flush=True
        )

    except Exception as error:
        print(
            f"❌ RabbitMQ RPC client startup failed: {error}",
            flush=True
        )

    # =========================
    # Schedule RPC server
    # =========================

    try:
        await schedule_rpc_server.start()

        print(
            "🔁 Schedule RPC server started",
            flush=True
        )

    except Exception as error:
        print(
            f"❌ Schedule RPC server startup failed: {error}",
            flush=True
        )

    # =========================
    # RabbitMQ event publisher
    # =========================

    try:
        await schedule_event_publisher.start()

        print(
            "📨 Schedule event publisher started",
            flush=True
        )

    except Exception as error:
        print(
            f"❌ Schedule event publisher failed: "
            f"{error}",
            flush=True
        )

    print(
        "✅ Schedule Service started",
        flush=True
    )

    yield

    # =========================
    # Graceful shutdown
    # =========================

    print(
        "🛑 Stopping Schedule Service...",
        flush=True
    )

    # =========================
    # Stop event publisher
    # =========================

    try:
        await schedule_event_publisher.stop()

    except Exception as error:
        print(
            f"Schedule event publisher shutdown error: "
            f"{error}",
            flush=True
        )

    # =========================
    # Stop Schedule RPC server
    # =========================

    try:
        await schedule_rpc_server.stop()

    except Exception as error:
        print(
            f"Schedule RPC server shutdown error: {error}",
            flush=True
        )

    # =========================
    # Stop RPC client
    # =========================

    try:
        await rabbit_rpc_client.stop()

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
        "✅ Schedule Service stopped",
        flush=True
    )


# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="Schedule Service",
    description="""
Schedule Service микросервиса платформы ВШП Студент.

Отвечает за:
- кабинеты;
- недельные шаблоны расписания;
- конкретные занятия;
- автоматическую генерацию занятий;
- дополнительные занятия;
- переносы;
- отмены;
- замены преподавателей;
- историю изменений;
- проверку конфликтов расписания.

Пользователи и преподаватели получаются из user-service.
Группы и филиалы получаются из academic-service.
""",
    version="1.0.0",
    lifespan=lifespan
)


# =====================================================
# ROUTES
# =====================================================

app.include_router(
    room_router,
    prefix=API_PREFIX
)

app.include_router(
    schedule_template_router,
    prefix=API_PREFIX
)

app.include_router(
    lesson_schedule_router,
    prefix=API_PREFIX
)

app.include_router(
    schedule_change_router,
    prefix=API_PREFIX
)

app.include_router(
    lesson_generation_router,
    prefix=API_PREFIX
)


# =====================================================
# ROOT
# =====================================================

@app.get("/")
async def root():
    return {
        "service": "schedule-service",
        "status": "ok"
    }


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
async def health():
    return {
        "service": "schedule-service",
        "status": "ok",
        "rpc_client_started": (
            rabbit_rpc_client.started
        ),
        "event_publisher_started": (
            schedule_event_publisher.started
        )
    }