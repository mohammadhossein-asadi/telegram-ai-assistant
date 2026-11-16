# Technology Stack

Every entry states responsibility, why it was selected, alternatives considered,
integration notes, licensing and maintenance concerns. Versions are the
constraints declared in `requirements*.txt`, not guesses.

## 1. Summary

| Layer | Technology | Version constraint | Licence |
| --- | --- | --- | --- |
| Language | Python | 3.12 (Docker image) | PSF |
| Bot framework | aiogram | `>=3.13,<4` | MIT |
| ORM | SQLAlchemy (async) | `>=2.0,<2.1` | MIT |
| DB driver | aiosqlite | `>=0.20` | MIT |
| Database | SQLite (file) | platform | Public domain |
| Validation/config | pydantic / pydantic-settings | `>=2.7` / `>=2.3` | MIT |
| HTTP client | httpx | `>=0.27` | BSD-3-Clause |
| Tests | pytest / pytest-asyncio | `>=8.0` / `>=0.23` | MIT / Apache-2.0 |
| Packaging/run | `run.py` (`sys.path` shim) | — | — |
| Containers | Docker + Compose | — | — |
| CI | GitHub Actions (provided workflow) | — | — |

## 2. Detailed entries

### 2.1 Python 3.12

- **Responsibility:** runtime for the whole application.
- **Why:** async-first (`asyncio`), modern typing (`X | None`), 3.12 is the Docker
  image's tag and what the code is exercised on.
- **Alternatives:** 3.11 (likely compatible, untested), 3.13 (no benefit here).
- **Integration:** every module uses `from __future__ import annotations`;
  `sys.path.insert(0, "src")` in `run.py` means the project is *not* an installable
  package — imports are top-level (`from core.config import ...`).
- **Concern:** no `pyproject.toml`, so there is no declared package metadata or
  tooling configuration beyond `pytest.ini`.

### 2.2 aiogram 3

- **Responsibility:** Telegram transport, routers, FSM, inline keyboards, middleware.
- **Why:** file-per-domain routers match the 13-domain handler layout; `out`
  middleware short-circuiting is exactly the block-user gate needed; MIT licence.
- **Alternatives:** `python-telegram-bot` v20 (LGPL-3.0, `ConversationHandler`
  model), raw HTTP.
- **Integration notes:**
  - Router order in `bot/handlers/__init__.py` is load-bearing: `chat.router` last.
  - FSM storage is `MemoryStorage` (state lost on restart).
  - Callback data namespace prefixes (`menu:`, `conv:`, `adm:`, …) avoid collisions.
  - `TelegramBadRequest` is caught in `ui.py` for HTML fallback.
- **Licence:** MIT — no copyleft obligation.
- **Maintenance:** pinned `<4`; upgrade deliberately with the suite.

### 2.3 SQLAlchemy 2 async + aiosqlite

- **Responsibility:** schema definition, sessions, all SQL.
- **Why:** typed `Mapped[...]` models, `async_sessionmaker`, mature async support,
  and plain SQL escape hatches for the migration runner.
- **Alternatives:** Tortoise ORM (smaller, weaker joins), raw aiosqlite (SQL would
  leak into handlers), `databases` (less ORM ergonomics).
- **Integration notes:**
  - One session per repository method (`async with self.db.session()`).
  - `expire_on_commit=False` so returned ORM objects survive commit.
  - Relationships use both ORM `cascade` and DB `ondelete` — necessary because
    SQLite needs `PRAGMA foreign_keys=ON` for DB-level cascades, which is **not**
    set; ORM-level cascade is what actually deletes children today.
  - `Database._ensure_sqlite_dir` creates the parent directory from the URL.
- **Concern:** no connection pooling tuning; SQLite defaults apply. WAL not enabled.

### 2.4 pydantic + pydantic-settings

- **Responsibility:** typed environment configuration with validation.
- **Why:** `Field(ge=..., le=...)` rejects nonsense limits at boot; `extra="ignore"`
  tolerates platform-injected variables.
- **Alternatives:** `os.getenv` (untyped), Dynaconf (heavier).
- **Integration notes:** `model_config = SettingsConfigDict(env_file=".env")`;
  `get_settings()` is `lru_cache`d — tests must clear the cache if they mutate env.
- **Concern:** `AI_API_KEY` etc. are `str` fields; a secret-bearing `repr` could leak
  in a debugging session (never logged today).

### 2.5 httpx

- **Responsibility:** AI chat-completions calls and GitHub REST reads.
- **Why:** async, one API for both integrations, explicit timeouts, no vendor SDK.
- **Alternatives:** `aiohttp` (also fine), official `openai` SDK (couples to a vendor).
- **Integration notes:**
  - A new `AsyncClient` is created per request (`async with httpx.AsyncClient(...)`).
    Simple and safe; a shared client would reduce overhead but adds lifecycle code.
  - Provider timeouts default to a bounded value in `openai_compat.py`.
  - GitHub client sets `Accept` and `User-Agent` (required by GitHub).
- **Concern:** per-request client creation is a small, measurable overhead; acceptable
  at chat latency scales (seconds).

### 2.6 pytest + pytest-asyncio

- **Responsibility:** the 32-test suite.
- **Why:** `asyncio_mode = auto` in `pytest.ini` removes `@pytest.mark.asyncio`
  noise; fixtures build an in-memory SQLite database per test.
- **Integration notes:** `tests/conftest.py` exposes an async `db`/session fixture;
  the AI provider is faked so no network is required.
- **Concern:** no coverage measurement, no lint/type gate (TASK-103).

### 2.7 SQLite (file database)

- **Responsibility:** the single source of durable state.
- **Why:** zero-ops for a single-container deployment; trivially backed up; the
  workload is small 1:1 chats.
- **Alternatives:** PostgreSQL (correct at multi-process scale, extra service today),
  MongoDB (no relational need).
- **Integration notes:** `DATABASE_URL=sqlite+aiosqlite:///./data/bot.db`; the
  directory is created on boot; Docker mounts `./data`.
- **Concern:** single writer; no WAL; no automatic backup. Mitigations in
  [backup-recovery](../devops/backup-recovery.md).

### 2.8 Docker + Docker Compose

- **Responsibility:** reproducible deployment.
- **Why:** one command, no host Python required, volume for the database.
- **Integration notes:** dependencies installed before source copy for layer cache;
  `PYTHONPATH=/app/src`; `restart: unless-stopped`; `env_file: .env`.
- **Concern:** runs as root, no `HEALTHCHECK`, base image not digest-pinned.

### 2.9 GitHub Actions

- **Responsibility:** CI (test) and security checks.
- **Status:** workflows are **provided by this documentation package**
  (`.github/workflows/ci.yml`, `security.yml`) but have not yet run in the
  repository. Do not claim "CI is green" until they have.

## 3. Deliberately not used

| Technology | Why not | Revisit when |
| --- | --- | --- |
| FastAPI / any web server | No inbound HTTP interface | Webhook mode or a dashboard is approved |
| Redis | Extra service for FSM/limits | Multiple processes (TASK-201/202) |
| Celery/RQ | No background jobs | Scheduled digests or bulk jobs appear |
| Alembic | Custom runner covers additive changes | Destructive/rename migrations needed (TASK-303) |
| openai SDK | Vendor coupling | Never, unless a provider needs SDK-only features |
| Kubernetes | One replica | Multi-region deployment is real |
| Next.js/React | No web UI in scope | Mini App is approved |
| LangChain / agent frameworks | Prompt construction here is ~120 lines of deterministic code | Multi-step tool calling with dynamic schemas |

## 4. Version-upgrade policy

1. Runtime dependencies are constrained by minor version; upgrades happen in a
   dedicated commit with the full suite run.
2. `aiogram` major versions require a migration checklist (router API, FSM storage,
   middleware signatures).
3. `SQLAlchemy` 2.1 requires verifying `async_sessionmaker` and `Mapped[]` behaviour.
4. Provider model names are **configuration, not code** — no release is needed to
   switch models.
