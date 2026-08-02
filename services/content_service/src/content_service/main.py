from contextlib import asynccontextmanager
import asyncio
import os

from fastapi import Depends, FastAPI
from common.security.rbac import require_content_mutation
from common.security.middleware import JWTAuthenticationMiddleware
from common.db_readiness import require_schema_table
from common.readiness import database_readiness

from content_service.api.api_lesson_content import (
    router as lesson_content_router
)
from content_service.db import db_init_models
from content_service.db.db_base import Base
from content_service.db.db_session import engine
from content_service.messaging.messaging_rabbit import (
    RabbitConnection
)
from content_service.messaging.messaging_rpc_client import (
    rabbit_rpc_client
)
from content_service.api.api_lesson_attachment import (
    router as lesson_attachment_router
)
from content_service.api.api_lesson_link import (
    router as lesson_link_router
)
from content_service.api.api_homework import (
    router as homework_router
)
from content_service.api.api_homework_attachment import (
    router as homework_attachment_router
)
from content_service.api.api_homework_submission import (
    router as homework_submission_router
)
from content_service.api.api_submission_attachment import (
    router as submission_attachment_router
)
from content_service.messaging.messaging_event_publisher import (
    content_event_publisher
)
from content_service.db.db_session import AsyncSessionLocal
from content_service.models.model_event_outbox import EventOutbox
from content_service.messaging.messaging_config import rabbitmq_settings
from common.outbox_worker import OutboxWorker


API_PREFIX = "/api/v1"
outbox_worker: OutboxWorker | None = None


# =====================================================
# LIFESPAN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global outbox_worker
    print(
        "🚀 Starting Content Service...",
        flush=True
    )

    outbox_worker = OutboxWorker(session_factory=AsyncSessionLocal, model=EventOutbox, exchange_name=rabbitmq_settings.exchange, producer="content-service", url=rabbitmq_settings.url)
    outbox_task = asyncio.create_task(outbox_worker.run_forever())

    # =========================
    # Database
    # =========================

    try:
        if os.getenv("AUTO_CREATE_TABLES", "false").lower() == "true":
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        else:
            async with engine.connect() as conn:
                await require_schema_table(conn, "homeworks")

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
    # RabbitMQ event publisher
    # =========================

    try:
        await content_event_publisher.start()

        print(
            "📨 RabbitMQ event publisher started",
            flush=True
        )

    except Exception as error:
        print(
            f"❌ RabbitMQ event publisher startup failed: "
            f"{error}",
            flush=True
        )

    print(
        "✅ Content Service started",
        flush=True
    )

    yield

    await outbox_worker.stop()
    outbox_task.cancel()
    try:
        await outbox_task
    except asyncio.CancelledError:
        pass

    # =========================
    # Graceful shutdown
    # =========================

    print(
        "🛑 Stopping Content Service...",
        flush=True
    )

    # =========================
    # Stop event publisher
    # =========================

    try:
        await content_event_publisher.stop()

    except Exception as error:
        print(
            f"Event publisher shutdown error: {error}",
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
    # Close database engine
    # =========================

    try:
        await engine.dispose()

    except Exception as error:
        print(
            f"Database shutdown error: {error}",
            flush=True
        )

    print(
        "✅ Content Service stopped",
        flush=True
    )


# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="Content Service",
    description="""
Content Service микросервиса платформы ВШП Студент.

Отвечает за:
- материалы занятий;
- текстовые материалы;
- файлы уроков;
- презентации;
- изображения;
- видео;
- полезные ссылки;
- домашние задания;
- работы студентов;
- файлы домашних работ;
- проверку и результаты домашних заданий.

Не отвечает за:
- пользователей;
- авторизацию;
- группы;
- расписание;
- новости;
- чаты;
- уведомления.

Занятия получаются из schedule-service.
Пользователи получаются из user-service.
Группы получаются из academic-service.
""",
    version="1.0.0",
    lifespan=lifespan
)


# =====================================================
# ROUTES
# =====================================================

app.add_middleware(JWTAuthenticationMiddleware)

app.include_router(
    lesson_content_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_content_mutation)]
)

app.include_router(
    lesson_attachment_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_content_mutation)]
)

app.include_router(
    lesson_link_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_content_mutation)]
)

app.include_router(
    homework_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_content_mutation)]
)

app.include_router(
    homework_attachment_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_content_mutation)]
)

app.include_router(
    homework_submission_router,
    prefix=API_PREFIX
)
app.include_router(
    submission_attachment_router,
    prefix=API_PREFIX
)

# =====================================================
# ROOT
# =====================================================

@app.get("/")
async def root():
    return {
        "service": "content-service",
        "status": "ok"
    }


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
async def health():
    return {
        "service": "content-service",
        "status": "ok",
        "rpc_client_started": rabbit_rpc_client.started,
        "event_publisher_started": (
            content_event_publisher.started
        )
    }


@app.get("/ready")
async def ready():
    components = {"rabbitmq": "probe-rabbitmq", "redis": "probe-redis", "outbox_worker": bool(outbox_worker and outbox_worker.started)}
    return await database_readiness(engine, ("homeworks", "lesson_contents"), components)
