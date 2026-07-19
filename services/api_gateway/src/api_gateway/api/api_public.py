from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import Response

from api_gateway.proxy.proxy_http import proxy_http_request
from api_gateway.proxy.proxy_routes import (
    get_public_service_name,
    get_public_service_url,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Public API"],
)

PUBLIC_API_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "HEAD",
]


@router.api_route(
    "/{upstream_path:path}",
    methods=PUBLIC_API_METHODS,
)
async def proxy_public_api(
    upstream_path: str,
    request: Request,
) -> Response:
    service_name = get_public_service_name(upstream_path)
    service_url = get_public_service_url(upstream_path)

    if service_name is None or service_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "unknown_api_route",
                "message": (
                    f"Маршрут '/api/v1/{upstream_path}' "
                    "не зарегистрирован в API Gateway"
                ),
            },
        )

    return await proxy_http_request(
        request,
        service_url=service_url,
        upstream_path=f"/api/v1/{upstream_path}",
    )