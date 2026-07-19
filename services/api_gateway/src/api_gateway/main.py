from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_gateway.api.api_health import router as health_router
from api_gateway.api.api_proxy import router as proxy_router
from api_gateway.api.api_public import router as public_router
from api_gateway.clients.client_http import http_client
from api_gateway.core.core_config import settings
from api_gateway.middleware.middleware_logging import LoggingMiddleware
from api_gateway.middleware.middleware_request_id import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("🚀 Starting API Gateway...")

    await http_client.start()

    print("✅ API Gateway started")

    yield

    print("🛑 Stopping API Gateway...")

    await http_client.stop()

    print("✅ API Gateway stopped")


app = FastAPI(
    title=settings.APP_NAME,
    description="Единая точка входа для платформы ВШП Студент",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


app.include_router(health_router)

# Основные публичные маршруты для React и мобильного приложения.
app.include_router(public_router)

# Технический прокси для разработки и диагностики.
app.include_router(proxy_router)


@app.get("/", tags=["Gateway"])
async def root() -> dict[str, str]:
    return {
        "service": "api-gateway",
        "message": "VSP Student API Gateway is running",
        "docs": "/docs",
        "health": "/health",
        "services_health": "/health/services",
        "public_api": "/api/v1",
        "technical_proxy": "/api/gateway",
    }