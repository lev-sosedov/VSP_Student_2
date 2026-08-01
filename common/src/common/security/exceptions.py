"""Internal JWT and authorization errors with safe public messages."""


class SecurityError(Exception):
    """Base class for errors that must not expose cryptographic details."""

    code = "security_error"
    public_message = "Authentication failed"


class AuthenticationError(SecurityError):
    """Base class for HTTP 401 authentication failures."""


class MissingTokenError(AuthenticationError):
    code = "missing_token"
    public_message = "Authentication credentials are required"


class InvalidAuthorizationSchemeError(AuthenticationError):
    code = "invalid_authorization_scheme"
    public_message = "Bearer authentication is required"


class MalformedTokenError(AuthenticationError):
    code = "malformed_token"
    public_message = "Invalid authentication token"


class InvalidSignatureError(AuthenticationError):
    code = "invalid_signature"
    public_message = "Invalid authentication token"


class ExpiredTokenError(AuthenticationError):
    code = "expired_token"
    public_message = "Authentication token has expired"


class TokenNotYetValidError(AuthenticationError):
    code = "token_not_yet_valid"
    public_message = "Authentication token is not active"


class InvalidIssuerError(AuthenticationError):
    code = "invalid_issuer"
    public_message = "Invalid authentication token"


class InvalidAudienceError(AuthenticationError):
    code = "invalid_audience"
    public_message = "Invalid authentication token"


class InvalidTokenTypeError(AuthenticationError):
    code = "invalid_token_type"
    public_message = "An access token is required"


class MissingClaimError(AuthenticationError):
    code = "missing_claim"
    public_message = "Invalid authentication token"


class InvalidSubjectError(AuthenticationError):
    code = "invalid_subject"
    public_message = "Invalid authentication token"


class InvalidRoleError(AuthenticationError):
    code = "invalid_role"
    public_message = "Invalid authentication token"


class InvalidTokenVersionError(AuthenticationError):
    code = "invalid_token_version"
    public_message = "Invalid authentication token"


class UnsupportedAlgorithmError(AuthenticationError):
    code = "unsupported_algorithm"
    public_message = "Invalid authentication token"


class InsufficientPermissionsError(SecurityError):
    code = "insufficient_permissions"
    public_message = "Insufficient permissions"
