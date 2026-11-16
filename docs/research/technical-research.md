# Technical Research

**Date:** 2026-11-16. Scope: verify the technology decisions that actually exist in
this codebase. No technology is proposed here that the product does not need.

> **Verification note:** claims about library APIs are grounded in this repository's
> code (which is running and tested). Version ranges are read from
> `requirements.txt`. Where a claim depends on upstream documentation that was not
> fetched in this session, it is marked **[needs upstream confirmation]** rather than
> asserted.

---

## 1. Python runtime

| Item | Value | Evidence |
| --- | --- | --- |
| Target | Python 3.12 | `Dockerfile: FROM python:3.12-slim`; README badge |
| Modern syntax used | `X | None` unions, `dict[str, ...]`, `@dataclass(slots=True)` | throughout `src/` |
| Async model | `asyncio.run(main())` in `run.py`; aiogram polling loop | `run.py`, `src/bot/main.py` |
| Compatibility floor | `from __future__ import annotations` in every module | `src/**` |

**Decision:** stay on 3.12. No 3.13-only features are used, so 3.11 would likely
work, but it is untested and should not be claimed.

---

## 2. Telegram framework: aiogram 3

| Question | Finding | Evidence |
| --- | --- | --- |
| Does the version support routers + FSM? | Yes — `Router`, `StatesGroup`, `MemoryStorage` | `src/bot/handlers/*`, `src/utils/states.py`, `src/bot/main.py` |
| Is middleware able to short-circuit an update? | Yes — returning `None` from an outer middleware stops dispatch | `src/bot/middlewares/user.py` |
| Are callback and message middlewares configured separately? | Yes — `dp.message.outer_middleware(...)` and `dp.callback_query.outer_middleware(...)` | `build_dispatcher()` |
| Does polling resolve used update types? | Yes — `dp.resolve_used_update_types()` | `main()` |
| Message length limit | 4096 characters (Telegram platform limit); this code chunks AI output at 3500 | `src/bot/ui.py` |

**Rate-limit consideration:** Telegram enforces ~30 messages/second globally and
per-chat limits; the broadcast handler sends sequentially and counts failures rather
than bursting. **[needs upstream confirmation for exact current numbers]**

**Alternatives:** `python-telegram-bot` v20+ (LGPL-3.0, application-level
ConversationHandler) — viable, but aiogram's router model maps better onto the
13-file handler layout, and MIT licensing is simpler.

---

## 3. Persistence: SQLAlchemy 2 async + SQLite

| Question | Finding | Evidence |
| --- | --- | --- |
| Can the schema be created without Alembic? | Yes — `Base.metadata.create_all` via `conn.run_sync` | `Database.create_all()` |
| Are cascades declared in the model? | Yes — `cascade="all, delete-orphan"` + `ondelete="CASCADE"` | `models/__init__.py` |
| Is `expire_on_commit=False` used? | Yes — objects stay usable after commit | `async_sessionmaker(...)` |
| Does `DATABASE_URL` claim Postgres portability? | The migration DDL is written to be portable, but **Postgres is untested** | `migrations.py` docstring; TASK-301 |
| SQLite concurrency | Single writer; fine for one polling process. WAL mode is **not** enabled | `Database.__init__` (no pragma) |

**Decision:** SQLite is correct for the deployment model. Documented limitation:
no WAL pragma, so concurrent writes serialise and can raise `database is locked`
under load. Adding `PRAGMA journal_mode=WAL` on connect is a cheap future improvement
(not implemented — do not claim it).

---

## 4. AI integration: OpenAI-compatible Chat Completions

| Question | Finding | Evidence |
| --- | --- | --- |
| Which endpoint shape? | `POST {base_url}/chat/completions` with `model`, `messages`, `temperature` | `src/services/ai/openai_compat.py` |
| Which response fields are read? | assistant content, `model`, `usage.prompt_tokens`, `usage.completion_tokens` (defensive defaults) | same |
| How are errors mapped? | `AIError(message, status=...)`; 401 → configuration/key hint; 429 → rate limit; timeouts → `AITimeoutError` | same |
| Is streaming used? | No — single response, then chunked delivery | same |
| Is the `openai` SDK used? | No — raw `httpx` | `requirements.txt` |

**Why no SDK:** provider abstraction must accept any compatible base URL; the SDK
adds a vendor-shaped client and its own retry semantics.

**Timeout/retry policy:** provider-level `complete()` retries once with linear
backoff (1 s); `chat()` does not retry. Retry behaviour is intentionally minimal —
the bot replies with a localized error rather than hanging.

---

## 5. Configuration: pydantic-settings

| Question | Finding | Evidence |
| --- | --- | --- |
| Are ranges validated? | Yes — `Field(ge=..., le=...)` on limits, context window, cache TTL | `src/core/config.py` |
| Are unknown env vars tolerated? | Yes — `extra="ignore"` | `SettingsConfigDict` |
| Is the settings object cached? | Yes — `@lru_cache(maxsize=1)` on `get_settings()` | same |
| Runtime validation | Returns a list of human-readable problems; `BOT_TOKEN` missing is fatal | `validate_runtime()` |

**Implication for tests:** `get_settings()` caching means a test that mutates env
must clear the cache; repository tests avoid settings entirely.

---

## 6. Localization approach

| Question | Finding |
| --- | --- |
| Format | Nested JSON, dotted key lookup, `str.format` placeholders |
| Locale switching | Per-user column `users.language`; middleware injects `lang` |
| Fallback | Unknown language → `DEFAULT_LANGUAGE` |
| Parity enforcement | Test compares recursive key sets of `en.json` and `fa.json` |
| Limitations | No plural rules, no ICU, no context-aware gender; Persian text is hand-authored |

Alternative evaluated and rejected: gettext/`.po` (build step + tooling) and
Fluent (overkill for 21 top-level namespaces).

---

## 7. Delivery/format conversion

| Question | Finding | Evidence |
| --- | --- | --- |
| How is Markdown handled? | Escaped first, then a regex subset converted to HTML | `markdown_to_telegram_html` |
| Which subset? | fenced code, inline code, bold, italic, strikethrough, links | same |
| Why escape first? | Prevents model output from injecting Telegram HTML entities | same |
| Known limitation | Nested/edge-case Markdown (tables, nested lists) is not converted; it degrades to plain text | regex-based design |

**Security relevance:** this is the single XSS-equivalent control in a Telegram bot
(HTML parse mode). Covered in [data-protection](../security/data-protection.md).

---

## 8. GitHub integration

| Question | Finding |
| --- | --- |
| Auth | Optional bearer token; unauthenticated rate limit applies without it |
| Endpoints | `GET /users/{login}`, `GET /users/{login}/repos?sort=updated&per_page=100&type=owner` |
| Caching | In-memory TTL, default 900 s, manual refresh |
| Failure policy | 404/403/429/timeouts return `None`/`[]`; UI shows a fallback |
| Data exposure | Public profile/repo metadata only; no writes, no scopes requested |

**[needs upstream confirmation]** current unauthenticated rate limits and API version
headers; the client sends `Accept: application/vnd.github+json` and a `User-Agent`,
which is required by GitHub.

---

## 9. Containerisation

| Question | Finding |
| --- | --- |
| Base image | `python:3.12-slim` |
| Install step | `pip install --no-cache-dir -r requirements.txt` before copying source (layer caching) |
| Entrypoint | `python run.py` with `PYTHONPATH=/app/src` |
| Persistence | `./data:/app/data` volume; `DATABASE_URL` points inside it |
| Compose | single service, `restart: unless-stopped`, `env_file: .env` |
| Missing | no healthcheck, no non-root user, no pinned image digest |

Those three omissions are real and are recorded in
[deployment](../devops/deployment.md) as known hardening gaps, not silently ignored.

---

## 10. Explicitly rejected technologies (with reasons)

| Technology | Why not |
| --- | --- |
| FastAPI / any HTTP server | No inbound API requirement; the Bot API is the interface |
| Celery / RQ | No background job exists; broadcasts run inline |
| Redis | Would add an operational dependency for FSM/limits that a single process does not need |
| Kubernetes | One container, one replica; Compose is proportionate |
| Vector database | No RAG requirement |
| GraphQL | No external consumers |
| Alembic (for now) | See §3 and TASK-303 |
| Next.js/React | The product has no web UI by design |

---

## 11. Open technical questions

| ID | Question | Blocks |
| --- | --- | --- |
| TR-01 | Should SQLite WAL be enabled? | Concurrency under burst load |
| TR-02 | Which KMS/approach for encrypting `ai_providers.api_key`? | TASK-104 |
| TR-03 | Is Postgres parity actually needed? | TASK-301 |
| TR-04 | Should FSM become persistent? | TASK-201 |
| TR-05 | Is webhook mode ever required (public HTTPS)? | TASK-305 |

All five are recorded in [open-questions](../project/open-questions.md) with owners.
