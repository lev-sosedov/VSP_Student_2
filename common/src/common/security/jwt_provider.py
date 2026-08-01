"""Strict RS256 access-token verification for backend services."""

from datetime import datetime, timezone
from typing import Any

import jwt
from jwt import exceptions as jwt_exceptions

from common.security.config import JWTVerificationConfig
from common.security.exceptions import (
    ExpiredTokenError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidRoleError,
    InvalidSignatureError,
    InvalidSubjectError,
    InvalidTokenTypeError,
    InvalidTokenVersionError,
    MalformedTokenError,
    MissingClaimError,
    TokenNotYetValidError,
    UnsupportedAlgorithmError,
)
from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType


REQUIRED_ACCESS_CLAIMS = (
    "sub",
    "auth_user_id",
    "role",
    "type",
    "token_version",
    "iat",
    "nbf",
    "exp",
    "iss",
    "aud",
    "jti",
)


class JWTProvider:
    """Verify tokens using only a configured public key and algorithm."""

    def __init__(self, config: JWTVerificationConfig) -> None:
        self._config = config

    def verify_access_token(self, token: str) -> CurrentPrincipal:
        claims = self.verify_token(token, expected_type="access")

        user_id = self._parse_positive_int(claims.get("sub"), InvalidSubjectError)
        self._parse_positive_int(claims.get("auth_user_id"), InvalidSubjectError)
        token_version = self._parse_positive_int(
            claims.get("token_version"), InvalidTokenVersionError
        )

        try:
            role = RoleType(claims.get("role"))
        except (TypeError, ValueError) as exc:
            raise InvalidRoleError() from exc

        return CurrentPrincipal(
            user_id=user_id,
            role=role,
            token_type="access",
            token_version=token_version,
            issued_at=self._timestamp_to_datetime(claims["iat"]),
            expires_at=self._timestamp_to_datetime(claims["exp"]),
            issuer=claims["iss"],
            audience=self._parse_audience(claims["aud"]),
            jti=claims.get("jti"),
            claims=claims,
        )

    def verify_refresh_token(self, token: str) -> dict[str, Any]:
        claims = self.verify_token(token, expected_type="refresh")
        self._parse_positive_int(claims.get("sub"), InvalidSubjectError)
        self._parse_positive_int(claims.get("auth_user_id"), InvalidSubjectError)
        self._parse_positive_int(claims.get("token_version"), InvalidTokenVersionError)
        try:
            RoleType(claims.get("role"))
        except (TypeError, ValueError) as exc:
            raise InvalidRoleError() from exc
        return claims

    def verify_token(self, token: str, *, expected_type: str) -> dict[str, Any]:
        if not isinstance(token, str) or not token.strip():
            raise MalformedTokenError()

        try:
            header = jwt.get_unverified_header(token)
        except jwt_exceptions.PyJWTError as exc:
            raise MalformedTokenError() from exc

        token_algorithm = header.get("alg")
        if token_algorithm == "none" or token_algorithm != self._config.algorithm:
            raise UnsupportedAlgorithmError()

        try:
            claims = jwt.decode(
                token,
                self._config.public_key,
                algorithms=[self._config.algorithm],
                audience=self._config.audience,
                issuer=self._config.issuer,
                leeway=self._config.clock_skew_seconds,
                options={
                    "require": list(REQUIRED_ACCESS_CLAIMS),
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_iss": True,
                    "verify_aud": True,
                },
            )
        except jwt_exceptions.ExpiredSignatureError as exc:
            raise ExpiredTokenError() from exc
        except jwt_exceptions.ImmatureSignatureError as exc:
            raise TokenNotYetValidError() from exc
        except jwt_exceptions.InvalidIssuerError as exc:
            raise InvalidIssuerError() from exc
        except jwt_exceptions.InvalidAudienceError as exc:
            raise InvalidAudienceError() from exc
        except jwt_exceptions.MissingRequiredClaimError as exc:
            raise MissingClaimError() from exc
        except jwt_exceptions.InvalidSignatureError as exc:
            raise InvalidSignatureError() from exc
        except jwt_exceptions.InvalidAlgorithmError as exc:
            raise UnsupportedAlgorithmError() from exc
        except jwt_exceptions.PyJWTError as exc:
            raise MalformedTokenError() from exc

        if claims.get("type") != expected_type:
            raise InvalidTokenTypeError()
        return claims

    @staticmethod
    def _parse_positive_int(value: Any, error_type: type[Exception]) -> int:
        if isinstance(value, bool):
            raise error_type()
        try:
            parsed = int(value)
        except (TypeError, ValueError) as exc:
            raise error_type() from exc
        if parsed <= 0 or str(parsed) != str(value):
            raise error_type()
        return parsed

    @staticmethod
    def _timestamp_to_datetime(value: int | float) -> datetime:
        return datetime.fromtimestamp(value, tz=timezone.utc)

    @staticmethod
    def _parse_audience(value: str | list[str]) -> str | tuple[str, ...]:
        if isinstance(value, str):
            return value
        return tuple(value)
