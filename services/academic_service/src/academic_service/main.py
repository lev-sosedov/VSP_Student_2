from contextlib import asynccontextmanager

from fastapi import FastAPI

from academic_service.api.api_branch import (
    router as branch_router
)
from academic_service.api.api_branch_address import (
    router as branch_address_router
)
from academic_service.api.api_direction import (
    router as direction_router
)
from academic_service.api.api_education_plan import (
    router as education_plan_router
)
from academic_service.api.api_education_plan_module import (
    router as education_plan_module_router
)
from academic_service.api.api_group import (
    router as group_router
)
from academic_service.api.api_group_member import (
    router as group_member_router
)
from academic_service.api.api_module import (
    router as module_router
)
from academic_service.db import db_init_models
from academic_service.db.db_base import Base
from academic_service.db.db_session import engine
from academic_service.events.events_consumer import (
    academic_consumer
)
from academic_service.messaging.messaging_rabbit import (
    RabbitConnection
)
from academic_service.messaging.messaging_rpc_client import (
    rabbit_rpc_client
)
from academic_service.messaging.messaging_rpc_server import (
    academic_rpc_server
)


API_PREFIX = "/api/v1"


# =====================================================
# LIFESPAN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        "🚀 Starting Academic Service...",
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
    # RabbitMQ event consumer
    # =========================

    try:
        await academic_consumer.start()

        print(
            "🐰 RabbitMQ consumer started",
            flush=True
        )

    except Exception as error:
        print(
            f"❌ RabbitMQ consumer startup failed: {error}",
            flush=True
        )

    # =========================
    # RabbitMQ RPC client
    # Academic Service -> User Service
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
    # Academic RPC server
    # Other services -> Academic Service
    # =========================

    try:
        await academic_rpc_server.start()

        print(
            "🔁 Academic RPC server started",
            flush=True
        )

    except Exception as error:
        print(
            f"❌ Academic RPC server startup failed: {error}",
            flush=True
        )

    print(
        "✅ Academic Service started",
        flush=True
    )

    # После yield приложение работает.
    yield

    # =================================================
    # Graceful shutdown
    # =================================================

    print(
        "🛑 Stopping Academic Service...",
        flush=True
    )

    # =========================
    # Stop Academic RPC server
    # =========================

    try:
        await academic_rpc_server.stop()

    except Exception as error:
        print(
            f"Academic RPC server shutdown error: {error}",
            flush=True
        )

    # =========================
    # Stop RPC client
    # =========================

    try:
        await rabbit_rpc_client.stop()

    except AttributeError:
        # Временная совместимость, если в старом
        # RabbitRpcClient ещё нет метода stop().
        pass

    except Exception as error:
        print(
            f"RPC client shutdown error: {error}",
            flush=True
        )

    # =========================
    # Stop event consumer
    # =========================

    try:
        await academic_consumer.stop()

    except Exception as error:
        print(
            f"Consumer shutdown error: {error}",
            flush=True
        )

    # =========================
    # Close shared RabbitMQ connection
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
        "✅ Academic Service stopped",
        flush=True
    )


# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="Academic Service",
    description="""
Academic Service микросервиса платформы ВШП Студент.

Отвечает за:
- филиалы;
- адреса филиалов;
- направления;
- учебные планы;
- модули;
- группы;
- участников групп.

Не отвечает за:
- пользователей;
- авторизацию;
- JWT;
- платежи;
- расписание занятий.

Пользователи получаются из user-service.
Расписание занятий хранится в schedule-service.
""",
    version="1.0.0",
    lifespan=lifespan
)


# =====================================================
# ROUTES
# =====================================================

app.include_router(
    module_router,
    prefix=API_PREFIX
)

app.include_router(
    education_plan_router,
    prefix=API_PREFIX
)

app.include_router(
    education_plan_module_router,
    prefix=API_PREFIX
)

app.include_router(
    direction_router,
    prefix=API_PREFIX
)

app.include_router(
    group_router,
    prefix=API_PREFIX
)

app.include_router(
    group_member_router,
    prefix=API_PREFIX
)

app.include_router(
    branch_router,
    prefix=API_PREFIX
)

app.include_router(
    branch_address_router,
    prefix=API_PREFIX
)


# =====================================================
# ROOT
# =====================================================

@app.get("/")
async def root():
    return {
        "service": "academic-service",
        "status": "ok"
    }


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
async def health():
    return {
        "service": "academic-service",
        "status": "ok"
    }