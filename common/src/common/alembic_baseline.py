"""Helpers for rendering SQLAlchemy model metadata in PostgreSQL Alembic baselines."""
from __future__ import annotations

from sqlalchemy import Enum
from sqlalchemy.types import UserDefinedType


class ExistingPostgresEnum(UserDefinedType):
    """Reference an already-declared PostgreSQL enum without runtime settings."""

    cache_ok = True

    def __init__(self, name: str) -> None:
        self.name = name

    def get_col_spec(self, **_: object) -> str:
        return self.name


def prepare_metadata(metadata):
    """Replace generic SQLAlchemy enums with renderable PostgreSQL type names."""
    enums: dict[str, list[str]] = {}
    for table in metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, Enum):
                name = column.type.name or f"{table.name}_{column.name}_enum"
                enums[name] = list(column.type.enums)
                column.type = ExistingPostgresEnum(name)
    return enums


def create_enum_types(bind, enums: dict[str, list[str]]) -> None:
    for name, labels in enums.items():
        quoted = ", ".join("'" + label.replace("'", "''") + "'" for label in labels)
        bind.execute(
            f"DO $$ BEGIN CREATE TYPE {name} AS ENUM ({quoted}); "
            f"EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
        )
