# Architecture

> Summary page. Full detail: [system architecture](architecture/system-architecture.md),
> [repository structure](architecture/repository-structure.md),
> [technology stack](architecture/technology-stack.md), [ADRs](architecture/decisions/),
> [diagrams](../artifacts/diagrams/system-context.mmd).

## Layers

```
handlers  →  services  →  repositories  →  SQLAlchemy models  →  SQLite
    ↓                          ↑
keyboards / views / ui     core.container (singletons)
```

- **Handlers** are thin: they read the injected `user` / `lang` / `is_admin`
  values from the middleware, call a service or repository, and render.
- **Services** hold business rules: prompt building, provider calls, tool
  prompts, memory facade.
- **Repositories** own all SQL. No handler touches a session directly.
- **`core.container`** is a plain object populated once by `bot/main.bootstrap()`.
  Handlers import the shared `container` singleton; this avoids threading a DI
  graph through every aiogram callable while keeping construction in one place.

## Provider abstraction

`services/ai/provider.py` defines the `AIProvider` interface (`chat`, `complete`).
`OpenAICompatibleProvider` implements it over `httpx` against any
`{base_url}/chat/completions` endpoint.

`ProviderRegistry` builds the available providers from environment settings plus
rows in `ai_providers` (added by admins). Users pick a *model string*; the
registry resolves it back to a provider when a request is made.

Adding a provider type = implement `AIProvider` and register it in the registry.
Adding an OpenAI-compatible endpoint = insert a row (no code change).

## Prompt construction

`services/chat/prompts.py` composes the system prompt from:

1. personality preset (or custom instructions),
2. response style,
3. tone,
4. response language (auto = detected input language, else explicit),
5. emoji preference,
6. stored user memories (when memory is enabled).

`temperature` is derived from the creativity level.

## Conversation context

`ChatEngine.respond()` loads the last `MAX_CONTEXT_MESSAGES` turns of the
conversation, appends the new user message, calls the provider, then persists
both turns. `run_tool()` performs one-shot completions that are **not** written
to conversation history.

## Data isolation

Every repository method that reads or mutates a conversation takes `user_id` and
returns `None` when ownership does not match, so one user can never open,
rename, or delete another user's conversation by guessing an ID.

## Rate limiting & limits

- Sliding 60-second in-memory window (`USER_RATE_LIMIT`) per Telegram ID.
- Daily request cap (`MAX_DAILY_REQUESTS`) counted from `usage_logs`.
- A per-user `asyncio.Lock` prevents overlapping AI requests from one user.

## Migrations

`database/migrations.py` creates the schema on first boot and records applied
versions in `schema_version` (currently `SCHEMA_VERSION = 2`). It is intentionally
lightweight and additive — no down-migrations, no Alembic dependency. Trade-offs and
the rules for adding v3: [migrations strategy](database/migrations-strategy.md) and
[ADR-002](architecture/decisions/ADR-002-persistence-and-migrations.md).

## Where to look next

| Question | Document |
| --- | --- |
| How does one message travel end to end? | [chat sequence diagram](architecture/system-architecture.md), [`chat-sequence.mmd`](../artifacts/diagrams/chat-sequence.mmd) |
| Which table stores what? | [data dictionary](database/data-dictionary.md) |
| Which callbacks exist? | [bot interface](api/api-design.md), [`telegram-interface.json`](../artifacts/api/telegram-interface.json) |
| What is the trust boundary? | [threat model](security/threat-model.md) |
| What is actually tested? | [test plan](testing/test-plan.md) |

## Known trade-offs

- `ai_providers.api_key` is stored in SQLite in plaintext so admins can add
  providers at runtime. Environment-provided keys stay in `.env` only.
- Rate-limit buckets are in memory; they reset on restart and do not span
  multiple bot processes. A Redis/DB bucket is the next step for horizontal scale.
- FSM state uses aiogram's `MemoryStorage`; pending multi-step flows (rename,
  broadcast, provider add) are lost on restart.
- No global error handler: an exception outside a handler's `try` is logged and the
  update is dropped without user feedback.
- `PRAGMA foreign_keys` stays off, so cascades are enforced by the ORM, not SQLite.
