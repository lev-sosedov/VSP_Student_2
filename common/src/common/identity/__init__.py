"""Typed contracts for resolving authentication identities."""

from common.identity.exceptions import (
    IdentityBlockedError,
    IdentityLinkDuplicateError,
    IdentityLinkMissingError,
    IdentityResolutionError,
    IdentityServiceUnavailableError,
    IdentityUnverifiedError,
    InvalidIdentityResponseError,
    UnknownRoleError,
    UserProfileNotFoundError,
)
from common.identity.models import ResolvedIdentity, UserIdentityProfile
from common.identity.roles import normalize_role

__all__ = [
    "IdentityBlockedError",
    "IdentityLinkDuplicateError",
    "IdentityLinkMissingError",
    "IdentityResolutionError",
    "IdentityServiceUnavailableError",
    "IdentityUnverifiedError",
    "InvalidIdentityResponseError",
    "ResolvedIdentity",
    "UnknownRoleError",
    "UserIdentityProfile",
    "UserProfileNotFoundError",
    "normalize_role",
]
