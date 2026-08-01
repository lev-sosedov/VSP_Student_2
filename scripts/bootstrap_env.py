from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def copy_example(example: Path) -> None:
    destination = example.with_name(".env")

    if destination.exists():
        print(f"skip: {destination.relative_to(ROOT)} already exists")
        return

    shutil.copyfile(example, destination)
    print(f"created: {destination.relative_to(ROOT)}")


def main() -> None:
    examples = [ROOT / ".env.example"]
    examples.extend(sorted((ROOT / "services").glob("*/.env.example")))

    for example in examples:
        if not example.exists():
            raise FileNotFoundError(example)
        copy_example(example)

    print("\nReplace every CHANGE_ME value before starting the stack.")


if __name__ == "__main__":
    main()
