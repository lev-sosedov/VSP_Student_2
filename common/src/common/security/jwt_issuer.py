"""Strict RS256 token issuance for auth-service only."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from common.identity import ResolvedIdentity


@dataclass(frozen=True, slots=True)
class JWTIssuerConfig:
    private_key: str
    algorithm: str
    issuer: str
    audience: str
    access_minutes: int = 30
    refresh_days: int = 14

    def __post_init__(self) -> None:
        if self.algorithm != "RS256":
            raise ValueError("JWT issuance requires RS256")
        if not self.private_key.strip() or not self.issuer or not self.audience:
            raise ValueError("complete JWT issuer configuration is required")


class JWTIssuer:
    def __init__(self, config: JWTIssuerConfig):
        self.config = config

    def create_pair(self, identity: ResolvedIdentity) -> dict[str, str]:
        return {
            "access_token": self._encode(identity, "access", timedelta(minutes=self.config.access_minutes)),
            "refresh_token": self._encode(identity, "refresh", timedelta(days=self.config.refresh_days)),
            "token_type": "bearer",
        }

    def _encode(self, identity: ResolvedIdentity, token_type: str, lifetime: timedelta) -> str:
        now = datetime.now(timezone.utc)
        claims = {
            "sub": str(identity.user_id),
            "auth_user_id": identity.auth_user_id,
            "role": identity.role.value,
            "token_version": identity.token_version,
            "type": token_type,
            "iat": now,
            "nbf": now,
            "exp": now + lifetime,
            "iss": self.config.issuer,
            "aud": self.config.audience,
            "jti": str(uuid4()),
        }
        return jwt.encode(claims, self.config.private_key, algorithm="RS256")
