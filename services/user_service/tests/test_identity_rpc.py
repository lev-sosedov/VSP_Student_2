import os
from types import SimpleNamespace

import pytest
from sqlalchemy.exc import MultipleResultsFound

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost/test",
)
os.environ.setdefault("RABBITMQ_USERNAME", "test")
os.environ.setdefault("RABBITMQ_PASSWORD", "test")

from common.utils.enum_role import RoleType
from user_service.messaging import messaging_rpc_server as rpc_module


class FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None


@pytest.mark.asyncio
async def test_identity_rpc_returns_minimal_typed_contract(monkeypatch):
    user = SimpleNamespace(
        id=42,
        auth_id=7,
        role=RoleType.STUDENT,
        is_active=True,
        is_account_verified=True,
        hashed_password="must-not-leak",
        phone_number="must-not-leak",
    )

    class FakeRepository:
        def __init__(self, _session):
            pass

        async def get_by_auth_id(self, auth_user_id):
            assert auth_user_id == 7
            return user

    monkeypatch.setattr(rpc_module, "AsyncSessionLocal", FakeSession)
    monkeypatch.setattr(rpc_module, "UserRepository", FakeRepository)
    response = await rpc_module.UserRpcServer().resolve_identity_by_auth_id(
        {"auth_user_id": 7}
    )
    assert response["success"] is True
    assert response["identity"] == {
        "user_id": 42,
        "auth_user_id": 7,
        "role": "student",
        "is_active": True,
        "is_account_verified": True,
    }


@pytest.mark.asyncio
async def test_identity_rpc_returns_none_for_missing_profile(monkeypatch):
    class FakeRepository:
        def __init__(self, _session):
            pass

        async def get_by_auth_id(self, _auth_user_id):
            return None

    monkeypatch.setattr(rpc_module, "AsyncSessionLocal", FakeSession)
    monkeypatch.setattr(rpc_module, "UserRepository", FakeRepository)
    response = await rpc_module.UserRpcServer().resolve_identity_by_auth_id(
        {"auth_user_id": 7}
    )
    assert response == {"success": True, "identity": None}


@pytest.mark.asyncio
async def test_identity_rpc_rejects_duplicate_auth_links(monkeypatch):
    class FakeRepository:
        def __init__(self, _session):
            pass

        async def get_by_auth_id(self, _auth_user_id):
            raise MultipleResultsFound("duplicate")

    monkeypatch.setattr(rpc_module, "AsyncSessionLocal", FakeSession)
    monkeypatch.setattr(rpc_module, "UserRepository", FakeRepository)
    response = await rpc_module.UserRpcServer().resolve_identity_by_auth_id(
        {"auth_user_id": 7}
    )
    assert response["success"] is False
    assert response["error_code"] == "identity_link_duplicate"


def test_users_auth_id_has_unique_schema_constraint():
    assert rpc_module.User.__table__.c.auth_id.unique is True


@pytest.mark.asyncio
@pytest.mark.parametrize("auth_user_id", [None, 0, -1, "bad"])
async def test_identity_rpc_rejects_invalid_auth_id(auth_user_id):
    response = await rpc_module.UserRpcServer().resolve_identity_by_auth_id(
        {"auth_user_id": auth_user_id}
    )
    assert response["success"] is False
    assert response["error_code"] == "invalid_auth_user_id"
