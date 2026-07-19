from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import Response

from api_gateway.proxy.proxy_http import proxy_http_request
from api_gateway.proxy.proxy_routes import get_service_url


router = APIRouter(
    prefix="/api/gateway",
    tags=["Proxy"],
)

PROXY_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "HEAD",
]


def _get_registered_service_url(service_name: str) -> str:
    service_url = get_service_url(service_name)

    if service_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "unknown_service",
                "message": f"Сервис '{service_name}' не зарегистрирован",
            },
        )

    return service_url


@router.api_route(
    "/{service_name}",
    methods=PROXY_METHODS,
)
async def proxy_service_root(
    service_name: str,
    request: Request,
) -> Response:
    service_url = _get_registered_service_url(service_name)

    return await proxy_http_request(
        request,
        service_url=service_url,
        upstream_path="/",
    )


@router.api_route(
    "/{service_name}/{upstream_path:path}",
    methods=PROXY_METHODS,
)
async def proxy_service_path(
    service_name: str,
    upstream_path: str,
    request: Request,
) -> Response:
    service_url = _get_registered_service_url(service_name)

    return await proxy_http_request(
        request,
        service_url=service_url,
        upstream_path=upstream_path,
    )