from auth_service.repositories.repository_refresh_session import hash_refresh_token
from auth_service.repositories.repository_login_attempt import LoginAttemptRepository


def test_refresh_tokens_are_stored_as_one_way_hashes():
    token = "opaque-refresh-token"
    digest = hash_refresh_token(token)
    assert digest != token
    assert len(digest) == 64
    assert digest == hash_refresh_token(token)


def test_audit_repository_never_stores_plain_phone():
    class DB:
        def add(self, item): self.item = item
        async def commit(self): pass
    import asyncio
    db = DB()
    asyncio.run(LoginAttemptRepository(db).record(
        phone="79990001122", success=False, reason_code="invalid_password",
        ip_address="127.0.0.1", user_agent="test"))
    assert db.item.phone_hash != "79990001122"
    assert db.item.success is False


def test_refresh_repository_uses_row_lock_for_rotation():
    from pathlib import Path
    source = Path(__file__).parents[1] / "src/auth_service/repositories/repository_refresh_session.py"
    assert "with_for_update" in source.read_text(encoding="utf-8")


def test_login_refresh_session_starts_non_null_family(monkeypatch):
    from pathlib import Path
    source = Path(__file__).parents[1] / "src/auth_service/services/services_auth.py"
    text = source.read_text(encoding="utf-8")
    assert "family_id=family_id or uuid.uuid4().hex" in text
