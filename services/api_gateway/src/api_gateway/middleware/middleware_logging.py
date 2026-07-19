import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        started_at = time.perf_counter()

        response = await call_next(request)

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        request_id = getattr(request.state, "request_id", "-")

        print(
            "[API Gateway] "
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration_ms={duration_ms} "
            f"request_id={request_id}"
        )

        return response