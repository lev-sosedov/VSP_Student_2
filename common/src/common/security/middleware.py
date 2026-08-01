"""Service-side JWT enforcement for complete router surfaces."""

from collections.abc import Awaitable, Callable, Collection
import os

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from common.security.dependencies import get_jwt_provider
from common.security.exceptions import AuthenticationError, MissingTokenError


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        public_paths: Collection[str] = (),
        public_get_prefixes: Collection[str] = (),
    ) -> None:
        super().__init__(app)
        base_public = {"/", "/health"}
        if os.environ.get("ENVIRONMENT", os.environ.get("APP_ENV", "development")) != "production":
            base_public.update({"/docs", "/redoc", "/openapi.json"})
        self.public_paths = frozenset(public_paths) | frozenset(base_public)
        self.public_get_prefixes = tuple(public_get_prefixes)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if self._is_public(request):
            return await call_next(request)
        try:
            header = request.headers.get("authorization")
            if not header:
                raise MissingTokenError()
            scheme, _, token = header.partition(" ")
            if scheme.lower() != "bearer" or not token.strip():
                raise MissingTokenError()
            request.state.current_principal = get_jwt_provider().verify_access_token(token)
        except AuthenticationError as exc:
            return JSONResponse(
                status_code=401,
                content={"detail": {"code": exc.code, "message": exc.public_message}},
                headers={"WWW-Authenticate": "Bearer"},
            )
        return await call_next(request)

    def _is_public(self, request: Request) -> bool:
        if request.method == "OPTIONS" or request.url.path in self.public_paths:
            return True
        return request.method == "GET" and any(
            request.url.path.startswith(prefix) for prefix in self.public_get_prefixes
        )
