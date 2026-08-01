import os
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("RABBITMQ_USERNAME", "test")
os.environ.setdefault("RABBITMQ_PASSWORD", "test")
import pytest
from fastapi import HTTPException
from starlette.requests import Request

from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType
from communication_service.api.dependencies import require_chat_member


def req(chat_id: int) -> Request:
    return Request({"type": "http", "method": "GET", "path": f"/chats/{chat_id}", "path_params": {"chat_id": chat_id}, "query_string": b"", "headers": [], "state": {}})


@pytest.mark.asyncio
async def test_chat_member_dependency_rejects_non_member(monkeypatch):
    class Repo:
        def __init__(self, session): pass
        async def get_member(self, chat_id, user_id): return None
    monkeypatch.setattr("communication_service.api.dependencies.ChatMemberRepository", Repo)
    with pytest.raises(HTTPException) as error:
        await require_chat_member(req(3), CurrentPrincipal(7, RoleType.ADMIN, "access", 1), object())
    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_chat_member_dependency_allows_active_member(monkeypatch):
    class Repo:
        def __init__(self, session): pass
        async def get_member(self, chat_id, user_id): return type("Member", (), {"is_active": True})()
    monkeypatch.setattr("communication_service.api.dependencies.ChatMemberRepository", Repo)
    principal = CurrentPrincipal(7, RoleType.STUDENT, "access", 1)
    assert await require_chat_member(req(3), principal, object()) is principal
