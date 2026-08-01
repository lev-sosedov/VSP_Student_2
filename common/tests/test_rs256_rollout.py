from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
import pytest

from common.identity import ResolvedIdentity
from common.security.config import JWTVerificationConfig
from common.security.dependencies import get_current_principal
from common.security.jwt_issuer import JWTIssuer, JWTIssuerConfig
from common.security.jwt_provider import JWTProvider
from common.security.middleware import JWTAuthenticationMiddleware
from common.security.permissions import require_admin
from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType


@pytest.fixture
def rsa_pair() -> tuple[str, str]:
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


def identity(version: int = 3) -> ResolvedIdentity:
    return ResolvedIdentity(
        user_id=42,
        auth_user_id=7,
        role=RoleType.STUDENT,
        token_version=version,
        is_active=True,
        is_account_verified=True,
    )


def issuer(private_key: str) -> JWTIssuer:
    return JWTIssuer(JWTIssuerConfig(
        private_key=private_key,
        algorithm="RS256",
        issuer="vsp-auth-service",
        audience="vsp-student-api",
    ))


def provider(public_key: str) -> JWTProvider:
    return JWTProvider(JWTVerificationConfig(
        algorithm="RS256",
        issuer="vsp-auth-service",
        audience="vsp-student-api",
        public_key=public_key,
        clock_skew_seconds=0,
    ))


def test_issuer_creates_access_and_refresh_with_canonical_claims(rsa_pair):
    tokens = issuer(rsa_pair[0]).create_pair(identity())
    access = provider(rsa_pair[1]).verify_access_token(tokens["access_token"])
    refresh = provider(rsa_pair[1]).verify_refresh_token(tokens["refresh_token"])
    assert access.user_id == 42
    assert access.role is RoleType.STUDENT
    assert access.token_version == 3
    assert refresh["sub"] == "42"
    assert refresh["auth_user_id"] == 7
    assert refresh["type"] == "refresh"


def test_tokens_do_not_contain_profile_or_credential_data(rsa_pair):
    tokens = issuer(rsa_pair[0]).create_pair(identity())
    claims = jwt.decode(tokens["access_token"], options={"verify_signature": False})
    assert not set(claims) & {"phone", "phone_number", "email", "name", "password", "password_hash", "hashed_password"}


@pytest.mark.parametrize("token_type, expected", [("access", "refresh"), ("refresh", "access")])
def test_token_types_cannot_cross_endpoints(rsa_pair, token_type, expected):
    tokens = issuer(rsa_pair[0]).create_pair(identity())
    token = tokens["access_token"] if token_type == "access" else tokens["refresh_token"]
    with pytest.raises(Exception):
        if expected == "access":
            provider(rsa_pair[1]).verify_access_token(token)
        else:
            provider(rsa_pair[1]).verify_refresh_token(token)


def test_hs256_and_alg_none_are_rejected(rsa_pair):
    now = datetime.now(timezone.utc)
    claims = {"sub": "42", "auth_user_id": 7, "role": "student", "type": "access", "token_version": 1,
              "iat": now, "nbf": now, "exp": now + timedelta(minutes=5), "iss": "vsp-auth-service",
              "aud": "vsp-student-api", "jti": "jti"}
    hs = jwt.encode(claims, "not-an-rsa-key", algorithm="HS256")
    none = jwt.encode(claims, key="", algorithm="none")
    with pytest.raises(Exception):
        provider(rsa_pair[1]).verify_access_token(hs)
    with pytest.raises(Exception):
        provider(rsa_pair[1]).verify_access_token(none)


def test_middleware_public_and_protected_statuses(monkeypatch, rsa_pair):
    app = FastAPI()
    app.add_middleware(JWTAuthenticationMiddleware, public_paths={"/public"})

    @app.get("/public")
    async def public():
        return {"ok": True}

    @app.get("/protected")
    async def protected(principal: CurrentPrincipal = Depends(lambda: None)):
        return {"ok": True}

    configured_provider = lambda: provider(rsa_pair[1])
    monkeypatch.setattr("common.security.middleware.get_jwt_provider", configured_provider)
    monkeypatch.setattr("common.security.dependencies.get_jwt_provider", configured_provider)
    client = TestClient(app)
    assert client.get("/public").status_code == 200
    assert client.get("/protected").status_code == 401


def test_role_dependency_returns_forbidden_for_wrong_role(rsa_pair, monkeypatch):
    app = FastAPI()
    app.add_middleware(JWTAuthenticationMiddleware)

    @app.get("/admin")
    async def admin(_principal: CurrentPrincipal = Depends(require_admin())):
        return {"ok": True}

    configured_provider = lambda: provider(rsa_pair[1])
    monkeypatch.setattr("common.security.middleware.get_jwt_provider", configured_provider)
    monkeypatch.setattr("common.security.dependencies.get_jwt_provider", configured_provider)
    app.dependency_overrides[get_current_principal] = lambda: CurrentPrincipal(
        user_id=42, role=RoleType.STUDENT, token_type="access", token_version=1
    )
    tokens = issuer(rsa_pair[0]).create_pair(identity())
    response = TestClient(app).get("/admin", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert response.status_code == 403
