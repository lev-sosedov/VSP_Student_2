import os
from pathlib import Path
from types import SimpleNamespace

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("RABBITMQ_USERNAME", "test")
os.environ.setdefault("RABBITMQ_PASSWORD", "test")

from common.parent_authorization import ParentAuthorizationClient
from user_service.messaging import messaging_rpc_server as rpc_module


class _Result:
    def __init__(self, row):
        self._row = row

    def scalar_one_or_none(self):
        return self._row


class _Session:
    def __init__(self, row=None, error=None):
        self.row = row
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def execute(self, _query):
        if self.error:
            raise self.error
        return _Result(self.row)


def _session_factory(row=None, error=None):
    return lambda: _Session(row, error)


@pytest.mark.asyncio
async def test_parent_rpc_authorizes_active_link(monkeypatch):
    monkeypatch.setattr(rpc_module, "AsyncSessionLocal", _session_factory(SimpleNamespace()))
    response = await rpc_module.UserRpcServer().parent_has_student(
        {"parent_user_id": 1, "student_user_id": 2}
    )
    assert response == {
        "success": True,
        "authorized": True,
        "parent_user_id": 1,
        "student_user_id": 2,
    }


@pytest.mark.asyncio
async def test_parent_rpc_denies_unlinked_or_missing_links(monkeypatch):
    monkeypatch.setattr(rpc_module, "AsyncSessionLocal", _session_factory(None))
    response = await rpc_module.UserRpcServer().parent_has_student(
        {"parent_user_id": 1, "student_user_id": 99}
    )
    assert response["success"] is True
    assert response["authorized"] is False
    assert response["reason"] == "parent_student_link_not_found"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"parent_user_id": 0, "student_user_id": 2},
        {"parent_user_id": True, "student_user_id": 2},
        {"parent_user_id": "bad", "student_user_id": 2},
    ],
)
async def test_parent_rpc_rejects_invalid_identifiers(payload):
    response = await rpc_module.UserRpcServer().parent_has_student(payload)
    assert response == {
        "success": False,
        "authorized": False,
        "reason": "invalid_request",
    }


@pytest.mark.asyncio
async def test_parent_rpc_database_failure_is_deny(monkeypatch):
    monkeypatch.setattr(
        rpc_module,
        "AsyncSessionLocal",
        _session_factory(error=RuntimeError("database unavailable")),
    )
    response = await rpc_module.UserRpcServer().parent_has_student(
        {"parent_user_id": 1, "student_user_id": 2}
    )
    assert response == {
        "success": False,
        "authorized": False,
        "reason": "authorization_unavailable",
    }


@pytest.mark.asyncio
async def test_parent_rpc_client_accepts_only_valid_authorization():
    async def call(_method, _payload, **_kwargs):
        return {
            "success": True,
            "authorized": True,
            "parent_user_id": 1,
            "student_user_id": 2,
        }

    assert await ParentAuthorizationClient(call).has_student(1, 2) is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response",
    [
        None,
        {},
        {"success": True, "authorized": True},
        {"success": True, "authorized": True, "parent_user_id": "1", "student_user_id": 2},
        {"success": True, "authorized": True, "parent_user_id": 1, "student_user_id": 2, "reason": 7},
    ],
)
async def test_parent_rpc_client_rejects_malformed(response):
    async def call(_method, _payload, **_kwargs):
        return response

    assert await ParentAuthorizationClient(call).has_student(1, 2) is False


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [TimeoutError(), ConnectionError("unavailable")])
async def test_parent_rpc_client_timeout_or_unavailable_is_deny(error):
    async def call(_method, _payload, **_kwargs):
        raise error

    assert await ParentAuthorizationClient(call).has_student(1, 2) is False


def test_parent_rpc_dispatch_and_contract_are_internal_only():
    source = Path(r"services/user_service/src/user_service/messaging/messaging_rpc_server.py").read_text(encoding="utf-8")
    assert '"parent.authorization.has_student"' in source
    assert 'response = await self.parent_has_student(payload)' in source
    assert "parent_user_id" in source and "student_user_id" in source
    assert "ParentStudentLink.parent_id" in source
    assert "ParentStudentLink.student_id" in source
    assert "return None" not in source[source.index("async def parent_has_student"):]


def test_existing_parent_http_mutations_remain_admin_only():
    source = Path(r"services/user_service/src/user_service/api/api_parent_students.py").read_text(encoding="utf-8")
    assert source.count("Depends(require_admin())") >= 4
    assert "Depends(get_current_principal)" in source
