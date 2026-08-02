from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SERVICES = (
    "auth_service", "user_service", "academic_service", "schedule_service",
    "content_service", "communication_service", "notification_service", "news_service",
)


def test_every_service_has_a_metadata_only_alembic_environment():
    for service in SERVICES:
        root = ROOT / "services" / service
        assert (root / "alembic.ini").exists()
        env = (root / "alembic" / "env.py").read_text(encoding="utf-8")
        assert "DATABASE_URL" in env
        assert "target_metadata" in env
        assert "JWT" not in env and "REDIS" not in env and "RABBITMQ" not in env
        assert list((root / "alembic" / "versions").glob("*.py"))


def test_startup_table_creation_is_explicitly_opt_in():
    for service in SERVICES:
        source = (ROOT / "services" / service / "src" / service / "main.py").read_text(encoding="utf-8")
        assert 'AUTO_CREATE_TABLES", "false"' in source


def test_startup_checks_schema_when_auto_creation_is_disabled():
    readiness = (ROOT / "common/src/common/db_readiness.py").read_text(encoding="utf-8")
    assert "to_regclass" in readiness
    assert "run Alembic upgrade head" in readiness
    for service in SERVICES:
        source = (ROOT / "services" / service / "src" / service / "main.py").read_text(encoding="utf-8")
        assert "require_schema_table" in source
