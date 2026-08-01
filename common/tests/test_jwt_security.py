from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
import jwt
import pytest
from starlette.requests import Request

from common.security.config import JWTVerificationConfig
from common.security.dependencies import get_current_principal, get_jwt_provider
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
from common.security.jwt_provider import JWTProvider
from common.security.permissions import (
    require_admin,
    require_roles,
    require_self_or_admin,
    require_teacher_or_admin,
)
from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType


ISSUER = "test-auth-service"
AUDIENCE = "test-api"
# Represents user_service.users.id, never auth_service.auth_users.id.
CANONICAL_USER_ID = 42


@pytest.fixture(scope="session")
def rsa_keys() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("ascii")
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")
    return private_pem, public_pem


@pytest.fixture
def provider(rsa_keys: tuple[str, str]) -> JWTProvider:
    return JWTProvider(
        JWTVerificationConfig(
            algorithm="RS256",
            issuer=ISSUER,
            audience=AUDIENCE,
            public_key=rsa_keys[1],
            clock_skew_seconds=0,
        )
    )


def claims(**overrides: object) -> dict[str, object]:
    now = datetime.now(timezone.utc)
    result: dict[str, object] = {
        "sub": str(CANONICAL_USER_ID),
        "auth_user_id": 7,
        "role": RoleType.STUDENT.value,
        "type": "access",
        "token_version": 1,
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=5),
        "iss": ISSUER,
        "aud": AUDIENCE,
        "jti": "test-jti",
    }
    result.update(overrides)
    return result


def token(private_key: str, **overrides: object) -> str:
    return jwt.encode(claims(**overrides), private_key, algorithm="RS256")


def principal(role: RoleType, user_id: int = CANONICAL_USER_ID) -> CurrentPrincipal:
    return CurrentPrincipal(user_id, role, "access", 1)


def auth_client(provider: JWTProvider) -> TestClient:
    app = FastAPI()

    @app.get("/protected")
    def protected(current: CurrentPrincipal = Depends(get_current_principal)) -> int:
        return current.user_id

    app.dependency_overrides[get_jwt_provider] = lambda: provider
    return TestClient(app)


def request_with_path(**path_params: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
            "path_params": path_params,
        }
    )


def test_valid_rs256_access_token(provider: JWTProvider, rsa_keys: tuple[str, str]) -> None:
    assert provider.verify_access_token(token(rsa_keys[0])).user_id == CANONICAL_USER_ID


def test_valid_current_principal() -> None:
    current = principal(RoleType.TEACHER)
    assert current.role is RoleType.TEACHER and current.token_version == 1


def test_missing_authorization(provider: JWTProvider) -> None:
    response = auth_client(provider).get("/protected")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_wrong_authorization_scheme(provider: JWTProvider) -> None:
    response = auth_client(provider).get("/protected", headers={"Authorization": "Basic abc"})
    assert response.status_code == 401


def test_empty_bearer_token(provider: JWTProvider) -> None:
    response = auth_client(provider).get("/protected", headers={"Authorization": "Bearer "})
    assert response.status_code == 401


def test_malformed_jwt(provider: JWTProvider) -> None:
    with pytest.raises(MalformedTokenError):
        provider.verify_access_token("not-a-jwt")


def test_invalid_signature(provider: JWTProvider) -> None:
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    other_pem = other_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    with pytest.raises(InvalidSignatureError):
        provider.verify_access_token(jwt.encode(claims(), other_pem, algorithm="RS256"))


def test_expired_token(provider: JWTProvider, rsa_keys: tuple[str, str]) -> None:
    with pytest.raises(ExpiredTokenError):
        provider.verify_access_token(token(rsa_keys[0], exp=datetime.now(timezone.utc) - timedelta(seconds=1)))


def test_nbf_in_future(provider: JWTProvider, rsa_keys: tuple[str, str]) -> None:
    with pytest.raises(TokenNotYetValidError):
        provider.verify_access_token(token(rsa_keys[0], nbf=datetime.now(timezone.utc) + timedelta(minutes=1)))


def test_wrong_issuer(provider: JWTProvider, rsa_keys: tuple[str, str]) -> None:
    with pytest.raises(InvalidIssuerError):
        provider.verify_access_token(token(rsa_keys[0], iss="wrong"))


def test_wrong_audience(provider: JWTProvider, rsa_keys: tuple[str, str]) -> None:
    with pytest.raises(InvalidAudienceError):
        provider.verify_access_token(token(rsa_keys[0], aud="wrong"))


def test_refresh_token_rejected(provider: JWTProvider, rsa_keys: tuple[str, str]) -> None:
    with pytest.raises(InvalidTokenTypeError):
        provider.verify_access_token(token(rsa_keys[0], type="refresh"))


def test_missing_sub(provider: JWTProvider, rsa_keys: tuple[str, str]) -> None:
    payload = claims()
    del payload["sub"]
    with pytest.raises(MissingClaimError):
        provider.verify_access_token(jwt.encode(payload, rsa_keys[0], algorithm="RS256"))


def test_non_numeric_sub(provider: JWTProvider, rsa_keys: tuple[str, str]) -> None:
    with pytest.raises(InvalidSubjectError):
        provider.verify_access_token(token(rsa_keys[0], sub="abc"))


@pytest.mark.parametrize("value", ["0", "-1"])
def test_non_positive_sub(provider: JWTProvider, rsa_keys: tuple[str, str], value: str) -> None:
    with pytest.raises(InvalidSubjectError):
        provider.verify_access_token(token(rsa_keys[0], sub=value))


def test_missing_role(provider: JWTProvider, rsa_keys: tuple[str, str]) -> None:
    payload = claims()
    del payload["role"]
    with pytest.raises(MissingClaimError):
        provider.verify_access_token(jwt.encode(payload, rsa_keys[0], algorithm="RS256"))


def test_unknown_role(provider: JWTProvider, rsa_keys: tuple[str, str]) -> None:
    with pytest.raises(InvalidRoleError):
        provider.verify_access_token(token(rsa_keys[0], role="superuser"))


def test_missing_token_version(provider: JWTProvider, rsa_keys: tuple[str, str]) -> None:
    payload = claims()
    del payload["token_version"]
    with pytest.raises(MissingClaimError):
        provider.verify_access_token(jwt.encode(payload, rsa_keys[0], algorithm="RS256"))


@pytest.mark.parametrize("value", [0, -1, "bad"])
def test_invalid_token_version(provider: JWTProvider, rsa_keys: tuple[str, str], value: object) -> None:
    with pytest.raises(InvalidTokenVersionError):
        provider.verify_access_token(token(rsa_keys[0], token_version=value))


def test_unsupported_algorithm(provider: JWTProvider) -> None:
    encoded = jwt.encode(claims(), "test-only-secret-with-at-least-32-bytes", algorithm="HS256")
    with pytest.raises(UnsupportedAlgorithmError):
        provider.verify_access_token(encoded)


def test_none_algorithm(provider: JWTProvider) -> None:
    encoded = jwt.encode(claims(), key="", algorithm="none")
    with pytest.raises(UnsupportedAlgorithmError):
        provider.verify_access_token(encoded)


def test_require_roles_allowed() -> None:
    current = principal(RoleType.TEACHER)
    assert require_roles(RoleType.TEACHER)(principal=current) is current


def test_require_roles_forbidden() -> None:
    with pytest.raises(HTTPException) as error:
        require_roles(RoleType.TEACHER)(principal=principal(RoleType.STUDENT))
    assert error.value.status_code == 403


def test_require_admin_for_admin() -> None:
    assert require_admin()(principal=principal(RoleType.ADMIN)).role is RoleType.ADMIN


def test_require_admin_for_student() -> None:
    with pytest.raises(HTTPException) as error:
        require_admin()(principal=principal(RoleType.STUDENT))
    assert error.value.status_code == 403


def test_require_teacher_or_admin_for_teacher() -> None:
    assert require_teacher_or_admin()(principal=principal(RoleType.TEACHER)).role is RoleType.TEACHER


def test_require_teacher_or_admin_for_admin() -> None:
    assert require_teacher_or_admin()(principal=principal(RoleType.ADMIN)).role is RoleType.ADMIN


def test_require_teacher_or_admin_for_student() -> None:
    with pytest.raises(HTTPException) as error:
        require_teacher_or_admin()(principal=principal(RoleType.STUDENT))
    assert error.value.status_code == 403


def test_require_self_or_admin_for_owner() -> None:
    result = asyncio.run(
        require_self_or_admin()(request=request_with_path(user_id="42"), principal=principal(RoleType.STUDENT))
    )
    assert result.user_id == 42


def test_require_self_or_admin_for_admin() -> None:
    result = asyncio.run(
        require_self_or_admin()(request=request_with_path(user_id="99"), principal=principal(RoleType.ADMIN))
    )
    assert result.role is RoleType.ADMIN


def test_require_self_or_admin_for_other_user() -> None:
    with pytest.raises(HTTPException) as error:
        asyncio.run(
            require_self_or_admin()(request=request_with_path(user_id="99"), principal=principal(RoleType.STUDENT))
        )
    assert error.value.status_code == 403
