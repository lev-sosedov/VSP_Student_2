import pytest

from common.security import user_state


class FakeRedis:
    data = {}
    async def hgetall(self, key):
        return self.data.get(key, {})
    async def hset(self, key, mapping):
        self.data[key] = mapping
    async def aclose(self):
        pass


@pytest.mark.asyncio
async def test_missing_state_is_non_blocking(monkeypatch):
    monkeypatch.setattr(user_state.Redis, "from_url", lambda *a, **k: FakeRedis())
    assert await user_state.get_user_security_state(999) is None


@pytest.mark.asyncio
async def test_state_round_trip_contains_version_role_status(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(user_state.Redis, "from_url", lambda *a, **k: fake)
    await user_state.set_user_security_state(auth_user_id=7, token_version=3, role="teacher", status="active")
    state = await user_state.get_user_security_state(7)
    assert state is not None
    assert (state.token_version, state.role, state.status) == (3, "teacher", "active")
