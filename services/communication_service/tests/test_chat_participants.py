import os
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("RABBITMQ_USERNAME", "test")
os.environ.setdefault("RABBITMQ_PASSWORD", "test")

import pytest
from types import SimpleNamespace
from fastapi import HTTPException

from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType
from communication_service.api import api_chat


def chat():
    return SimpleNamespace(
        id=7, created_by=3, participant_one_id=3, participant_two_id=4,
        members=[SimpleNamespace(user_id=3, is_active=True), SimpleNamespace(user_id=4, is_active=True), SimpleNamespace(user_id=4, is_active=True)],
    )

@pytest.mark.asyncio
async def test_participants_include_legacy_and_canonical_ids_without_duplicates(monkeypatch):
    class Repo:
        def __init__(self, session): pass
        async def get_by_id(self, _chat_id, with_members=False): return chat()
    monkeypatch.setattr(api_chat, "ChatRepository", Repo)
    async def call_user(*, method, payload, **kwargs):
        assert payload["user_ids"] == [3, 4]
        return {"success": True, "users": [
            {"id": 3, "role": "admin", "user_name": "Admin", "last_name": None, "first_name": None, "avatar_url": None, "is_active": True},
            {"id": 4, "role": "teacher", "user_name": "Teacher", "last_name": None, "first_name": None, "avatar_url": None, "is_active": True},
        ]}
    monkeypatch.setattr(api_chat.communication_rpc_client, "call_user", call_user)
    result = await api_chat.get_chat_participants_endpoint(7, CurrentPrincipal(3, RoleType.ADMIN, "access", 1), object())
    assert [item.user_id for item in result.items] == [3, 4]

@pytest.mark.asyncio
async def test_participants_skip_missing_or_inactive_profiles(monkeypatch):
    class Repo:
        def __init__(self, session): pass
        async def get_by_id(self, _chat_id, with_members=False): return chat()
    monkeypatch.setattr(api_chat, "ChatRepository", Repo)
    async def call_user(*, method, payload, **kwargs):
        return {"success": True, "users": [{"id": 3, "role": "admin", "user_name": "Admin", "is_active": True}, {"id": 4, "role": "teacher", "is_active": False}]}
    monkeypatch.setattr(api_chat.communication_rpc_client, "call_user", call_user)
    result = await api_chat.get_chat_participants_endpoint(7, CurrentPrincipal(3, RoleType.ADMIN, "access", 1), object())
    assert [item.user_id for item in result.items] == [3]

@pytest.mark.asyncio
async def test_participants_malformed_rpc_is_503(monkeypatch):
    class Repo:
        def __init__(self, session): pass
        async def get_by_id(self, _chat_id, with_members=False): return chat()
    monkeypatch.setattr(api_chat, "ChatRepository", Repo)
    async def call_user(*, method, payload, **kwargs): return None
    monkeypatch.setattr(api_chat.communication_rpc_client, "call_user", call_user)
    with pytest.raises(HTTPException) as error:
        await api_chat.get_chat_participants_endpoint(7, CurrentPrincipal(3, RoleType.ADMIN, "access", 1), object())
    assert error.value.status_code == 503
