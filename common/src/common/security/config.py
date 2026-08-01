"""Environment-backed configuration for JWT verification.

This is separate from the provider so loading key material and validating
deployment settings are not mixed with token parsing.
"""

from dataclasses import dataclass
import os
from pathlib import Path


SUPPORTED_VERIFICATION_ALGORITHMS = frozenset({"RS256"})


@dataclass(frozen=True, slots=True)
class JWTVerificationConfig:
    algorithm: str
    issuer: str
    audience: str
    public_key: str
    clock_skew_seconds: int = 30

    def __post_init__(self) -> None:
        if self.algorithm not in SUPPORTED_VERIFICATION_ALGORITHMS:
            raise ValueError("unsupported configured JWT algorithm")
        if not self.issuer.strip() or not self.audience.strip():
            raise ValueError("JWT issuer and audience are required")
        if not self.public_key.strip():
            raise ValueError("JWT public key is required")
        if isinstance(self.clock_skew_seconds, bool) or self.clock_skew_seconds < 0:
            raise ValueError("JWT clock skew must be a non-negative integer")

    @classmethod
    def from_environment(cls) -> "JWTVerificationConfig":
        key_path_value = os.environ.get("JWT_PUBLIC_KEY_PATH", "").strip()
        if not key_path_value:
            raise ValueError("JWT_PUBLIC_KEY_PATH is required")
        key_path = Path(key_path_value)
        public_key = key_path.read_text(encoding="utf-8")
        return cls(
            algorithm=os.environ.get("JWT_ALGORITHM", "RS256"),
            issuer=os.environ.get("JWT_ISSUER", "vsp-auth-service"),
            audience=os.environ.get("JWT_AUDIENCE", "vsp-student-api"),
            public_key=public_key,
            clock_skew_seconds=int(os.environ.get("JWT_CLOCK_SKEW_SECONDS", "30")),
        )
