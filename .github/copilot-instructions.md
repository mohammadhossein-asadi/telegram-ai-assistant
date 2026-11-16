# Copilot instructions

Canonical guidance: [`AGENTS.md`](../AGENTS.md). This file is a condensed adapter for
inline suggestions and Copilot Chat.

## Project

Telegram AI assistant. Python 3.12, aiogram 3, SQLAlchemy 2 async, SQLite, no HTTP or
web layer. Entry point `run.py` → `src/bot/main.py`. Imports are rooted at `src/`
(`from core.config import ...`).

## When completing code here

- Layer boundaries: handlers → services → repositories → models. Never import
  `aiogram` in `services/` or `database/`; never write SQL in handlers.
- Every user-scoped query must include `user_id`.
- Use `get_logger(__name__)`; never `print`.
- New strings go into **both** `src/localization/fa.json` and `en.json` with identical
  keys. Persian text needs correct ZWNJ.
- Callback data format: `namespace:action[:id]`, e.g. `conv:open:12`.
- Async I/O only; one `async with self.db.session()` per repository method.
- Add `from __future__ import annotations` to new modules.
- Public functions get type hints using `X | None` unions.

## When suggesting schema changes

1. Edit `src/database/models/__init__.py`.
2. Bump `SCHEMA_VERSION` in `src/database/migrations.py` and add an additive
   `_ADDED_COLUMNS` entry with a default.
3. Update `artifacts/database/schema.sql` and `docs/database/data-dictionary.md`.

## Do not suggest

- FastAPI/Flask, Redis, Celery, Alembic, Django, React/Next.js.
- `eval`/`exec`/`pickle`/`subprocess` for app logic.
- Rewriting unrelated modules or reformatting whole files.
- Storing secrets in code, tests, or docs.
- Deleting or weakening tests.

## Testing

`pytest -q` (31 tests, offline, in-memory DB). New behaviour ⇒ new test at the lowest
observable level. Bug fix ⇒ regression test.

## Style

Double quotes, 4-space indent, ~88 columns, short docstrings on public repository and
service methods. Match the surrounding file rather than imposing a new style.
