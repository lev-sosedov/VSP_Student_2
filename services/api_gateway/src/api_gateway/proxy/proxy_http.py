from collections.abc import Iterable

import httpx
from fastapi import HTTPException, Request, status
from fastapi.responses import Response

from api_gateway.clients.client_http import http_client


REQUEST_HEADERS_TO_REMOVE = {
    "host",
    "content-length",
    "connection",
}

RESPONSE_HEADERS_TO_REMOVE = {
    "content-length",
    "content-encoding",
    "transfer-encoding",
    "connection",
}


def _filter_headers(
    headers: Iterable[tuple[str, str]],
    excluded_headers: set[str],
) -> dict[str, str]:
    return {
        key: value
        for key, value in headers
        if key.lower() not in excluded_headers
    }


async def proxy_http_request(
    request: Request,
    *,
    service_url: str,
    upstream_path: str,
) -> Response:
    target_url = (
        f"{service_url.rstrip('/')}/"
        f"{upstream_path.lstrip('/')}"
    )

    request_headers = _filter_headers(
        request.headers.items(),
        REQUEST_HEADERS_TO_REMOVE,
    )

    request_headers["x-forwarded-host"] = request.headers.get("host", "")
    request_headers["x-forwarded-proto"] = request.url.scheme

    request_id = getattr(request.state, "request_id", None)

    if request_id:
        request_headers["x-request-id"] = request_id

    body = await request.body()

    try:
        upstream_response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=request_headers,
            params=request.query_params,
            content=body,
        )

    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "service_unavailable",
                "message": "Не удалось подключиться к микросервису",
                "service_url": service_url,
            },
        ) from exc

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "error": "gateway_timeout",
                "message": "Микросервис не ответил вовремя",
                "service_url": service_url,
            },
        ) from exc

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "bad_gateway",
                "message": "Ошибка обращения к микросервису",
            },
        ) from exc

    response_headers = _filter_headers(
        upstream_response.headers.items(),
        RESPONSE_HEADERS_TO_REMOVE,
    )

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
    )