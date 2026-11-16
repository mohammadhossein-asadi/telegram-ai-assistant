# ADR-002 — SQLite + SQLAlchemy async with a custom additive migration runner

- **Status:** Accepted (implemented)
- **Date:** 2026-11-16
- **Related:** [database design](../../database/database-design.md), [migrations strategy](../../database/migrations-strategy.md)

## Context

The bot must persist users, per-user settings, conversations, messages, personas,
saved prompts, memory facts, provider rows and usage logs. The deployment target is
a single container on a small host, operated by one person, with no database server
available. Self-hosters must be able to upgrade by pulling a new image and
restarting.

## Problem

Which database and schema-evolution mechanism gives durable, relational storage
with zero operational overhead, while still allowing safe additive upgrades of an
already-populated database?

## Considered alternatives

| Option | Pros | Cons | Verdict |
| --- | --- | --- | --- |
| SQLite file + SQLAlchemy 2 async + custom runner | zero services; single-file backup; relational integrity; typed models | single writer; no downgrades; runner must be maintained | **Chosen** |
| SQLite + Alembic | standard tooling, autogenerate, downgrades | config tree, `env.py`, revisions, second schema authority; overkill for additive changes | Deferred (TASK-303) |
| PostgreSQL + Alembic | concurrency, real DDL | extra service to run/back up; contradicts "one container" | Rejected for current scale; `DATABASE_URL` stays swappable |
| MongoDB | schemaless | relationships are central (user→conversations→messages); no benefit | Rejected |
| JSON files on disk | trivial | no transactions, no query, corruption risk | Rejected |
| In-memory only | fastest | loses all history — the product's core value | Rejected |

## Decision

1. **Database:** SQLite via `sqlite+aiosqlite`, default
   `./data/bot.db`, directory auto-created from the URL.
2. **Access:** SQLAlchemy 2 declarative models with typed `Mapped[...]`; one
   `AsyncSession` per repository method; `expire_on_commit=False`.
3. **Schema creation:** `Base.metadata.create_all` inside `run_migrations()` at
   every boot (idempotent).
4. **Evolution:** a hand-written additive runner keyed on `schema_version`:
   - `SCHEMA_VERSION` constant (currently `2`),
   - `_ADDED_COLUMNS` map of `table -> [(column, DDL)]`,
   - inspector-based existence check so re-runs and partially upgraded databases
     are safe.
5. **Portability:** DDL written with portable types (`INTEGER`, `BOOLEAN DEFAULT 0`,
   `VARCHAR(128)`, `TEXT`) so a Postgres URL is *plausible* — but Postgres remains
   **untested** and must not be claimed as supported.

## Consequences

**Positive**

- A fresh clone boots into a working schema with one command.
- An existing v1 database gains v2 columns without data loss (proven by
  `tests/test_migrations.py::test_additive_migration_on_legacy_schema`).
- No migration tool to learn for a self-hoster.

**Negative / accepted costs**

- No downgrade path; a bad migration must be fixed forward.
- No rename/drop support — such a change requires manual SQL or adopting Alembic.
- Cascade deletes rely on the ORM because SQLite enforces `ON DELETE` only with
  `PRAGMA foreign_keys=ON`, which is not set.

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Migration applied against an unexpected schema | startup failure | inspector check + explicit version rows |
| Concurrent processes both migrating | DDL conflict | single-process deployment rule; backup before upgrade |
| SQLite `database is locked` under load | failed writes | serialise per-user AI calls; consider WAL (TR-01) |
| Data loss on host disk failure | total loss | documented `sqlite3 .backup` + volume strategy |

## Verification

- `tests/test_migrations.py` — idempotency, column presence, legacy upgrade.
- `tests/test_database.py` — user/settings creation, conversation isolation, memory
  upsert/clear.
- `Database._ensure_sqlite_dir` — verified by pointing `DATABASE_URL` at a nested
  path in tests.
