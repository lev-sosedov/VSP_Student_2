# Canonical identity resolution

Stage 2.2 prepares a typed internal lookup from `auth_service.auth_users.id` to
the canonical `user_service.users.id`. JWT `sub` remains defined as the latter.
The active HS256 login and token payload are deliberately unchanged.

## Ownership and transport

`user-service` owns profile identity, role, active state, and account-verification
state. `auth-service` owns credentials, its active state, and `token_version`.
The existing RabbitMQ RPC queue is extended with
`identity.resolve_by_auth_id`; no new synchronous HTTP dependency is introduced.
The request contains only a positive `auth_user_id`. The response contains only
`user_id`, `auth_user_id`, normalized `role`, `is_active`, and
`is_account_verified`. Passwords, password hashes, phone numbers, names, and
other profile data are not part of the contract. The client has a bounded
timeout and maps transport failures to a controlled unavailable error.
The callback queue is exclusive and auto-deleted; response messages use the
same no-ack callback pattern as the existing project RPC client. The prepared
client has an explicit `stop()` that cancels pending requests and closes its
channel and connection. It remains lazy and is not started by the current Auth
Service lifecycle.

## Validation and failure policy

The shared `ResolvedIdentity` requires positive identifiers, a known `RoleType`,
`token_version >= 1`, and explicit status flags. Existing upper- or mixed-case
roles normalize safely; unknown roles fail closed. Missing profiles, broken
links, unsupported roles, unavailable RPC, blocked accounts, and (when required
by policy) unverified accounts have distinct controlled errors.
`users.auth_id` remains unique in the User Service schema. The lookup also
detects multiple rows explicitly and fails closed instead of selecting one.

The resolver checks both Auth Service and User Service active states. Account
verification is optional policy because existing accounts may legitimately be
unverified. Endpoint dependencies are not connected in this stage.

## Migration and rollout

The Auth Service Alembic baseline contains a reversible `token_version`
migration. Upgrade adds the column with default `1`, backfills null rows, makes
it non-null, and adds a positive-value constraint. The migration is not run by
application startup and was not applied during this stage.

Before production rollout, create and verify a PostgreSQL backup, apply the
migration in a maintenance window, verify existing rows, then deploy. Rollback
removes only the new constraint and column; it does not touch profiles or Docker
volumes. Wiring resolution into token issuance and switching HS256 to RS256 are
later, separately reviewed stages.
