# Authorization matrix

Auth session endpoints are scoped to the JWT principal. Refresh rotation uses
families and reuse detection; access tokens are short-lived (15 minutes) and
are not synchronously revoked by every downstream service.

All HTTP services validate the RS256 access token locally. `ADMIN` is the only
role with unrestricted administrative access. `self/admin` means the path,
query, or body identifier must equal `CurrentPrincipal.user_id`, unless the
principal is an administrator.

| Service | Method / endpoint family | Public | Roles | Ownership / participant check | Notes |
|---|---|---:|---|---|---|
| auth | `POST /api/v1/auth/register`, `/login`, `/refresh` | yes | anonymous | none | Only authentication bootstrap routes are public. |
| auth | password, logout, profile operations | no | authenticated | current principal | Refresh validates `auth_user_id` and `token_version`. |
| user | user profile and own resources | no | authenticated | self/admin | Administrative listing, role, verification, block and activation operations are admin-only. |
| academic | reads | no | authenticated | membership where an identifier is supplied | Administrative catalog and group mutations are admin-only; group membership mutations are admin-only. |
| schedule | reads | no | authenticated | own schedule / assigned group | Schedule mutations are admin or an assigned teacher; students and parents cannot mutate schedules. |
| content | published/read routes | no | authenticated | publication and group membership | Teacher content mutations are limited to assigned groups; student submissions are self-only. |
| communication | chat/message routes | no | authenticated | chat participant; sender is always principal | A client-supplied `sender_id` is never trusted. WebSocket access must be participant-scoped. |
| notification | notification routes | no | authenticated | self/admin | Ordinary users cannot create notifications for another user. |
| news | published GET routes | yes | anonymous or authenticated | none for public reads | Drafts and all mutations are admin-only; public comments require explicit moderation policy. |
| gateway | health and documented public proxy routes | limited | n/a | n/a | Forwards `Authorization`; strips client-supplied identity headers and never authorizes on their behalf. |

## Explicitly fail-closed follow-up areas

Parent-child authorization and teacher access to individual groups, lessons,
materials, attendance, and submissions require domain relationship queries. Until
those queries are implemented, endpoints must not infer a relationship from a
client-supplied identifier or trusted header; they remain authenticated and are
restricted to the roles enforced by the service boundary.

WebSocket handlers must use the same verifier and participant check as HTTP
routes, return `4401` for missing/invalid/expired tokens and `4403` for a valid
non-participant, and never log token values.
