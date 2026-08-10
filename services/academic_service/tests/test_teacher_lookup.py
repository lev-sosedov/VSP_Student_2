import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("RABBITMQ_USERNAME", "test")
os.environ.setdefault("RABBITMQ_PASSWORD", "test")

from types import SimpleNamespace

import pytest

from academic_service.clients.client_user_rpc import UserRpcClient
from academic_service.repositories.repository_group_member import GroupMemberRepository
from academic_service.services.service_group_member import GroupMemberService


class GroupRepo:
    async def get_by_id(self, _group_id):
        return SimpleNamespace(id=1)


@pytest.mark.asyncio
async def test_teacher_lookup_skips_stale_candidates_in_membership_id_order():
    memberships = [
        SimpleNamespace(id=10, user_id=1002),  # missing User profile
        SimpleNamespace(id=20, user_id=43),    # inactive user
        SimpleNamespace(id=30, user_id=44),    # wrong role
        SimpleNamespace(id=40, user_id=4),      # first valid teacher
        SimpleNamespace(id=50, user_id=5),      # second valid teacher
    ]

    class Repo:
        async def get_teachers(self, _group_id):
            return memberships

    class Users:
        async def get_user_by_id(self, user_id):
            return {
                1002: None,
                43: {"id": 43, "role": "teacher", "is_active": False},
                44: {"id": 44, "role": "student", "is_active": True},
                4: {"id": 4, "role": "teacher", "is_active": True},
                5: {"id": 5, "role": "teacher", "is_active": True},
            }[user_id]

    result = await GroupMemberService(Repo(), GroupRepo(), Users()).get_teacher(1)
    assert result.id == 40
    assert result.user_id == 4


@pytest.mark.asyncio
async def test_repository_get_teachers_builds_deterministic_ordered_query():
    class ScalarResult:
        def all(self):
            return []

        def scalars(self):
            return self

    class Session:
        def __init__(self):
            self.statement = None

        async def execute(self, statement):
            self.statement = statement
            return ScalarResult()

    session = Session()
    await GroupMemberRepository(session).get_teachers(1)
    assert session.statement is not None
    order_by = list(session.statement._order_by_clauses)
    assert len(order_by) == 1
    assert str(order_by[0].element) == "group_members.id"
    assert order_by[0].modifier.__name__ == "asc_op"


@pytest.mark.asyncio
async def test_teacher_lookup_returns_none_when_no_valid_teacher_exists():
    class Repo:
        async def get_teachers(self, _group_id):
            return [SimpleNamespace(id=1, user_id=1002), SimpleNamespace(id=2, user_id=44)]

    class Users:
        async def get_user_by_id(self, user_id):
            return None if user_id == 1002 else {"id": 44, "role": "student", "is_active": True}

    assert await GroupMemberService(Repo(), GroupRepo(), Users()).get_teacher(1) is None


@pytest.mark.asyncio
async def test_teacher_lookup_fails_closed_on_user_rpc_error():
    class Repo:
        async def get_teachers(self, _group_id):
            return [SimpleNamespace(id=1, user_id=1002)]

    class Users:
        async def get_user_by_id(self, _user_id):
            raise TimeoutError("timeout")

    with pytest.raises(RuntimeError):
        await GroupMemberService(Repo(), GroupRepo(), Users()).get_teacher(1)


@pytest.mark.asyncio
async def test_user_rpc_missing_profile_is_successful_null_and_skipped():
    class Rpc:
        async def call(self, **_kwargs):
            return {"success": True, "user": None}

    assert await UserRpcClient(Rpc()).get_user_by_id(1002) is None


@pytest.mark.asyncio
async def test_user_rpc_malformed_profile_fails_closed():
    class Rpc:
        async def call(self, **_kwargs):
            return {"success": True, "user": {"id": 1002}}

    with pytest.raises(RuntimeError):
        await UserRpcClient(Rpc()).get_user_by_id(1002)
