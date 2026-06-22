from fastapi import FastAPI

from user_service.api.users  import router as user_router

app = FastAPI(
    title="VSH Student - User Service",
    description="""
User Service микросервиса платформы ВШП Студент.

Отвечает за:
- пользователей
- профили
- роли
- статусы аккаунтов
- управление доступом

Не отвечает за:
- авторизацию
- JWT генерацию
- регистрацию

Auth выполняется через auth-service.
""",
    version="1.0.0",
)


# ==========================
# API ROUTES
# ==========================

app.include_router(user_router,prefix="/api/v1")


# ==========================
# HEALTH CHECK
# ==========================

@app.get(
    "/health",
    tags=["System"],
    summary="Проверка состояния сервиса",
    description="""
Используется:
- Docker healthcheck
- Kubernetes probe
- мониторинг
"""
)
async def health_check():

    return {
        "service": "user-service",
        "status": "ok"
    }