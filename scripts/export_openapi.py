from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE_DIR = ROOT / "openapi" / "baseline"


@dataclass(frozen=True)
class Service:
    name: str
    source: str
    module: str


SERVICES = (
    Service("api-gateway", "services/api_gateway/src", "api_gateway.main"),
    Service("auth-service", "services/auth_service/src", "auth_service.main"),
    Service("user-service", "services/user_service/src", "user_service.main"),
    Service("academic-service", "services/academic_service/src", "academic_service.main"),
    Service("schedule-service", "services/schedule_service/src", "schedule_service.main"),
    Service("content-service", "services/content_service/src", "content_service.main"),
    Service(
        "notification-service",
        "services/notification_service/src",
        "notification_service.main",
    ),
    Service(
        "communication-service",
        "services/communication_service/src",
        "communication_service.main",
    ),
    Service("news-service", "services/news_service/src", "news_service.main"),
)

EXPORT_CODE = """
import json
from importlib import import_module

module = import_module({module!r})
print(json.dumps(module.app.openapi(), ensure_ascii=False, sort_keys=True))
"""


def export_service(service: Service) -> dict:
    environment = os.environ.copy()
    python_paths = [
        str(ROOT / service.source),
        str(ROOT / "common" / "src"),
    ]
    existing_path = environment.get("PYTHONPATH")
    if existing_path:
        python_paths.append(existing_path)

    environment.update(
        {
            "PYTHONHASHSEED": "0",
            "PYTHONPATH": os.pathsep.join(python_paths),
            "DATABASE_URL": "postgresql+asyncpg://vsp:openapi@localhost:5432/vsp",
            "JWT_SECRET_KEY": "openapi-export-only-not-a-runtime-secret",
            "RABBITMQ_USERNAME": "openapi",
            "RABBITMQ_PASSWORD": "openapi",
            "SMTP_USER": "",
            "SMTP_PASSWORD": "",
        }
    )

    result = subprocess.run(
        [sys.executable, "-c", EXPORT_CODE.format(module=service.module)],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Cannot export {service.name}:\n{result.stderr.strip()}"
        )

    return json.loads(result.stdout)


def write_schema(path: Path, schema: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def check_baseline() -> int:
    changed: list[str] = []

    with tempfile.TemporaryDirectory(prefix="vsp-openapi-") as directory:
        current_dir = Path(directory)

        for service in SERVICES:
            schema = export_service(service)
            current_path = current_dir / f"{service.name}.json"
            write_schema(current_path, schema)

            baseline_path = BASELINE_DIR / current_path.name
            if not baseline_path.exists():
                changed.append(f"missing baseline: {current_path.name}")
                continue

            if baseline_path.read_bytes() != current_path.read_bytes():
                changed.append(f"changed schema: {current_path.name}")

    if changed:
        print("OpenAPI compatibility check failed:")
        for item in changed:
            print(f"- {item}")
        return 1

    print("OpenAPI schemas match the committed baseline.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare generated schemas with openapi/baseline",
    )
    args = parser.parse_args()

    if args.check:
        return check_baseline()

    for service in SERVICES:
        print(f"exporting {service.name}...")
        schema = export_service(service)
        write_schema(BASELINE_DIR / f"{service.name}.json", schema)

    print(f"OpenAPI baseline written to {BASELINE_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
