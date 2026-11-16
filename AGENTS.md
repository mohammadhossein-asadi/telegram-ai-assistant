# AGENTS.md — canonical instructions for AI coding agents

This is the single source of truth for automated contributors. Tool-specific files
(`CLAUDE.md`, `GEMINI.md`, `.cursor/rules/*`, `.github/copilot-instructions.md`) are
thin adapters that point here; if they disagree, **this file wins**.

Human contributors: see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 1. What this project is

A Persian-first, bilingual (FA/EN) Telegram AI assistant built on aiogram 3 and
SQLAlchemy 2 async with SQLite. One process, one container, one database file.
No HTTP API. No web UI. No model training.

Read [docs/product/product-dna.md](docs/product/product-dna.md) for scope and
[docs/architecture/system-architecture.md](docs/architecture/system-architecture.md)
for structure before making non-trivial changes.

## 2. Fast facts

| Item | Value |
| --- | --- |
| Language | Python 3.12 |
| Entry point | `run.py` → `src/bot/main.py::main` |
| Import root | `src` (top-level imports: `from core.config import ...`) |
| Bot framework | aiogram 3 (`>=3.13,<4`) |
| DB | SQLite via `sqlite+aiosqlite`, default `./data/bot.db` |
| Schema version | `SCHEMA_VERSION = 2` in `src/database/migrations.py` |
| Routers | 13, ordered in `src/bot/handlers/__init__.py` |
| Locales | `fa`, `en` in `src/localization/*.json` (must stay key-identical) |
| Tests | 32 in `tests/`, `pytest -q` |

## 3. Commands

```bash
pip install -r requirements-dev.txt   # setup
python run.py                          # run (needs BOT_TOKEN)
pytest -q                              # 32 tests, no network
python -m compileall -q src            # syntax check
```

There is **no** linter, formatter, type checker, migration CLI, or build step. Do not
invent commands; do not add tooling unless the task asks for it.

## 4. Architecture in one screen

```
bot/handlers (13 routers)  →  services  →  database/repositories  →  models  → SQLite
        ↘ core.container (populated once in bot/main.bootstrap())
bot/keyboards, bot/views, bot/ui  =  presentation only
```

**Hard rules**

1. `services/` and `database/` never import `aiogram`.
2. Handlers never build SQL; they call a repository.
3. Every user-scoped query filters by `user_id`.
4. The chat router is registered **last** in `ROUTERS`.
5. Callback payloads are `namespace:action[:id]`; one namespace = one owner.
6. New locale string ⇒ both `en.json` and `fa.json`.
7. New column ⇒ bump `SCHEMA_VERSION` + add an additive entry + update
   `artifacts/database/schema.sql` and `docs/database/data-dictionary.md`.

Details: [ADR-001](docs/architecture/decisions/ADR-001-architecture-pattern.md),
[ADR-002](docs/architecture/decisions/ADR-002-persistence-and-migrations.md).

## 5. Where to change what

| Task | Files |
| --- | --- |
| Add/modify a command | `src/bot/handlers/<domain>.py`, `src/localization/*.json` |
| Add a callback button | handler + `src/bot/keyboards/common.py` + `src/bot/views.py` |
| Change AI behaviour | `src/services/chat/engine.py`, `src/services/chat/prompts.py` |
| Add a provider protocol | `src/services/ai/` (new class, register it) |
| Change limits | `src/core/config.py` + `.env.example` + docs |
| Add a table/column | `src/database/models/__init__.py` + `migrations.py` + docs |
| Change text/formatting | `src/utils/text.py` (+ tests) |
| Change delivery/edit behaviour | `src/bot/ui.py` |

## 6. Invariants that must not regress

| Invariant | Why | Test |
| --- | --- | --- |
| Both catalogs have identical keys | UI breaks in one language | `test_catalogs_have_identical_keys` |
| History is written only after a successful AI call | no orphan user turns | `test_respond_persists_both_turns` |
| Context is bounded by `MAX_CONTEXT_MESSAGES` | cost | `test_engine_respects_max_context` |
| Tool calls never write to `messages` | prompt hygiene | `test_tool_run_does_not_write_history` |
| Model output is escaped before HTML conversion | injection | `test_markdown_is_escaped_and_converted` |
| Migrations are idempotent and additive | data safety | `test_migrations.py` |
| Foreign ids return `None` | privacy | `test_conversation_and_messages_are_isolated` |

## 7. Coding conventions

- `from __future__ import annotations` at the top of every module.
- Type hints on public functions; `X | None` unions.
- 4-space indent, ~88 char lines, double quotes.
- Async everywhere I/O happens; never call a sync DB driver.
- One session per repository method: `async with self.db.session()`.
- Log via `get_logger(__name__)`; never `print`.
- No secret ever appears in a message, log, test, or doc.

## 8. Testing expectations

- Any behaviour change needs a test at the lowest level that can observe it.
- Bug fix ⇒ failing test first, then the fix.
- Tests use in-memory SQLite and a fake provider; **never** the network or `./data`.
- Do not weaken or delete an existing test to make a change pass.

## 9. Do not

- Add FastAPI/Flask, Redis, Celery, Alembic, or a frontend framework without an
  explicit request.
- Rewrite working modules for style.
- Change the schema destructively or edit an applied migration.
- Introduce `eval`/`exec`/`pickle`/shell calls.
- Commit `.env`, `data/`, keys, or generated secrets.
- Claim a check passed without running it.
- Invent facts about the product; mark unknowns `[UNKNOWN — USER INPUT REQUIRED]`.

## 10. Definition of done

1. `pytest -q` passes.
2. `python -m compileall -q src` passes.
3. Locale parity maintained.
4. Docs updated where behaviour/contracts changed (traceability CSV row if a
   requirement changed).
5. No new secret, no new undocumented callback prefix, no unmentioned schema change.

## 11. Documentation map

| Need | Document |
| --- | --- |
| Scope, personas, requirements | [docs/product/](docs/product/) |
| Competitors, OSS, tech | [docs/research/](docs/research/) |
| System design, ADRs | [docs/architecture/](docs/architecture/) |
| Schema, dictionary | [docs/database/](docs/database/) |
| Bot interface contract | [docs/api/api-design.md](docs/api/api-design.md) |
| Threats, secrets | [docs/security/](docs/security/) |
| Chat UI patterns | [docs/design/](docs/design/) |
| Tests | [docs/testing/](docs/testing/) |
| Deploy, runbooks | [docs/devops/](docs/devops/) |
| Status, open questions | [docs/project/](docs/project/) |
| Full index | [docs/index.md](docs/index.md) |
| Handoff memory | [HANDOFF.md](HANDOFF.md) |
