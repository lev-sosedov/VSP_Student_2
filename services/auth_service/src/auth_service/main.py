from fastapi import FastAPI

from auth_service.api.api_auth import router as auth_router


app = FastAPI(
    title="VSH Student - Auth Service",
    description="""
Auth Service микросервиса платформы ВШП Студент.

Отвечает за:
- регистрацию пользователей
- аутентификацию
- проверку паролей
- генерацию JWT токенов
- обновление access/refresh токенов
- управление сессиями

Не отвечает за:
- хранение профиля пользователя
- роли и права доступа
- пользовательские данные

User данные находятся в user-service.
""",
    version="1.0.0",
)


# ==========================
# API ROUTES
# ==========================

app.include_router(
    auth_router,
    prefix="/api/v1"
)


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
        "service": "auth-service",
        "status": "ok"
    }