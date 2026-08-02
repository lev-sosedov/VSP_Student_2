# Backend continuous integration

The backend CI workflow runs on pull requests targeting `master`, pushes to
`master`, and manual dispatches. It performs configuration and secret checks,
Ruff/mypy/compile checks, the complete pytest suite, isolated Alembic checks,
and Docker image builds. Images are built only for validation; CI never pushes
or deploys an image.

All CI credentials are disposable values supplied by the workflow. PostgreSQL,
RabbitMQ, and Redis are service containers created for the job and are never
the development Compose volume. RSA keys are generated under the runner's
temporary directory and are not uploaded or logged.

Run the same checks locally from the repository root:

```powershell
python -m ruff check common/src scripts/check_configuration.py
python -m mypy
python -m pytest
python -m compileall common services scripts
python scripts/check_configuration.py
python scripts/migrate_all_services.py --check
docker compose config --quiet
docker compose build api-gateway auth-service user-service academic-service schedule-service content-service communication-service notification-service news-service
git diff --check
```

The migration command is deliberately the non-mutating `--check` mode. Never
point CI or this checklist at the production database, and never add `.env`,
private keys, tokens, backups, or generated caches to a commit.
