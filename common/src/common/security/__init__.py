"""Shared, opt-in authentication infrastructure for backend services."""

from common.security.jwt_provider import JWTProvider
from common.security.principal import CurrentPrincipal

__all__ = ["CurrentPrincipal", "JWTProvider"]
