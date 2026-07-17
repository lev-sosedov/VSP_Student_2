from contextlib import asynccontextmanager

from fastapi import FastAPI

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


API_PREFIX = "/api/v1"


# =====================================================
# LIFESPAN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        "🚀 Starting Content Service...",
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

app.include_router(
    lesson_content_router,
    prefix=API_PREFIX
)

app.include_router(
    lesson_attachment_router,
    prefix=API_PREFIX
)

app.include_router(
    lesson_link_router,
    prefix=API_PREFIX
)

app.include_router(
    homework_router,
    prefix=API_PREFIX
)

app.include_router(
    homework_attachment_router,
    prefix=API_PREFIX
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