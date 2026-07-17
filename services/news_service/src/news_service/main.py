from contextlib import asynccontextmanager

from fastapi import FastAPI

from news_service.db import db_init_models
from news_service.db.db_base import Base
from news_service.db.db_session import engine
from news_service.api.api_post import (
    router as post_router
)
from news_service.api.api_post_media import (
    router as post_media_router
)
from news_service.api.api_post_view import (
    router as post_view_router
)
from news_service.api.api_post_comment import (
    router as post_comment_router
)
from news_service.messaging.messaging_rabbit import (
    RabbitConnection
)
from news_service.messaging.messaging_rpc_client import (
    news_rpc_client
)


API_PREFIX = "/api/v1"


# =====================================================
# LIFESPAN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        "🚀 Starting News Service...",
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
        await news_rpc_client.start()

        print(
            "🔁 News RPC client started",
            flush=True
        )

    except Exception as error:
        print(
            f"❌ News RPC client failed: {error}",
            flush=True
        )

    print(
        "✅ News Service started",
        flush=True
    )

    yield

    try:
        await news_rpc_client.stop()

    except Exception as error:
        print(
            f"RPC client shutdown error: {error}",
            flush=True
        )

    try:
        await RabbitConnection.close()

    except Exception as error:
        print(
            f"RabbitMQ shutdown error: {error}",
            flush=True
        )

    # =========================
    # Graceful shutdown
    # =========================

    print(
        "🛑 Stopping News Service...",
        flush=True
    )

    try:
        await engine.dispose()

    except Exception as error:
        print(
            f"Database shutdown error: {error}",
            flush=True
        )

    print(
        "✅ News Service stopped",
        flush=True
    )


# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="News Service",
    description="""
News Service микросервиса платформы ВШП Студент.

Отвечает за:
- публикации школы;
- новости;
- статьи;
- мероприятия;
- достижения;
- важные объявления;
- фото;
- видео;
- аудио;
- документы;
- просмотры;
- комментарии;
- ответы на комментарии;
- публикацию и архивирование;
- закрепление публикаций;
- уведомления о новых публикациях.

Не отвечает за:
- пользователей;
- авторизацию;
- учебные группы;
- расписание;
- домашние задания;
- сообщения;
- системные уведомления.

Пользователи получаются из user-service.
Уведомления отправляются через RabbitMQ.
""",
    version="1.0.0",
    lifespan=lifespan
)

# =====================================================
# ROUTES
# =====================================================

app.include_router(
    post_router,
    prefix=API_PREFIX
)

app.include_router(
    post_media_router,
    prefix=API_PREFIX
)

app.include_router(
    post_view_router,
    prefix=API_PREFIX
)

app.include_router(
    post_comment_router,
    prefix=API_PREFIX
)


# =====================================================
# ROOT
# =====================================================

@app.get("/")
async def root():
    return {
        "service": "news-service",
        "status": "ok"
    }


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
async def health():
    return {
        "service": "news-service",
        "status": "ok",
        "rpc_client_started": (
            news_rpc_client.started
        )
    }