from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRACKED_ENV_PATTERN = re.compile(r"(^|/)\.env(?:\..+)?$")
SAFE_EXAMPLE_PATTERN = re.compile(r"(^|/)\.env\.example$")
SENSITIVE_KEY_FILE_PATTERN = re.compile(
    r"(^|/)(?:secrets?/.*|[^/]+\.(?:pem|key))$",
    re.IGNORECASE,
)
DATABASE_BACKUP_PATTERN = re.compile(
    r"(^|/).*database[_-]backup.*\.sql$",
    re.IGNORECASE,
)
KEY_MATERIAL_PATTERN = re.compile(
    r"-----BEGIN (?:RSA )?(?:PRIVATE|PUBLIC) KEY-----"
)
FORBIDDEN_LITERAL_PATTERNS = {
    "hardcoded PostgreSQL password": re.compile(
        r"POSTGRES_PASSWORD\s*:\s*(?:postgres|admin|password)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "hardcoded JWT secret": re.compile(
        r"^[ \t]*JWT_SECRET_KEY[ \t]*:[ \t]*(?!\$\{|CHANGE_ME)[^\s#]+",
        re.IGNORECASE | re.MULTILINE,
    ),
}


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    errors: list[str] = []
    files = tracked_files()

    for file_name in files:
        if TRACKED_ENV_PATTERN.search(file_name) and not SAFE_EXAMPLE_PATTERN.search(
            file_name
        ):
            errors.append(f"tracked secret file: {file_name}")
        if SENSITIVE_KEY_FILE_PATTERN.search(file_name):
            errors.append(f"tracked key material file: {file_name}")
        if DATABASE_BACKUP_PATTERN.search(file_name):
            errors.append(f"tracked database backup: {file_name}")

    inspected = [
        ROOT / "docker-compose.yml",
        ROOT / "docker-compose.override.yml",
        ROOT / "docker-compose.prod.yml",
    ]

    for path in inspected:
        text = path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_LITERAL_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label}: {path.relative_to(ROOT)}")

    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    protected_services = (
        "auth-service", "user-service", "academic-service", "schedule-service",
        "content-service", "communication-service", "notification-service", "news-service",
    )
    if "x-redis-environment: &redis-environment" not in compose:
        errors.append("missing shared Redis environment anchor")
    if compose.count("*redis-environment") < len(protected_services):
        errors.append("not all JWT-protected services receive REDIS_URL")

    alembic_services = (
        "auth_service", "user_service", "academic_service", "schedule_service",
        "content_service", "communication_service", "notification_service", "news_service",
    )
    for service in alembic_services:
        service_root = ROOT / "services" / service
        for required in ("alembic.ini", "alembic/env.py", "alembic/script.py.mako"):
            if not (service_root / required).exists():
                errors.append(f"missing Alembic file: services/{service}/{required}")
        versions = list((service_root / "alembic" / "versions").glob("*.py"))
        if not versions:
            errors.append(f"missing Alembic revisions: services/{service}")

    example = (ROOT / ".env.example").read_text(encoding="utf-8")
    if "AUTO_CREATE_TABLES=" not in example:
        errors.append(".env.example must define AUTO_CREATE_TABLES")

    contract = ROOT / "common" / "src" / "common" / "messaging_contract.py"
    contract_text = contract.read_text(encoding="utf-8")
    for required in ("EventEnvelope", "event_id", "event_version", "correlation_id", "parse_event_envelope"):
        if required not in contract_text:
            errors.append(f"messaging contract missing {required}")

    reliability = ROOT / "common" / "src" / "common" / "messaging_reliability.py"
    if not reliability.exists():
        errors.append("missing common RabbitMQ reliability utilities")
    for required in ("outbox_context.py", "outbox_worker.py"):
        if not (ROOT / "common" / "src" / "common" / required).exists():
            errors.append(f"missing common outbox utility: {required}")
    domain_outbox = {
        "academic_service": "20260802_01_event_outbox.py",
        "schedule_service": "20260802_01_event_outbox.py",
        "content_service": "20260802_01_event_outbox.py",
        "communication_service": "20260802_02_event_outbox.py",
        "news_service": "20260802_01_event_outbox.py",
    }
    for service, revision in domain_outbox.items():
        migration = ROOT / "services" / service / "alembic" / "versions" / revision
        model = ROOT / "services" / service / "src" / service / "models" / "model_event_outbox.py"
        if not migration.exists() or not model.exists():
            errors.append(f"missing transactional outbox for {service}")
        publisher_dir = ROOT / "services" / service / "src" / service / "messaging"
        publisher_sources = "\n".join(p.read_text(encoding="utf-8") for p in publisher_dir.glob("*publisher*.py"))
        if "current_session.get()" not in publisher_sources or "EventOutbox" not in publisher_sources:
            errors.append(f"domain publisher is not outbox-backed: {service}")
    for service in ("auth_service", "user_service", "academic_service", "communication_service", "notification_service"):
        main_path = ROOT / "services" / service / "src" / service / "main.py"
        if main_path.exists() and "/ready" not in main_path.read_text(encoding="utf-8"):
            errors.append(f"missing /ready route: {service}")

    for file_name in files:
        path = ROOT / file_name
        if not path.exists():
            continue
        if path.suffix.lower() not in {".py", ".md", ".yml", ".yaml", ".toml", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if KEY_MATERIAL_PATTERN.search(text):
            errors.append(f"embedded key material: {file_name}")

    if errors:
        print("Configuration check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Configuration check passed: no tracked .env or known hardcoded secrets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
