"""Prepare canonical identity resolution without changing current login behavior."""

from typing import Protocol

from pydantic import ValidationError

from common.identity import (
    IdentityBlockedError,
    IdentityLinkDuplicateError,
    IdentityLinkMissingError,
    IdentityServiceUnavailableError,
    IdentityUnverifiedError,
    InvalidIdentityResponseError,
    ResolvedIdentity,
    UnknownRoleError,
    UserIdentityProfile,
    UserProfileNotFoundError,
    normalize_role,
)


class IdentityRpc(Protocol):
    async def resolve_by_auth_id(self, auth_user_id: int) -> dict: ...


class IdentityResolver:
    def __init__(self, rpc_client: IdentityRpc):
        self.rpc_client = rpc_client

    async def resolve(self, auth_user, *, require_verified: bool = False) -> ResolvedIdentity:
        if (
            isinstance(auth_user.id, bool)
            or not isinstance(auth_user.id, int)
            or auth_user.id < 1
        ):
            raise IdentityLinkMissingError()
        try:
            response = await self.rpc_client.resolve_by_auth_id(auth_user.id)
        except Exception:
            raise IdentityServiceUnavailableError() from None

        if not isinstance(response, dict):
            raise InvalidIdentityResponseError()
        if not response.get("success"):
            error_code = response.get("error_code")
            if error_code == "identity_link_missing":
                raise IdentityLinkMissingError()
            if error_code == "unknown_role":
                raise UnknownRoleError()
            if error_code == "identity_link_duplicate":
                raise IdentityLinkDuplicateError()
            raise IdentityServiceUnavailableError()

        raw_profile = response.get("identity")
        if raw_profile is None:
            raise UserProfileNotFoundError()
        try:
            raw_profile = dict(raw_profile)
            raw_profile["role"] = normalize_role(raw_profile.get("role"))
            profile = UserIdentityProfile.model_validate(raw_profile)
        except UnknownRoleError:
            raise
        except (TypeError, ValueError, ValidationError):
            raise InvalidIdentityResponseError() from None

        if profile.auth_user_id != auth_user.id:
            raise IdentityLinkMissingError()
        if not profile.is_active or not auth_user.is_active:
            raise IdentityBlockedError()
        if require_verified and profile.is_account_verified is not True:
            raise IdentityUnverifiedError()

        try:
            return ResolvedIdentity(
                **profile.model_dump(),
                token_version=auth_user.token_version,
            )
        except ValidationError:
            raise InvalidIdentityResponseError() from None
