# JWT security: current state and RS256 transition

This document prepares a future authentication cutover. The shared module is
opt-in and is not attached to any production endpoint in this stage.

## Current implementation

`auth_service` uses `python-jose` with a configured `JWT_ALGORITHM` (currently
HS256) and a symmetric `JWT_SECRET_KEY`. Access and refresh tokens contain
`user_id`, `role`, `exp`, and `type` (`access` or `refresh`). Access and refresh
have separate lifetimes but otherwise share claims and the signing key. They
have no `sub`, `iat`, `nbf`, `iss`, `aud`, `jti`, or `token_version`.

`auth_service` checks signature, expiration, and token type, but not the target
issuer, audience, or principal contract. Error handling is duplicated: one
decoder returns `None`, while another raises an HTTP exception.

Two identity mismatches must be resolved before endpoint enforcement. The
current `user_id` is `auth_users.id`, while the canonical target `sub` is
**`user_service.users.id`**. `auth_users.id` remains the internal credential ID
and is linked through `users.auth_id`; ownership checks must never treat those
IDs as interchangeable.

The current login flow reads only `auth_service.auth_users`. It does not query
`user_service`, so it cannot yet issue the canonical `sub`. Before RS256
issuance is enabled, login and refresh must resolve the corresponding
`user_service.users` record through an authenticated internal endpoint or RPC,
using the stable `auth_id` link, and fail safely if the mapping is missing.

The target `role` is also authoritative in `user_service` and must use the exact
lowercase values of the existing shared `RoleType`: `user`, `parent`,
`student`, `teacher`, or `admin`. `auth_service` currently defaults roles to
uppercase `USER`; future issuance must fetch the current role from
`user_service` rather than trust that unsynchronized copy.

`user_service` does not validate JWTs. API Gateway does not validate them
either; its proxy preserves and forwards the incoming `Authorization` header.
Other services currently trust request identifiers or mark JWT identity as
future work.

The repository is temporarily inconsistent at the library level:
`auth_service` uses `python-jose`, while several other services list PyJWT.
The target shared module standardizes future verification on
`PyJWT[crypto]`. `auth_service` must migrate its issuer atomically during the
cutover; both libraries must not validate tokens in one service.

## Target token contract

All timestamps use NumericDate UTC values. Required access-token claims are:

| Claim | Meaning |
| --- | --- |
| `sub` | `user_service.users.id` encoded as a positive decimal string |
| `role` | One value from the existing `RoleType` enum |
| `type` | Literal `access` |
| `token_version` | Positive integer used for session invalidation |
| `iat` | Time at which the token was issued |
| `nbf` | Earliest time at which the token is accepted |
| `exp` | Expiration time |
| `iss` | Configured authentication issuer |
| `aud` | Configured platform audience |
| `jti` | Unique token identifier for audit and revocation controls |

Refresh tokens use `type=refresh` and a separate, longer expiration. The
shared microservice verifier accepts access tokens only, so a refresh token can
never authorize a resource request.

Future target environment settings are `JWT_ALGORITHM=RS256`, `JWT_ISSUER`,
`JWT_AUDIENCE`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`,
`JWT_REFRESH_TOKEN_EXPIRE_DAYS`, `JWT_CLOCK_SKEW_SECONDS`,
`JWT_PRIVATE_KEY_PATH`, and `JWT_PUBLIC_KEY_PATH`. Production verification must
enforce signature, algorithm, `exp`, `nbf`, issuer, and audience. They remain
commented in `.env.example` until `auth_service` can issue RS256 tokens; the
active example stays compatible with the current HS256 backend.

## Shared module

`common/security` contains:

- `config.py`: immutable verification configuration and public-key loading;
- `jwt_provider.py`: strict RS256 access-token verification;
- `principal.py`: immutable, typed `CurrentPrincipal`;
- `dependencies.py`: `HTTPBearer` integration and uniform HTTP 401 responses;
- `permissions.py`: role and ownership authorization factories;
- `exceptions.py`: internal failures with safe public messages.

`config.py` is separate because service configuration and filesystem key
loading are deployment concerns, while token parsing remains deterministic and
easy to test. Verification requires only the public key; the verifier never
loads a private key.

`CurrentPrincipal` validates a positive integer `user_id`, an existing
`RoleType`, `type=access`, and a positive `token_version`. It also exposes safe
metadata such as issue/expiry times, issuer, audience, and `jti`.

## Authentication and permissions

Missing, malformed, expired, incorrectly signed, or otherwise invalid tokens
produce HTTP 401 with `WWW-Authenticate: Bearer`. Responses contain a stable
public error code but no token or cryptographic detail. A valid identity without
sufficient role or ownership produces HTTP 403.

- `require_roles(...)` accepts only `RoleType` values;
- `require_admin()` accepts `ADMIN`;
- `require_teacher_or_admin()` accepts `TEACHER` or `ADMIN`;
- `require_self_or_admin()` compares the principal ID with a path parameter
  (default `user_id`) or an explicit async/sync owner resolver.

No dependency is connected to a working endpoint in this stage.

## RSA key storage

Generate at least a 3072-bit RSA pair on a trusted administrator workstation,
for example with OpenSSL. Protect the private key with strict filesystem ACLs.
Never place either key in the repository or Docker build context.

Suggested local locations are outside the checkout in an OS-protected
application-data directory. In containers:

- mount the private key read-only only into `auth_service` at
  `JWT_PRIVATE_KEY_PATH`;
- mount the public key read-only into API Gateway and verifying services at
  `JWT_PUBLIC_KEY_PATH`;
- in production, prefer Docker/Kubernetes secrets or a secret manager over
  ordinary bind mounts.

The repository and Docker context ignore `*.pem`, `*.key`, and `secrets/`.

## Safe HS256 to RS256 cutover

1. Back up configuration and verify rollback credentials without exposing them.
2. Deploy public keys and RS256 verification code without enabling endpoint
   dependencies.
3. Add `token_version` storage and teach `auth_service` to issue the target
   claims using only the private key.
4. Test login, refresh, permissions, and rollback in an isolated environment.
5. Change issuer and verifiers in one controlled deployment. Never select the
   verification algorithm from the JWT header.
6. Existing HS256 tokens become invalid at cutover. Users must sign in once
   again; refresh tokens must not silently bridge algorithms.
7. After the maximum old-token lifetime, remove the symmetric secret and all
   temporary compatibility code.

No automatic HS256 fallback is implemented. If an operationally unavoidable
overlap is approved later, it must use a short-lived server-side allowlist,
separate keys per algorithm, explicit issuer/version discrimination, telemetry,
and a fixed removal date. It must be disabled by default and must never accept
whatever `alg` the token header requests.

## Rotation

Future rotation should add a server-selected `kid`, distribute the next public
key before use, keep the previous public key only for the maximum access-token
lifetime, and then remove it. Private keys stay confined to `auth_service`.
Verifiers resolve only known configured key IDs and never fetch arbitrary key
URLs from token headers.

## `token_version`

Neither `auth_users` nor `user_service.users` currently has `token_version`.
No database change is made in this stage. The proposed authoritative source is
`auth_service`, because session invalidation belongs with credentials.

Including a positive `token_version` claim identifies the session generation,
but merely validating that the claim is a positive integer does **not** revoke
older tokens. Immediate revocation requires comparing it with the current
authoritative value. A later substage can expose that value through an
authenticated internal Auth Service endpoint or a carefully managed Redis
cache. No network or Redis lookup belongs in the shared cryptographic module.

Protected endpoints need an explicit failure policy before rollout. The safe
default for high-impact operations is fail closed when current-version status
cannot be obtained. Any narrowly approved cached grace period must be bounded,
observable, documented per endpoint, and must never silently become fail-open.

The authoritative version increases after password changes, account blocking,
role changes, and an administrator's “end all sessions” action. Until the
current-version lookup exists, use short-lived access tokens and strict refresh
token validation; do not claim that `token_version` alone provides revocation.

## Endpoint rollout and rollback

Public endpoints remain those in `docs/security/api-boundaries.md`, including
login, registration, refresh, health checks, and the approved public news feed.
No endpoint allowlist changes in this stage.

Recommended protected-service rollout:

1. `academic_service`;
2. `schedule_service`;
3. `content_service`;
4. `communication_service`;
5. `notification_service`;
6. `news_service`;
7. API Gateway enforcement after upstream behavior is verified.

Roll out one service at a time with contract tests and observability. Rollback
means disabling the newly attached dependency and redeploying the previous
application image; it never requires database or volume deletion. During the
actual algorithm cutover, rollback restores the complete previous issuer and
verifier set together rather than enabling an open-ended dual-algorithm fallback.
