"""Typed identity produced by strict access-token validation."""

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping

from common.utils.enum_role import RoleType


@dataclass(frozen=True, slots=True)
class CurrentPrincipal:
    user_id: int
    role: RoleType
    token_type: str
    token_version: int
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    issuer: str | None = None
    audience: str | tuple[str, ...] | None = None
    jti: str | None = None
    claims: Mapping[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        if isinstance(self.user_id, bool) or self.user_id <= 0:
            raise ValueError("user_id must be a positive integer")
        if not isinstance(self.role, RoleType):
            raise ValueError("role must be a RoleType")
        if self.token_type != "access":
            raise ValueError("CurrentPrincipal requires an access token")
        if isinstance(self.token_version, bool) or self.token_version <= 0:
            raise ValueError("token_version must be a positive integer")
        object.__setattr__(self, "claims", MappingProxyType(dict(self.claims)))
