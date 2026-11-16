from __future__ import annotations

import pytest
from sqlalchemy import text

from database import Database, run_migrations


async def _columns(db, table: str) -> set[str]:
    async with db.engine.begin() as conn:
        rows = await conn.execute(text(f"PRAGMA table_info({table})"))
        return {row[1] for row in rows}


async def test_migration_is_idempotent_and_current(tmp_path) -> None:
    db = Database(f"sqlite+aiosqlite:///{tmp_path}/m.db")
    first = await run_migrations(db)
    assert first == 2

    # Running again must not raise (columns already exist) and must stay at v2.
    second = await run_migrations(db)
    assert second == 2

    async with db.engine.begin() as conn:
        version = (
            await conn.execute(text("SELECT MAX(version) FROM schema_version"))
        ).scalar()
    assert version == 2
    await db.dispose()


async def test_new_columns_exist(tmp_path) -> None:
    db = Database(f"sqlite+aiosqlite:///{tmp_path}/c.db")
    await run_migrations(db)

    assert {"default_persona_id", "auto_routing"} <= await _columns(db, "user_settings")
    assert {"persona_id", "model", "is_pinned", "summary"} <= await _columns(
        db, "conversations"
    )
    assert {"prompt_tokens", "completion_tokens"} <= await _columns(db, "usage_logs")
    assert "capabilities" in await _columns(db, "ai_providers")

    async with db.engine.begin() as conn:
        tables = {
            row[0]
            for row in await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
        }
    assert {"personas", "prompts"} <= tables
    await db.dispose()


async def test_additive_migration_on_legacy_schema(tmp_path) -> None:
    """A v1 database without the new columns must be upgraded in place."""
    db = Database(f"sqlite+aiosqlite:///{tmp_path}/legacy.db")
    async with db.engine.begin() as conn:
        await conn.execute(
            text(
                "CREATE TABLE user_settings (id INTEGER PRIMARY KEY, user_id INTEGER, "
                "personality VARCHAR(32))"
            )
        )
        await conn.execute(
            text(
                "CREATE TABLE schema_version (version INTEGER PRIMARY KEY, "
                "description TEXT, applied_at TIMESTAMP)"
            )
        )
        await conn.execute(
            text("INSERT INTO schema_version (version, description) VALUES (1, 'initial')")
        )

    await run_migrations(db)
    columns = await _columns(db, "user_settings")
    assert "auto_routing" in columns
    assert "default_persona_id" in columns
    await db.dispose()
