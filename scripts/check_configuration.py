from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRACKED_ENV_PATTERN = re.compile(r"(^|/)\.env(?:\..+)?$")
SAFE_EXAMPLE_PATTERN = re.compile(r"(^|/)\.env\.example$")
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

    if errors:
        print("Configuration check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Configuration check passed: no tracked .env or known hardcoded secrets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
