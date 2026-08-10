import os
from pathlib import Path

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("RABBITMQ_USERNAME", "test")
os.environ.setdefault("RABBITMQ_PASSWORD", "test")

from user_service.messaging import messaging_rpc_server as rpc_module


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [{}, {"user_ids": "1"}, {"user_ids": [True]}, {"user_ids": [0]}])
async def test_chat_profiles_rpc_rejects_invalid_payload(payload):
    response = await rpc_module.UserRpcServer().get_chat_profiles_by_ids(payload)
    assert response == {"success": False, "users": [], "error": "invalid_request"}


@pytest.mark.asyncio
async def test_chat_profiles_rpc_returns_safe_profile_fields(monkeypatch):
    class Session:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *_args):
            return None

    class User:
        id = 4
        role = "teacher"
        user_name = "Teacher"
        first_name = "Ivan"
        last_name = "Petrov"
        avatar_url = None
        is_active = True

    class Repository:
        def __init__(self, _session): pass
        async def get_by_ids(self, _ids): return [User()]

    monkeypatch.setattr(rpc_module, "AsyncSessionLocal", lambda: Session())
    monkeypatch.setattr(rpc_module, "UserRepository", Repository)
    response = await rpc_module.UserRpcServer().get_chat_profiles_by_ids({"user_ids": [4, 4, 404]})
    assert response == {"success": True, "users": [{"id": 4, "role": "teacher", "user_name": "Teacher", "first_name": "Ivan", "last_name": "Petrov", "avatar_url": None, "is_active": True}]}


def test_chat_participants_use_typed_rpc_and_no_question_mark_fallbacks():
    source = Path("services/communication_service/src/communication_service/api/api_chat.py").read_text(encoding="utf-8")
    assert 'users.get_chat_profiles_by_ids' in source
    segment = source[source.index('async def get_chat_participants_endpoint'):source.index('@router.get(\n    \"/{chat_id}\"', source.index('async def get_chat_participants_endpoint'))]
    assert '????????' not in segment
