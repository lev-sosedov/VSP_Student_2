import os
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("RABBITMQ_USERNAME", "test")
os.environ.setdefault("RABBITMQ_PASSWORD", "test")

import pytest
from types import SimpleNamespace

from academic_service.services.service_group_member import GroupMemberService


class Repo:
    async def get_teachers(self, _group_id):
        return [SimpleNamespace(user_id=1002), SimpleNamespace(user_id=4)]

class GroupRepo:
    async def get_by_id(self, _group_id):
        return SimpleNamespace(id=1)

@pytest.mark.asyncio
async def test_teacher_lookup_skips_missing_then_returns_active_teacher():
    class Users:
        async def get_user_by_id(self, user_id):
            return None if user_id == 1002 else {"id": 4, "role": "teacher", "is_active": True}
    result = await GroupMemberService(Repo(), GroupRepo(), Users()).get_teacher(1)
    assert result.user_id == 4

@pytest.mark.asyncio
async def test_teacher_lookup_skips_duplicate_and_wrong_role():
    class Users:
        async def get_user_by_id(self, user_id):
            return {"id": user_id, "role": "student", "is_active": True} if user_id == 1002 else {"id": user_id, "role": "teacher", "is_active": False}
    assert await GroupMemberService(Repo(), GroupRepo(), Users()).get_teacher(1) is None

@pytest.mark.asyncio
async def test_teacher_lookup_fails_closed_on_user_rpc_error():
    class Users:
        async def get_user_by_id(self, _user_id):
            raise TimeoutError("timeout")
    with pytest.raises(RuntimeError):
        await GroupMemberService(Repo(), GroupRepo(), Users()).get_teacher(1)
