import pytest
from fastapi import HTTPException

from communication_service.api import api_chat


class _FakeService:
    instances = []

    def __init__(self, session):
        self.calls = []
        self.__class__.instances.append(self)

    async def ensure_admin_chat(self, **kwargs):
        self.calls.append(("admin", kwargs))

    async def ensure_private_chat(self, **kwargs):
        self.calls.append(("teacher", kwargs))


@pytest.mark.asyncio
async def test_parent_sync_deduplicates_teacher_across_groups(monkeypatch):
    _FakeService.instances.clear()
    monkeypatch.setattr(api_chat, "ChatService", _FakeService)
    monkeypatch.setattr(api_chat.settings, "ADMIN_USER_ID", 99)

    async def call(*, method, payload, **kwargs):
        if method == "parent.authorization.students":
            return {"success": True, "student_ids": [7]}
        if method == "academic.authorization.user_groups":
            return {"success": True, "group_ids": [10, 11]}
        if method == "group_members.get_by_group":
            return {"success": True, "members": [{"user_id": 42}]}
        raise AssertionError(method)

    monkeypatch.setattr(api_chat.communication_rpc_client, "call_user", call)
    monkeypatch.setattr(api_chat.communication_rpc_client, "call_academic", call)

    await api_chat._sync_parent_private_chats(5, object())

    calls = _FakeService.instances[-1].calls
    assert [kind for kind, _ in calls] == ["admin", "teacher"]
    assert calls[1][1]["first_user_id"] == 5
    assert calls[1][1]["second_user_id"] == 42


@pytest.mark.asyncio
async def test_parent_sync_malformed_rpc_fails_without_creating_chats(monkeypatch):
    _FakeService.instances.clear()
    monkeypatch.setattr(api_chat, "ChatService", _FakeService)
    monkeypatch.setattr(api_chat.settings, "ADMIN_USER_ID", 99)

    async def call(*, method, payload, **kwargs):
        if method == "parent.authorization.students":
            return {"success": True, "student_ids": [7]}
        return None

    monkeypatch.setattr(api_chat.communication_rpc_client, "call_user", call)
    monkeypatch.setattr(api_chat.communication_rpc_client, "call_academic", call)

    with pytest.raises(HTTPException) as error:
        await api_chat._sync_parent_private_chats(5, object())
    assert error.value.status_code == 503
    assert _FakeService.instances[-1].calls == []


@pytest.mark.asyncio
async def test_parent_sync_rejects_invalid_configured_admin(monkeypatch):
    monkeypatch.setattr(api_chat.settings, "ADMIN_USER_ID", 0)
    with pytest.raises(HTTPException) as error:
        await api_chat._sync_parent_private_chats(5, object())
    assert error.value.status_code == 503
