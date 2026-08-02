# Alembic and existing databases

Each backend service now owns an Alembic environment and a baseline revision. The
baseline describes the complete schema for a new database; it is not a command to
recreate an existing database.

The logical databases are intentionally unchanged: `vsp`, `vsp_user`,
`academic_db`, `schedule_db`, `content_db`, `communication_db`,
`notification_db`, and `news_db`.

## Audit before applying anything

1. Make a `pg_dumpall` backup outside the repository and verify that it is
   non-empty.
2. Inspect the service schema (`\dt`, `\d+ table`, indexes, constraints and
   foreign keys) and record row counts.
3. Run `alembic current`, `alembic heads`, and an offline `upgrade head`.
4. If the existing schema already contains the baseline, use `alembic stamp`
   only after an explicit schema comparison and a reviewed backup. Never stamp
   a database that has not been compared.
5. Apply only later revisions with `alembic upgrade head`, one database at a
   time, stopping at the first error. Never run the baseline over populated
   tables.

The repository script `scripts/migrate_all_services.py --check` performs the
non-mutating audit and offline SQL generation. Applying migrations requires an
explicit `--apply` and `DATABASE_URL_<SERVICE>` variables; URLs and passwords
are never printed. The script never runs downgrade automatically and never
creates, drops, or deletes databases or volumes.

## New empty databases

For a newly created, isolated database, run `alembic upgrade head` from the
service directory. The baseline creates the current model schema, including
the user outbox and the canonical private-chat pair index. The communication
baseline leaves legacy nullable pair values untouched; it only prevents new
canonical duplicates. Baseline downgrade functions are intentionally no-ops:
the baseline must never delete an existing schema. Rollback of a later revision
must use its reviewed downgrade; whole-schema rollback belongs only to a
disposable database outside the production procedure.

## Automatic table creation

Service startup no longer changes schema by default. `AUTO_CREATE_TABLES=false`
is the safe production setting; production schema changes are Alembic-only.
For an isolated development database, `AUTO_CREATE_TABLES=true` may be used
for backwards compatibility. Do not enable it for the shared production-like
volume.
