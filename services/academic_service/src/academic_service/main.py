from contextlib import asynccontextmanager
import asyncio
import os

from fastapi import Depends, FastAPI
from common.security.rbac import require_admin_mutations
from common.security.middleware import JWTAuthenticationMiddleware
from common.db_readiness import require_schema_table
from common.readiness import database_readiness

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
from academic_service.db.db_session import AsyncSessionLocal
from academic_service.models.model_event_outbox import EventOutbox
from academic_service.messaging.messaging_config import rabbitmq_settings
from common.outbox_worker import OutboxWorker


API_PREFIX = "/api/v1"
outbox_worker: OutboxWorker | None = None


# =====================================================
# LIFESPAN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global outbox_worker
    outbox_worker = OutboxWorker(session_factory=AsyncSessionLocal, model=EventOutbox, exchange_name=rabbitmq_settings.exchange, producer="academic-service", url=rabbitmq_settings.url)
    outbox_task = asyncio.create_task(outbox_worker.run_forever())
    print(
        "🚀 Starting Academic Service...",
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
                await require_schema_table(conn, "groups")

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
    await outbox_worker.stop()
    outbox_task.cancel()

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
        await outbox_task
    except asyncio.CancelledError:
        pass
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

app.add_middleware(
    JWTAuthenticationMiddleware,
    public_paths={"/api/v1/branches"},
)

app.include_router(
    module_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin_mutations)]
)

app.include_router(
    education_plan_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin_mutations)]
)

app.include_router(
    education_plan_module_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin_mutations)]
)

app.include_router(
    direction_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin_mutations)]
)

app.include_router(
    group_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin_mutations)]
)

app.include_router(
    group_member_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin_mutations)]
)

app.include_router(
    branch_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin_mutations)]
)

app.include_router(
    branch_address_router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin_mutations)]
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


@app.get("/ready")
async def ready():
    return await database_readiness(engine, ("groups",), {"rabbitmq": "probe-rabbitmq", "outbox_worker": bool(outbox_worker and outbox_worker.started)})
