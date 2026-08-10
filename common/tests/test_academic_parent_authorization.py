import os
from pathlib import Path
from types import SimpleNamespace

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("RABBITMQ_USERNAME", "test")
os.environ.setdefault("RABBITMQ_PASSWORD", "test")

from academic_service.messaging import messaging_rpc_server as rpc_module
from academic_service.api.api_group_member import get_parent_child_groups
from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType
from fastapi import HTTPException
from common.parent_authorization import ParentStudentGroupAuthorizationClient


class _Result:
    def __init__(self, row):
        self.row = row

    def scalar_one_or_none(self):
        return self.row


class _Session:
    def __init__(self, row):
        self.row = row

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def execute(self, _query):
        return _Result(self.row)


@pytest.mark.asyncio
async def test_academic_parent_group_rpc_authorizes_linked_student(monkeypatch):
    async def user_call(**_kwargs):
        return {
            "success": True,
            "authorized": True,
            "parent_user_id": 10,
            "student_user_id": 20,
        }

    monkeypatch.setattr(rpc_module.rabbit_rpc_client, "call", user_call)
    monkeypatch.setattr(
        rpc_module,
        "AsyncSessionLocal",
        lambda: _Session(SimpleNamespace(id=1, group_id=30, user_id=20)),
    )
    response = await rpc_module.AcademicRpcServer().authorization_parent_student_group(
        {"parent_user_id": 10, "student_user_id": 20, "group_id": 30}
    )
    assert response == {
        "success": True,
        "authorized": True,
        "parent_user_id": 10,
        "student_user_id": 20,
        "group_id": 30,
    }


@pytest.mark.asyncio
async def test_academic_parent_group_rpc_denies_missing_membership(monkeypatch):
    async def user_call(**_kwargs):
        return {"success": True, "authorized": True, "parent_user_id": 10, "student_user_id": 20}

    monkeypatch.setattr(rpc_module.rabbit_rpc_client, "call", user_call)
    monkeypatch.setattr(rpc_module, "AsyncSessionLocal", lambda: _Session(None))
    response = await rpc_module.AcademicRpcServer().authorization_parent_student_group(
        {"parent_user_id": 10, "student_user_id": 20, "group_id": 999}
    )
    assert response == {"success": True, "authorized": False, "reason": "student_group_membership_not_found"}


@pytest.mark.asyncio
async def test_academic_parent_group_rpc_denies_user_link_failure(monkeypatch):
    async def user_call(**_kwargs):
        return None

    monkeypatch.setattr(rpc_module.rabbit_rpc_client, "call", user_call)
    response = await rpc_module.AcademicRpcServer().authorization_parent_student_group(
        {"parent_user_id": 10, "student_user_id": 20, "group_id": 30}
    )
    assert response["success"] is False
    assert response["authorized"] is False


@pytest.mark.asyncio
async def test_academic_parent_group_rpc_rejects_invalid_ids():
    response = await rpc_module.AcademicRpcServer().authorization_parent_student_group(
        {"parent_user_id": True, "student_user_id": 20, "group_id": 30}
    )
    assert response == {"success": False, "authorized": False, "reason": "invalid_request"}


@pytest.mark.asyncio
@pytest.mark.parametrize("response", [None, {}, {"success": True, "authorized": True, "parent_user_id": 1}])
async def test_parent_group_client_rejects_malformed(response):
    async def call(_method, _payload, **_kwargs):
        return response

    client = ParentStudentGroupAuthorizationClient(call)
    assert await client.has_student_group(1, 2, 3) is False


@pytest.mark.asyncio
async def test_parent_group_client_rejects_id_mismatch():
    async def call(_method, _payload, **_kwargs):
        return {
            "success": True,
            "authorized": True,
            "parent_user_id": 999,
            "student_user_id": 2,
            "group_id": 3,
        }

    assert await ParentStudentGroupAuthorizationClient(call).has_student_group(1, 2, 3) is False


def test_parent_group_endpoint_uses_principal_and_is_read_only():
    source = Path("services/academic_service/src/academic_service/api/api_group_member.py").read_text(encoding="utf-8")
    block = source[source.index('"/parent/children/{student_id}"'):]
    block = block[:block.index('@router.get(', 1)]
    assert "Depends(get_current_principal)" in block
    assert "principal.user_id" in block
    assert "parent_id" not in block
    assert "get_parent_student_groups" in block


def test_academic_rpc_dispatch_is_registered():
    source = Path("services/academic_service/src/academic_service/messaging/messaging_rpc_server.py").read_text(encoding="utf-8")
    assert '"parent.authorization.has_student_group"' in source
    assert "authorization_parent_student_group" in source
class _EndpointService:
    async def get_parent_student_groups(self, parent_user_id, student_user_id):
        assert parent_user_id == 10
        if student_user_id != 20:
            raise PermissionError("not linked")
        return []

    async def get_active_student_groups(self, student_user_id):
        assert student_user_id == 20
        return []


def _principal(user_id, role):
    return CurrentPrincipal(user_id=user_id, role=role, token_type="access", token_version=1)


@pytest.mark.asyncio
async def test_parent_http_endpoint_uses_principal_and_denies_foreign_student():
    service = _EndpointService()
    assert await get_parent_child_groups(20, service, _principal(10, RoleType.PARENT)) == []
    with pytest.raises(HTTPException) as error:
        await get_parent_child_groups(21, service, _principal(10, RoleType.PARENT))
    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_parent_http_endpoint_keeps_admin_access_and_denies_student_role():
    service = _EndpointService()
    assert await get_parent_child_groups(20, service, _principal(1, RoleType.ADMIN)) == []
    with pytest.raises(HTTPException) as error:
        await get_parent_child_groups(20, service, _principal(20, RoleType.STUDENT))
    assert error.value.status_code == 403