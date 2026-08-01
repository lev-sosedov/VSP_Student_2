# HTTP API boundaries

Every backend HTTP service validates the same RS256 bearer token locally. The
API Gateway forwards `Authorization` unchanged but strips all incoming trusted
identity headers (`X-User-ID`, `X-Role` and variants); authorization never relies
on the Gateway alone.

Unauthenticated HTTP routes are limited to health/readiness/liveness, auth
register/login/refresh, development documentation, and the explicitly public
published-news GET routes. RabbitMQ RPC is an internal transport and does not
use a user JWT. The Gateway technical proxy is not a public production route.

| Service | Public HTTP | Protected operations |
| --- | --- | --- |
| auth-service | register, login, refresh, health | me, logout, password change |
| user-service | health | profiles and administration |
| academic-service | health | academic resources and mutations |
| schedule-service | health | schedules and attendance |
| content-service | health | lessons, homework, submissions and attachments |
| communication-service | health | chats, messages and WebSocket sessions |
| notification-service | health | notifications and user settings |
| news-service | health, published-news GET | writes, moderation and non-public reads |

Role checks use the shared `RoleType`: ADMIN is global administrative access;
TEACHER is limited to teacher operations where resource ownership exists;
STUDENT is limited to own submissions/attendance/messages/notifications;
PARENT access remains denied where a verified parent-child policy is not yet
implemented; USER receives only basic self-profile capabilities.

Any `user_id`, `student_id`, `sender_id`, or equivalent supplied by a client is
untrusted. Services compare it with `CurrentPrincipal.user_id` or require an
explicit ADMIN/resource-owner policy. Internal service-to-service HTTP
authentication is a separate future concern and is not provided by forwarding a
user JWT.
