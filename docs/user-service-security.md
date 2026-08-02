# User-service security and synchronization

## Access matrix

- `GET/PATCH /api/v1/users/me` resolve the owner exclusively from `principal.user_id`.
- A full profile or user list is admin-only. Role, block, activation, verification and deletion are admin-only.
- The public teacher endpoint exposes only the documented public profile fields.
- User profile updates are allow-listed; role, status, auth links, token version and other service fields cannot be changed by a profile PATCH.

## Role and status synchronization

User-service writes role/status changes and a versioned event to `user_event_outbox` in the same database transaction. A retry-safe publisher emits events with a unique `event_id`. Auth-service records processed event IDs and applies role changes, blocks/deletes, increments `token_version`, and revokes refresh sessions. Activation does not restore revoked sessions.

The outbox DDL is provided in `services/user_service/migrations/20260802_01_user_event_outbox.sql`; it is intentionally not applied automatically to an existing database.
