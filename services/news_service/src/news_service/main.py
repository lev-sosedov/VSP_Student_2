from contextlib import asynccontextmanager
import os

from fastapi import Depends, FastAPI
from common.security.rbac import require_admin_mutations
from common.security.middleware import JWTAuthenticationMiddleware
from common.db_readiness import require_schema_table
from common.readiness import database_readiness

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
from news_service.messaging.messaging_event_publisher import (
    news_event_publisher
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
        if os.getenv("AUTO_CREATE_TABLES", "false").lower() == "true":
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        else:
            async with engine.connect() as conn:
                await require_schema_table(conn, "posts")

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


    # =========================
    # RabbitMQ event publisher
    # =========================

    try:
        await news_event_publisher.start()

        print(
            "📨 News event publisher started",
            flush=True
        )

    except Exception as error:
        print(
            f"❌ News event publisher failed: "
            f"{error}",
            flush=True
        )

    print(
        "✅ News Service started",
        flush=True
    )

    yield

    # =========================
    # Graceful shutdown
    # =========================

    print(
        "🛑 Stopping News Service...",
        flush=True
    )

    # =========================
    # Stop event publisher
    # =========================

    try:
        await news_event_publisher.stop()

    except Exception as error:
        print(
            f"Event publisher shutdown error: "
            f"{error}",
            flush=True
        )

    # =========================
    # Stop RPC client
    # =========================

    try:
        await news_rpc_client.stop()

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

app.add_middleware(
    JWTAuthenticationMiddleware,
    public_get_paths={"/api/v1/posts"},
    public_get_prefixes={"/api/v1/posts/slug/"},
)

app.include_router(
    post_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin_mutations)]
)

app.include_router(
    post_media_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin_mutations)]
)

app.include_router(
    post_view_router,
    prefix=API_PREFIX
)

app.include_router(
    post_comment_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin_mutations)]
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
        ),
        "event_publisher_started": (
            news_event_publisher.started
        )
    }


@app.get("/ready")
async def ready():
    return await database_readiness(engine, ("posts",), {"rabbitmq": True, "redis": True})
