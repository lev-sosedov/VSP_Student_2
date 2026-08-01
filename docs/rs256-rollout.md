# RS256 rollout

The backend uses one strict RS256 contract. There is no HS256 fallback or
dual-format decoder. Existing tokens become invalid at cutover and users sign in
again.

Generate local keys outside the repository:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/generate_jwt_keys.ps1
```

The default files are created beside the repository. Set
`JWT_PRIVATE_KEY_HOST_PATH` and `JWT_PUBLIC_KEY_HOST_PATH` when using other
locations. Only auth-service mounts the private key; every verifier mounts only
the public key. Never copy either key into an image or commit it.

Before deployment, back up PostgreSQL, validate `docker compose config`, confirm
the key mounts, and build images without stopping infrastructure. Deploy all HTTP
services together because HS256 tokens are intentionally unsupported. Verify
login, refresh, public news, 401/403 behavior, and representative ownership
checks. Rollback restores the previous complete application set; it does not
delete volumes or downgrade the token-version migration.

Swagger, ReDoc and OpenAPI are public only outside `production`. RabbitMQ RPC is
not authenticated with user JWT. Internal HTTP service authentication remains a
separate future task; internal endpoints must not be exposed through Gateway.

## Service boundary matrix

| Service | Public HTTP | Protected operations |
| --- | --- | --- |
| auth | register, login, refresh, health | me, password change, logout |
| user | health | profile self/admin; administration admin-only |
| academic | health | authenticated; administrative mutations require future resource-scoped policy |
| schedule | health | authenticated; teacher/admin ownership is enforced by existing domain relations where available |
| content | health | authenticated; student submission identity is token-bound |
| communication | health | authenticated; message sender is token-bound |
| notification | health | authenticated; user notification paths are self/admin |
| news | health, published-news GET routes | all write operations require authentication |

Parent-to-child authorization is not synthesized. Although relationship storage
exists, resource-level parent policy is not consistently available across
services and remains a follow-up task. Teacher group ownership also needs a
cross-service policy layer before it can be claimed for every endpoint.
