import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from common.identity import (
    IdentityBlockedError, IdentityLinkMissingError,
    IdentityLinkDuplicateError, InvalidIdentityResponseError,
    IdentityServiceUnavailableError, IdentityUnverifiedError,
    ResolvedIdentity, UnknownRoleError, UserProfileNotFoundError, normalize_role,
)
from common.utils.enum_role import RoleType
from auth_service.models.models_auth_user import AuthUser
from auth_service.repositories.repository_auth import AuthRepository
from auth_service.services.identity_resolver import IdentityResolver
from auth_service.services.token_version import TokenVersionService


def auth_user(**overrides):
    values = {"id": 7, "is_active": True, "token_version": 1}
    values.update(overrides)
    return SimpleNamespace(**values)


def identity_response(**overrides):
    values = {"user_id": 42, "auth_user_id": 7, "role": "student", "is_active": True, "is_account_verified": True}
    values.update(overrides)
    return {"success": True, "identity": values}


@pytest.mark.parametrize("role", list(RoleType))
def test_normalizes_every_role_enum(role):
    assert normalize_role(role) is role


@pytest.mark.parametrize("value, expected", [("USER", RoleType.USER), (" Student ", RoleType.STUDENT), ("TeAcHeR", RoleType.TEACHER)])
def test_normalizes_legacy_role_casing(value, expected):
    assert normalize_role(value) is expected


def test_unknown_role_is_rejected():
    with pytest.raises(UnknownRoleError):
        normalize_role("superuser")


@pytest.mark.parametrize("field", ["user_id", "auth_user_id"])
def test_dto_rejects_non_positive_ids(field):
    values = dict(user_id=42, auth_user_id=7, role="user", token_version=1, is_active=True, is_account_verified=None)
    values[field] = 0
    with pytest.raises(ValidationError):
        ResolvedIdentity(**values)


@pytest.mark.parametrize("field", ["user_id", "auth_user_id", "token_version"])
def test_dto_rejects_numeric_strings(field):
    values = dict(user_id=42, auth_user_id=7, role="user", token_version=1, is_active=True, is_account_verified=None)
    values[field] = "1"
    with pytest.raises(ValidationError):
        ResolvedIdentity(**values)


def test_dto_rejects_invalid_token_version():
    with pytest.raises(ValidationError):
        ResolvedIdentity(user_id=42, auth_user_id=7, role="user", token_version=0, is_active=True, is_account_verified=None)


def test_auth_model_defaults_token_version_to_one():
    assert AuthUser.__table__.c.token_version.default.arg == 1
    assert AuthUser.__table__.c.token_version.nullable is False


def test_auth_model_rejects_invalid_token_version():
    with pytest.raises(ValueError):
        AuthUser(token_version=0)


@pytest.mark.asyncio
async def test_resolver_returns_canonical_user_id_not_auth_id():
    rpc = AsyncMock()
    rpc.resolve_by_auth_id.return_value = identity_response()
    resolved = await IdentityResolver(rpc).resolve(auth_user())
    assert resolved.user_id == 42 and resolved.auth_user_id == 7


@pytest.mark.asyncio
async def test_resolver_rejects_missing_profile():
    rpc = AsyncMock()
    rpc.resolve_by_auth_id.return_value = {"success": True, "identity": None}
    with pytest.raises(UserProfileNotFoundError):
        await IdentityResolver(rpc).resolve(auth_user())


@pytest.mark.asyncio
async def test_resolver_maps_unavailable_rpc():
    rpc = AsyncMock()
    rpc.resolve_by_auth_id.side_effect = ConnectionError()
    with pytest.raises(IdentityServiceUnavailableError):
        await IdentityResolver(rpc).resolve(auth_user())


@pytest.mark.asyncio
async def test_resolver_maps_rpc_timeout():
    rpc = AsyncMock()
    rpc.resolve_by_auth_id.side_effect = asyncio.TimeoutError()
    with pytest.raises(IdentityServiceUnavailableError):
        await IdentityResolver(rpc).resolve(auth_user())


@pytest.mark.asyncio
async def test_resolver_rejects_malformed_rpc_response():
    rpc = AsyncMock()
    rpc.resolve_by_auth_id.return_value = ["not", "a", "mapping"]
    with pytest.raises(InvalidIdentityResponseError):
        await IdentityResolver(rpc).resolve(auth_user())


@pytest.mark.asyncio
async def test_resolver_rejects_duplicate_identity_link():
    rpc = AsyncMock()
    rpc.resolve_by_auth_id.return_value = {
        "success": False,
        "error_code": "identity_link_duplicate",
    }
    with pytest.raises(IdentityLinkDuplicateError):
        await IdentityResolver(rpc).resolve(auth_user())


@pytest.mark.asyncio
async def test_resolver_rejects_broken_link():
    rpc = AsyncMock()
    rpc.resolve_by_auth_id.return_value = identity_response(auth_user_id=8)
    with pytest.raises(IdentityLinkMissingError):
        await IdentityResolver(rpc).resolve(auth_user())


@pytest.mark.asyncio
async def test_resolver_rejects_invalid_auth_user_id_without_rpc_call():
    rpc = AsyncMock()
    with pytest.raises(IdentityLinkMissingError):
        await IdentityResolver(rpc).resolve(auth_user(id=0))
    rpc.resolve_by_auth_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolver_rejects_unknown_role():
    rpc = AsyncMock()
    rpc.resolve_by_auth_id.return_value = identity_response(role="owner")
    with pytest.raises(UnknownRoleError):
        await IdentityResolver(rpc).resolve(auth_user())


@pytest.mark.asyncio
async def test_resolver_rejects_blocked_profile():
    rpc = AsyncMock()
    rpc.resolve_by_auth_id.return_value = identity_response(is_active=False)
    with pytest.raises(IdentityBlockedError):
        await IdentityResolver(rpc).resolve(auth_user())


@pytest.mark.asyncio
async def test_resolver_can_require_verified_profile():
    rpc = AsyncMock()
    rpc.resolve_by_auth_id.return_value = identity_response(is_account_verified=False)
    with pytest.raises(IdentityUnverifiedError):
        await IdentityResolver(rpc).resolve(auth_user(), require_verified=True)


@pytest.mark.asyncio
async def test_unverified_profile_is_allowed_by_current_default_policy():
    rpc = AsyncMock()
    rpc.resolve_by_auth_id.return_value = identity_response(is_account_verified=False)
    resolved = await IdentityResolver(rpc).resolve(auth_user())
    assert resolved.is_account_verified is False


@pytest.mark.asyncio
async def test_resolver_rejects_inactive_auth_user():
    rpc = AsyncMock()
    rpc.resolve_by_auth_id.return_value = identity_response()
    with pytest.raises(IdentityBlockedError):
        await IdentityResolver(rpc).resolve(auth_user(is_active=False))


def test_identity_contract_contains_no_credentials_or_pii():
    fields = set(identity_response()["identity"])
    assert fields == {"user_id", "auth_user_id", "role", "is_active", "is_account_verified"}
    assert not fields & {"password", "hashed_password", "phone_number", "email", "user_name"}


@pytest.mark.asyncio
async def test_token_version_increment_is_single_atomic_update():
    result = SimpleNamespace(scalar_one_or_none=lambda: 2)
    session = SimpleNamespace(execute=AsyncMock(return_value=result), commit=AsyncMock())
    version = await AuthRepository(session).increment_token_version(7)
    assert version == 2
    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()
    statement = str(session.execute.await_args.args[0])
    assert "token_version +" in statement and "RETURNING" in statement


@pytest.mark.asyncio
async def test_token_version_service_rejects_missing_auth_user():
    repository = SimpleNamespace(increment_token_version=AsyncMock(return_value=None))
    with pytest.raises(LookupError):
        await TokenVersionService(repository).invalidate_all_sessions(7)


@pytest.mark.asyncio
async def test_concurrent_token_version_calls_each_use_atomic_update():
    versions = iter((2, 3))

    class Result:
        def scalar_one_or_none(self):
            return next(versions)

    session = SimpleNamespace(
        execute=AsyncMock(side_effect=lambda _statement: Result()),
        commit=AsyncMock(),
    )
    repository = AuthRepository(session)
    returned = await asyncio.gather(
        repository.increment_token_version(7),
        repository.increment_token_version(7),
    )
    assert returned == [2, 3]
    assert session.execute.await_count == 2
    assert all(
        "token_version +" in str(call.args[0]) and "RETURNING" in str(call.args[0])
        for call in session.execute.await_args_list
    )


def test_migration_is_reversible_and_backfills_before_not_null():
    migration = Path(__file__).parents[1] / "alembic" / "versions" / "20260802_01_add_token_version.py"
    source = migration.read_text(encoding="utf-8")
    assert "UPDATE auth_users SET token_version = 1" in source
    assert source.index("UPDATE auth_users") < source.index("nullable=False")
    assert 'op.drop_column("auth_users", "token_version")' in source
