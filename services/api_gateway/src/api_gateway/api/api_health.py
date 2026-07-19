import asyncio
from typing import Any

import httpx
from fastapi import APIRouter

from api_gateway.clients.client_http import http_client
from api_gateway.core.core_config import settings


router = APIRouter(tags=["Health"])


async def check_service(
    service_name: str,
    service_url: str,
) -> tuple[str, dict[str, Any]]:
    health_url = f"{service_url.rstrip('/')}/health"

    try:
        response = await http_client.client.get(health_url)

        return service_name, {
            "status": (
                "healthy"
                if response.status_code == 200
                else "unhealthy"
            ),
            "status_code": response.status_code,
            "url": service_url,
        }

    except httpx.TimeoutException:
        return service_name, {
            "status": "timeout",
            "status_code": None,
            "url": service_url,
        }

    except httpx.HTTPError:
        return service_name, {
            "status": "unavailable",
            "status_code": None,
            "url": service_url,
        }


@router.get("/health")
async def gateway_health() -> dict[str, Any]:
    return {
        "service": "api-gateway",
        "status": "healthy",
    }


@router.get("/health/services")
async def services_health() -> dict[str, Any]:
    checks = await asyncio.gather(
        *[
            check_service(service_name, service_url)
            for service_name, service_url
            in settings.service_urls.items()
        ]
    )

    services = dict(checks)

    all_healthy = all(
        service["status"] == "healthy"
        for service in services.values()
    )

    return {
        "service": "api-gateway",
        "status": "healthy" if all_healthy else "degraded",
        "services": services,
    }