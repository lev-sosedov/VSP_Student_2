# Production deployment

Production uses `docker-compose.prod.yml` as a standalone file. Caddy is the
only service publishing host ports (80/tcp, 443/tcp and 443/udp for HTTP/3).
The edge, backend and data networks are separate; Caddy is attached only to
edge and the gateway bridges edge/backend. Database, Redis and RabbitMQ are on
the internal data network and have no host ports.

Copy `.env.production.example` to protected `.env.production`, provision the
RSA pair under `/opt/vsp/secrets`, and run `deploy/first-deploy.sh`. The script
validates keys, creates a timestamped backup, applies pending Alembic upgrades,
and starts the stack. It never removes volumes.

After deployment verify every `/health` and `/ready`, public news, a protected
route returning `401` without JWT, and empty login returning `422`. Keep the
previous image tag and backup for rollback.
