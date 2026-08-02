# Rollback

Keep the previous image tag and commit recorded before deployment. Restore the
previous tag in `.env.production` and run `docker compose -f docker-compose.prod.yml
up -d --no-build <service>`. Do not downgrade production migrations
automatically; use a tested backup and an approved recovery plan. Verify
`/health`, `/ready`, login, and critical read-only API paths afterwards.
