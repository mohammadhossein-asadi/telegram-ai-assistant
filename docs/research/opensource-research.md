# Open-Source & Dependency Research

**Research date:** 2026-11-16.
**Method:** the dependency list was read from `requirements.txt` / `requirements-dev.txt`
and cross-checked against the imports in `src/`. Licence and maintenance claims
come from the projects' own repositories; anything not checked is labelled.

This document answers one question per dependency: *reuse, adapt, or avoid?* It
does not recommend replacing working libraries without a concrete engineering reason.

---

## 1. Runtime dependencies (as pinned in this repo)

| Package | Constraint in repo | Purpose here | Licence | Maintenance | Decision |
| --- | --- | --- | --- | --- | --- |
| `aiogram` | `>=3.13,<4` | Bot framework: routers, FSM, inline keyboards, `Bot`/`Dispatcher` | MIT | Active 3.x line | **Reuse** |
| `SQLAlchemy` | `>=2.0,<2.1` | Async ORM + Core for all persistence | MIT | Active | **Reuse** |
| `aiosqlite` | `>=0.20` | Async SQLite driver behind SQLAlchemy | MIT | Maintained | **Reuse** |
| `pydantic` | `>=2.7` | Field validation/ranges in `Settings` | MIT | Active | **Reuse** |
| `pydantic-settings` | `>=2.3` | `.env`/env loading with typed fields | MIT | Active | **Reuse** |
| `httpx` | `>=0.27` | OpenAI-compatible calls + GitHub REST | BSD-3-Clause | Active | **Reuse** |

**Dev:** `pytest >=8.0` (MIT), `pytest-asyncio >=0.23` (Apache-2.0), configured with
`asyncio_mode = auto` in `pytest.ini`.

### Why these and not alternatives

| Need | Chosen | Alternatives considered | Reason |
| --- | --- | --- | --- |
| Telegram framework | aiogram 3 | `python-telegram-bot` (v20+, LGPL-3.0), raw Bot API via `httpx` | aiogram's router/FSM model matches the 13-router layout; MIT licence; no application-level LGPL obligation |
| ORM | SQLAlchemy 2 async | `databases`+`SQLAlchemy Core`, Tortoise ORM, raw `aiosqlite` | Declarative models + `async_sessionmaker` + typed `Mapped[]`; Tortoise is smaller but weaker for complex queries; raw SQL would leak into handlers |
| Migrations | **custom runner** (`database/migrations.py`) | Alembic | Alembic is the standard but adds a config tree and a second schema source of truth for a 9-table schema with additive-only changes; the runner is 100 lines and tested. Revisit at TASK-303 if schema churn grows |
| HTTP | httpx | `aiohttp`, `openai` SDK | One client for both integrations; the `openai` SDK would couple provider abstraction to a vendor |
| Config | pydantic-settings | `python-dotenv` + `os.getenv`, Dynaconf | Typed ranges (`ge`/`le`) already catch bad limits at startup |
| Testing | pytest + pytest-asyncio | `unittest.IsolatedAsyncioTestCase` | Fixture ergonomics and `asyncio_mode=auto` |

---

## 2. Similar repositories studied (not copied)

| Repository | Licence | What was learned | Action |
| --- | --- | --- | --- |
| `n3d1117/chatgpt-telegram-bot` | GPL-2.0 | Standard Docker layout for a Python Telegram bot; `translations.json` approach to i18n; command-first UX | **Avoid code reuse** (GPL + command-first UX). Adopted nothing beyond general layout conventions |
| `tbxark/ChatGPT-Telegram-Workers` | MIT | Provider abstraction by protocol; admin surface; plugin/template concept | **Adapted as concept only**: provider registry + capabilities, and "prompts as data" (Prompt Studio) |
| `father-bot/chatgpt_telegram_bot` | MIT | Tool modes as discrete UX entries | Concept already implemented independently |
| aiogram examples (`aiogram/aiogram` docs) | MIT | Router ordering, FSM usage, inline-keyboard callbacks | **Reuse patterns** (standard API usage) |

No source file from any external project is copied into this repository. Concepts
(provider registry, prompt templates, tool modes) are generic and re-implemented
against this codebase's own models.

---

## 3. Reusable-component evaluation (per component)

### 3.1 aiogram 3 router ordering

- **Relevance:** callback collision is the main UX bug class in menu bots.
- **Integration complexity:** low — `ROUTERS` list in `src/bot/handlers/__init__.py`.
- **Risk:** a generic `F.text` chat handler swallowing state-specific messages if
  registered too early. Mitigated by registering `chat.router` **last**.
- **Decision:** reuse as designed; documented in
  [ADR-001](../architecture/decisions/ADR-001-architecture-pattern.md).

### 3.2 SQLAlchemy async repository pattern

- **Relevance:** all data access must be testable without aiogram.
- **Risk:** session leakage. Mitigated by `async with self.db.session()` per method
  and `expire_on_commit=False`.
- **Decision:** reuse; one session per operation, no long-lived sessions.

### 3.3 Custom migration runner vs Alembic

- **Relevance:** self-hosters upgrade by pulling and restarting.
- **Risk:** the runner intentionally does not support destructive changes,
  renames, or downgrades. It also has **no automatic backup** before DDL.
- **Decision:** keep for now; documented limitation; Alembic comparison in
  [migrations-strategy](../database/migrations-strategy.md).

### 3.4 httpx-based provider client

- **Relevance:** "any OpenAI-compatible endpoint" is a core differentiator.
- **Risk:** divergent endpoints (missing `usage` block, non-standard errors).
  Mitigated by defensive parsing and `AIError` mapping in `openai_compat.py`.
- **Decision:** keep; add per-provider classes only when a protocol truly differs
  (e.g. Anthropic Messages), per [ADR-003](../architecture/decisions/ADR-003-ai-provider-abstraction.md).

### 3.5 JSON localization catalogs + custom loader

- **Relevance:** FA/EN parity with zero build step.
- **Risk:** no pluralization/ICU support; strings are flat key paths.
- **Alternatives:** GNU gettext (`.po`), Fluent, `babel`. All add tooling for a
  product with two locales and no complex plural rules.
- **Decision:** keep; documented as a constraint in
  [design-system](../design/design-system.md).

---

## 4. Rejected / deferred dependencies

| Candidate | Why considered | Why rejected or deferred |
| --- | --- | --- |
| Alembic | Standard migrations | Adds config + duplicate schema authority for additive-only changes; deferred (TASK-303) |
| Redis + `aiogram` Redis storage | Persistent FSM, shared limits | New service to operate; deferred until multi-process is real (TASK-201/202) |
| `openai` Python SDK | Simpler OpenAI calls | Couples to one vendor; breaks the provider abstraction |
| `loguru` | Nicer logging | stdlib `logging` is sufficient at this scale |
| `apscheduler` | Scheduled digests | No scheduled feature exists in scope |
| `alembic`, `celery`, `fastapi` | "Standard stack" additions | No queue or HTTP surface exists; adding them would be architecture theatre |
| Vector DB / embeddings libs | RAG | No requirement; explicitly a non-goal |
| `ruff`/`black`/`mypy` | Quality gates | **Not rejected — missing.** Recommended as TASK-103 (P1) |

---

## 5. Licensing notes

| Component | Licence | Obligation for this project (MIT) |
| --- | --- | --- |
| aiogram, SQLAlchemy, aiosqlite, pydantic, pydantic-settings, pytest | MIT | None beyond attribution in dependency metadata |
| httpx | BSD-3-Clause | None beyond attribution |
| pytest-asyncio | Apache-2.0 | None beyond attribution; patent grant applies |
| `python-telegram-bot` (not used) | LGPL-3.0 | Avoided deliberately: dynamic linking is fine, but a pure-Python import makes the boundary debatable; MIT framework is simpler |
| `n3d1117/chatgpt-telegram-bot` (not used) | GPL-2.0 | Would force GPL on derived code; **no code reused** |

**Distribution risk:** the repository declares MIT in `README.md` and `LICENSE`.
No dependency's licence conflicts with that.

---

## 6. Maintenance-risk register

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| aiogram 3.x breaking change before 4.0 | Low (semver) | Medium | Pin `<4`; upgrade deliberately with test run |
| SQLAlchemy 2.x minor changes | Low | Low | Pin `<2.1` |
| OpenAI-compatible endpoints diverge (usage fields, errors) | Medium | Medium | Defensive parsing; `AIError` with status; provider health screen |
| Telegram Bot API additions (e.g. message limits) | Medium | Low | Limits centralised in `utils/text.py` |
| GitHub REST rate limits for unauthenticated reads | High (60/h) | Low | TTL cache + optional token |

---

## 7. Recommendations

1. **Do not add a framework.** The stack is 6 runtime packages; every addition needs
   a named requirement.
2. **Add quality tooling before features** (`ruff`, then optionally `mypy`) — the
   only "missing standard" in the dependency set (TASK-103).
3. **Keep the custom migration runner** until a destructive or rename migration is
   actually needed; then adopt Alembic with a baseline, not a rewrite.
4. **Add provider classes, not protocols-in-config**, when a non-OpenAI-compatible
   API must be supported.
5. **Vendor nothing.** All dependencies are installable from PyPI; no code is
   copied from the studied repositories.
