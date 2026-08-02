# PostgreSQL restore

Restore only into a disposable test database first. Verify the backup checksum
and target before restoring with credentials supplied through the protected
environment. Never use `docker compose down -v` or remove the named volume.
Keep the previous backup until a restore has been tested.
