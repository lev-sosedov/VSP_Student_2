import asyncio
import os
from contextlib import asynccontextmanager
from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from common.security.middleware import JWTAuthenticationMiddleware
from common.db_readiness import require_schema_table

from communication_service.db import db_init_models
from communication_service.db.db_base import Base
from communication_service.db.db_session import engine
from communication_service.api.api_chat import (
    router as chat_router
)
from communication_service.api.api_chat_member import (
    router as chat_member_router
)
from communication_service.api.api_message import (
    router as message_router
)
from communication_service.api.api_message_read import (
    router as message_read_router
)
from communication_service.api.api_websocket import (
    router as websocket_router
)
from communication_service.messaging.messaging_rabbit import (
    RabbitConnection
)
from communication_service.messaging.messaging_rpc_client import (
    communication_rpc_client
)
from communication_service.api.api_message_attachment import (
    router as message_attachment_router
)
from communication_service.messaging.messaging_event_publisher import (
    communication_event_publisher
)
from communication_service.messaging.messaging_academic_event_consumer import (
    academic_event_consumer
)


API_PREFIX = "/api/v1"


# =====================================================
# Надёжный запуск RabbitMQ-компонентов
# =====================================================

async def start_rabbit_component(
    name: str,
    starter: Callable[[], Awaitable[None]]
) -> None:
    while True:
        try:
            await starter()
            return

        except asyncio.CancelledError:
            raise

        except Exception as error:
            print(
                f"⏳ {name}: RabbitMQ ещё не готов "
                f"({error}). Новая попытка через 5 секунд...",
                flush=True
            )

            await asyncio.sleep(5)


# =====================================================
# LIFESPAN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        "🚀 Starting Communication Service...",
        flush=True
    )

    # =========================
    # Database
    # =========================

    try:
        if os.getenv("AUTO_CREATE_TABLES", "false").lower() == "true":
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        else:
            async with engine.connect() as conn:
                await require_schema_table(conn, "chats")

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

    await start_rabbit_component(
        name="Communication RPC client",
        starter=communication_rpc_client.start
    )

    print(
        "🔁 Communication RPC client started",
        flush=True
    )

    # =========================
    # RabbitMQ event publisher
    # =========================

    await start_rabbit_component(
        name="Communication event publisher",
        starter=communication_event_publisher.start
    )

    print(
        "📨 Communication event publisher started",
        flush=True
    )

    # =========================
    # Academic group member events
    # =========================

    await start_rabbit_component(
        name="Academic member event consumer",
        starter=academic_event_consumer.start
    )

    print(
        "👥 Academic member event consumer started",
        flush=True
    )

    print(
        "✅ Communication Service started",
        flush=True
    )

    yield

    # =========================
    # Graceful shutdown
    # =========================

    print(
        "🛑 Stopping Communication Service...",
        flush=True
    )

    # =========================
    # Stop academic event consumer
    # =========================

    try:
        await academic_event_consumer.stop()

    except Exception as error:
        print(
            f"Academic event consumer shutdown error: {error}",
            flush=True
        )

    # =========================
    # Stop event publisher
    # =========================

    try:
        await communication_event_publisher.stop()

    except Exception as error:
        print(
            f"Event publisher shutdown error: {error}",
            flush=True
        )

    # =========================
    # Stop RPC client
    # =========================

    try:
        await communication_rpc_client.stop()

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
        "✅ Communication Service stopped",
        flush=True
    )


# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="Communication Service",
    description="""
Communication Service микросервиса платформы ВШП Студент.

Отвечает за:
- личные чаты;
- групповые чаты;
- чаты занятий;
- сообщения;
- ответы на сообщения;
- вложения;
- прочитано / не прочитано;
- закреплённые чаты и сообщения;
- WebSocket;
- события RabbitMQ.

Не отвечает за:
- пользователей;
- авторизацию;
- учебные группы;
- расписание;
- уведомления.

Пользователи получаются из user-service.
Группы получаются из academic-service.
Занятия получаются из schedule-service.
""",
    version="1.0.0",
    lifespan=lifespan
)

# =====================================================
# ROUTES
# =====================================================


app.add_middleware(JWTAuthenticationMiddleware)

app.include_router(
    chat_router,
    prefix=API_PREFIX
)

app.include_router(
    chat_member_router,
    prefix=API_PREFIX
)

app.include_router(
    message_router,
    prefix=API_PREFIX
)

app.include_router(
    message_read_router,
    prefix=API_PREFIX
)

app.include_router(
    websocket_router
)

app.include_router(
    message_attachment_router,
    prefix=API_PREFIX
)


# =====================================================
# ROOT
# =====================================================

@app.get("/")
async def root():
    return {
        "service": "communication-service",
        "status": "ok"
    }


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
async def health():
    return {
        "service": "communication-service",
        "status": "ok",
        "rpc_client_started": (
            communication_rpc_client.started
        ),
        "event_publisher_started": (
            communication_event_publisher.started
        )
    }
