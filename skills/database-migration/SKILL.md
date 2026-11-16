---
name: database-migration
description: Add a column or table to this project's SQLite schema safely — additive migration, SCHEMA_VERSION bump, DDL artifact regeneration and doc updates.
---

# Skill: add a schema change

Use when you need to persist a new value.

## Decide first

| Need | Where |
| --- | --- |
| One scalar per user | `users` / `user_settings` column |
| One scalar per conversation | `conversations` column |
| Per-message metadata | `messages` column |
| New entity with its own lifecycle | new table + repository |
| Key/value user facts | `user_memory` (no schema change) |

If the change is not additive (rename, drop, type change, split), **stop**: that requires
an ADR and a rebuild strategy. See `docs/database/migrations-strategy.md`.

## Steps

### 1. Model

`src/database/models/__init__.py`:

```python
class Conversation(Base):
    ...
    summary_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
```

Use `Mapped[...]`, explicit `default`, and `nullable=False` only with a default.

### 2. Migration entry

`src/database/migrations.py`:

```python
SCHEMA_VERSION = 3                      # was 2

_ADDED_COLUMNS: dict[str, dict[str, str]] = {
    "conversations": {
        "pinned": "BOOLEAN DEFAULT 0 NOT NULL",   # existing v2 entry
        "summary_tokens": "INTEGER DEFAULT 0 NOT NULL",
    },
}
```

The runner inspects existing columns and only adds missing ones, so it stays
idempotent. SQLite constraints: `ALTER TABLE ... ADD COLUMN` cannot add a NOT NULL
column without a DEFAULT, and cannot add a UNIQUE column.

### 3. Repository

Add the accessor with an ownership filter; never expose a raw session.

### 4. Artifacts and docs

```bash
python - <<'PY'
import asyncio, pathlib
from database.base import Database
from database.models import Base
# regenerate artifacts/database/schema.sql from metadata (see the generator in
# docs/database/database-design.md §DDL artifact)
PY
```

Then update:

- `artifacts/database/schema.sql`
- `docs/database/data-dictionary.md` (column row)
- `docs/database/entity-relationship-diagram.md` (if a table changed shape)
- `docs/database/indexes-and-constraints.md` (if an index was added)
- `docs/project/decisions-log.md` (one line)

### 5. Test

```python
async def test_migration_adds_summary_tokens(db, tmp_path):
    # build v2 schema, run migrate(), assert column + default
    ...
```

## Verification

```bash
pytest -q tests/test_migrations.py
python -c "import sqlite3;sqlite3.connect(':memory:').executescript(open('artifacts/database/schema.sql').read())"
sqlite3 data/bot.db "PRAGMA table_info(conversations);"
```

## Rules

- Never edit an already-applied migration entry; append a new version.
- Never drop or rename in a minor release.
- Every NOT NULL addition has a DEFAULT.
- `PRAGMA foreign_keys` is off; cascades come from the ORM. Don't rely on DB-level FK
  enforcement.
