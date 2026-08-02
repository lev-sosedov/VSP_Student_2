"""Audit or deliberately apply all service Alembic environments.

The default is non-mutating. Applying requires --apply and one
DATABASE_URL_<SERVICE> variable per service. Secrets and URLs are never printed.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICES = {
    "auth_service": ROOT / "services/auth_service",
    "user_service": ROOT / "services/user_service",
    "academic_service": ROOT / "services/academic_service",
    "schedule_service": ROOT / "services/schedule_service",
    "content_service": ROOT / "services/content_service",
    "communication_service": ROOT / "services/communication_service",
    "notification_service": ROOT / "services/notification_service",
    "news_service": ROOT / "services/news_service",
}


def run(service: str, args: list[str], *, apply: bool = False) -> None:
    directory = SERVICES[service]
    env = os.environ.copy()
    if apply:
        key = f"DATABASE_URL_{service.upper()}"
        url = env.get(key)
        if not url:
            raise SystemExit(f"missing {key}; no migration was started")
        env["DATABASE_URL"] = url
    elif not env.get("DATABASE_URL"):
        # Offline rendering needs a dialect URL but never opens a connection.
        env["DATABASE_URL"] = "postgresql+asyncpg://offline:offline@localhost:5432/offline"
    command = [sys.executable, "-m", "alembic", "-c", str(directory / "alembic.ini"), *args]
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="audit and render offline SQL")
    parser.add_argument("--apply", action="store_true", help="apply upgrade head sequentially")
    options = parser.parse_args()
    if not options.check and not options.apply:
        options.check = True
    for service in SERVICES:
        print(f"[{service}]", flush=True)
        run(service, ["heads"])
        run(service, ["history"])
        run(service, ["upgrade", "head", "--sql"])
    if options.apply:
        for service in SERVICES:
            run(service, ["upgrade", "head"], apply=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
