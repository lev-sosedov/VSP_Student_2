"""Controlled identity-resolution errors without sensitive details."""


class IdentityResolutionError(Exception):
    code = "identity_resolution_error"
    public_message = "Identity could not be resolved"


class UserProfileNotFoundError(IdentityResolutionError):
    code = "user_profile_not_found"
    public_message = "User profile was not found"


class IdentityLinkMissingError(IdentityResolutionError):
    code = "identity_link_missing"
    public_message = "Authentication identity is not linked to a user profile"


class IdentityLinkDuplicateError(IdentityResolutionError):
    code = "identity_link_duplicate"
    public_message = "Authentication identity has an invalid profile link"


class InvalidIdentityResponseError(IdentityResolutionError):
    code = "invalid_identity_response"
    public_message = "Identity service returned an invalid response"


class UnknownRoleError(IdentityResolutionError):
    code = "unknown_role"
    public_message = "User role is not supported"


class IdentityServiceUnavailableError(IdentityResolutionError):
    code = "identity_service_unavailable"
    public_message = "Identity service is temporarily unavailable"


class IdentityBlockedError(IdentityResolutionError):
    code = "identity_blocked"
    public_message = "User account is inactive"


class IdentityUnverifiedError(IdentityResolutionError):
    code = "identity_unverified"
    public_message = "User account is not verified"
