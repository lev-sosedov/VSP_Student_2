"""Service-side JWT enforcement for complete router surfaces."""

from collections.abc import Awaitable, Callable, Collection
import os

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from common.security.dependencies import get_jwt_provider
from common.security.exceptions import AuthenticationError, MissingTokenError
from common.security.user_state import get_user_security_state


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        public_paths: Collection[str] = (),
        public_get_paths: Collection[str] = (),
        public_get_prefixes: Collection[str] = (),
    ) -> None:
        super().__init__(app)
        # Exact infrastructure probes only.  Do not broaden this to prefixes:
        # `/ready/test` and similarly named application routes remain protected.
        base_public = {"/", "/health", "/ready"}
        if os.environ.get("ENVIRONMENT", os.environ.get("APP_ENV", "development")) != "production":
            base_public.update({"/docs", "/redoc", "/openapi.json"})
        self.public_paths = frozenset(public_paths) | frozenset(base_public)
        self.public_get_paths = frozenset(public_get_paths)
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
            principal = request.state.current_principal
            state = await get_user_security_state(int(principal.claims["auth_user_id"]))
            if state is not None:
                if state.status in {"blocked", "deleted", "inactive"}:
                    return JSONResponse(status_code=401, content={"detail": "User is not active"})
                if state.token_version != principal.token_version:
                    return JSONResponse(status_code=401, content={"detail": "Token has been revoked"})
                if state.role != principal.role.value:
                    return JSONResponse(status_code=401, content={"detail": "Token role is stale"})
        except AuthenticationError as exc:
            return JSONResponse(
                status_code=401,
                content={"detail": {"code": exc.code, "message": exc.public_message}},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception:
            # Missing state is intentionally allowed for existing users. Redis
            # failures fail closed for mutations and fail open for reads.
            if request.method not in {"GET", "HEAD", "OPTIONS"}:
                return JSONResponse(status_code=503, content={"detail": "Authorization state unavailable"})
        return await call_next(request)

    def _is_public(self, request: Request) -> bool:
        if request.method == "OPTIONS" or request.url.path in self.public_paths:
            return True
        return request.method == "GET" and (
            request.url.path in self.public_get_paths
            or any(request.url.path.startswith(prefix) for prefix in self.public_get_prefixes)
        )
