from contextlib import asynccontextmanager

from fastapi import FastAPI

from schedule_service.api.api_schedule_template import (
    router as schedule_template_router
)
from schedule_service.api.api_lesson_schedule import (
    router as lesson_schedule_router
)
from schedule_service.api.api_schedule_change import (
    router as schedule_change_router
)
from schedule_service.api.api_room import router as room_router
from schedule_service.db.db_base import Base
from schedule_service.db.db_session import engine
from schedule_service.db import db_init_models

API_PREFIX = "/api/v1"




# =====================================================
# LIFESPAN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Schedule Service...")

    # =========================
    # Database
    # =========================

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("📦 Database tables created")
    print("✅ Schedule Service started")

    yield

    # =========================
    # Graceful shutdown
    # =========================

    print("🛑 Stopping Schedule Service...")

    await engine.dispose()

    print("✅ Schedule Service stopped")


# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="Schedule Service",
    description="""
Schedule Service микросервиса платформы ВШП Студент.

Отвечает за:
- кабинеты
- недельные шаблоны расписания
- конкретные занятия
- дополнительные занятия
- переносы занятий
- отмены занятий
- замены преподавателей
- историю изменений расписания

Не отвечает за:
- пользователей
- авторизацию
- группы
- филиалы
- учебные планы
- материалы занятий

Пользователи получаются из user-service.
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
        "status": "ok"
    }
