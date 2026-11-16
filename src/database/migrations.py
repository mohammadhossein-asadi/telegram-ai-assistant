"""Lightweight versioned migration runner.

Schema is created from the ORM metadata on first boot; additive column changes
for already-deployed databases are applied here exactly once and tracked in
``schema_version``. Statements use portable SQL that works on SQLite and
PostgreSQL, so switching ``DATABASE_URL`` needs no code change.
"""

from __future__ import annotations

from sqlalchemy import inspect, text

from core.logging import get_logger
from database.base import Database

log = get_logger(__name__)

# Columns added after v1, keyed by table -> (column, DDL type/default).
_ADDED_COLUMNS: dict[str, list[tuple[str, str]]] = {
    "user_settings": [
        ("default_persona_id", "INTEGER"),
        ("auto_routing", "BOOLEAN DEFAULT 0"),
    ],
    "conversations": [
        ("persona_id", "INTEGER"),
        ("model", "VARCHAR(128)"),
        ("is_pinned", "BOOLEAN DEFAULT 0"),
        ("summary", "TEXT"),
    ],
    "usage_logs": [
        ("prompt_tokens", "INTEGER DEFAULT 0"),
        ("completion_tokens", "INTEGER DEFAULT 0"),
    ],
    "ai_providers": [
        ("capabilities", "VARCHAR(255) DEFAULT ''"),
    ],
}

SCHEMA_VERSION = 2


def _existing_columns(sync_conn) -> dict[str, set[str]]:
    inspector = inspect(sync_conn)
    return {
        table: {column["name"] for column in inspector.get_columns(table)}
        for table in _ADDED_COLUMNS
    }


async def run_migrations(db: Database) -> int:
    await db.create_all()

    async with db.engine.begin() as conn:
        await conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS schema_version ("
                "version INTEGER PRIMARY KEY, description TEXT,"
                "applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            )
        )
        row = (await conn.execute(text("SELECT MAX(version) FROM schema_version"))).scalar()
        current = int(row or 0)

        if current < 1:
            await conn.execute(
                text(
                    "INSERT INTO schema_version (version, description) "
                    "VALUES (1, 'initial schema')"
                )
            )
            current = 1

        if current < SCHEMA_VERSION:
            existing = await conn.run_sync(_existing_columns)
            added: list[str] = []
            for table, columns in _ADDED_COLUMNS.items():
                present = existing.get(table, set())
                for name, ddl in columns:
                    if name in present:
                        continue
                    await conn.execute(
                        text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")
                    )
                    added.append(f"{table}.{name}")
            await conn.execute(
                text(
                    "INSERT INTO schema_version (version, description) "
                    "VALUES (:v, :d)"
                ),
                {"v": SCHEMA_VERSION, "d": "personas, prompts, tokens, pinning"},
            )
            if added:
                log.info("Applied migration 2: added %s", ", ".join(added))
            current = SCHEMA_VERSION

    return current
