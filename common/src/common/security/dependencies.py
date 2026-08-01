"""FastAPI dependencies for strict bearer-token authentication."""

from functools import lru_cache

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from common.security.config import JWTVerificationConfig
from common.security.exceptions import (
    AuthenticationError,
    InvalidAuthorizationSchemeError,
    MissingTokenError,
)
from common.security.jwt_provider import JWTProvider
from common.security.principal import CurrentPrincipal


bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def get_jwt_provider() -> JWTProvider:
    return JWTProvider(JWTVerificationConfig.from_environment())


def authentication_http_exception(error: AuthenticationError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": error.code, "message": error.public_message},
        headers={"WWW-Authenticate": "Bearer"},
    )


def authenticate_credentials(
    authorization_header: str | None,
    credentials: HTTPAuthorizationCredentials | None,
    provider: JWTProvider,
) -> CurrentPrincipal:
    try:
        if authorization_header is None:
            raise MissingTokenError()
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise InvalidAuthorizationSchemeError()
        if not credentials.credentials.strip():
            raise MissingTokenError()
        return provider.verify_access_token(credentials.credentials)
    except AuthenticationError as exc:
        raise authentication_http_exception(exc) from exc


def get_current_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    provider: JWTProvider = Depends(get_jwt_provider),
) -> CurrentPrincipal:
    existing = getattr(request.state, "current_principal", None)
    if isinstance(existing, CurrentPrincipal):
        return existing
    return authenticate_credentials(
        request.headers.get("authorization"), credentials, provider
    )


def get_optional_principal(request: Request) -> CurrentPrincipal | None:
    """Return middleware-populated principal, allowing documented public GETs."""
    existing = getattr(request.state, "current_principal", None)
    return existing if isinstance(existing, CurrentPrincipal) else None
