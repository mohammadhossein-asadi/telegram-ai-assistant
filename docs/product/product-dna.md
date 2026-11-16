# Product DNA — Telegram AI Assistant

> Status: **current** (derived from the implemented codebase, not from a market brief).
> Source of truth for product intent. Engineering detail lives in
> [`docs/architecture/system-architecture.md`](../architecture/system-architecture.md).
> Evidence base: the repository at commit `main` (79 tracked files, `src/` ≈ 5.4k lines
> of Python incl. tests), plus the operator's stated intent in `README.md` and `HANDOFF.md`.

## 1. Identity

| Field | Value |
| --- | --- |
| Product name (working title) | Telegram AI Assistant |
| Persian display name | دستیار هوشمند (`BOT_NAME_FA` default in `src/core/config.py`) |
| English display name | AI Assistant (`BOT_NAME_EN` default) |
| Repository | `mohammadhossein-asadi/telegram-ai-assistant` |
| Distribution | Open source, MIT (see [`LICENSE`](../../LICENSE)), self-hosted |
| Runtime surface | Telegram bot (long polling), text-only |
| Languages | Persian (`fa`, RTL) and English (`en`, LTR), full parity |
| Owner / maintainer | Mohammadhossein Asadi — <https://github.com/mohammadhossein-asadi> |

## 2. Summary

A bilingual, menu-driven Telegram assistant that gives one user a private,
persistent AI workspace inside a chat window: multiple conversations with
history, user-authored personas, saved prompts, a per-user fact memory, six
AI tool modes, model/provider selection, and an operator admin panel — all
configured through inline keyboards rather than memorised commands, and all
backed by a single small SQLite database file.

## 3. Vision

Make a capable AI assistant feel native to Persian-speaking Telegram users:
no web app, no account signup, no English-only menus, and no loss of context
between sessions — while remaining a codebase a single developer can read in
an afternoon and a self-hoster can run with one Docker command.

## 4. Mission

Ship a small, dependency-light, test-enforced Python bot in which:

1. every user-visible string exists in both languages and the catalogs are
   proven identical by a test;
2. every feature is reachable by tapping, not typing;
3. the AI vendor is an implementation detail behind an `AIProvider` interface;
4. a user's data is unreachable from any other user's session by construction.

## 5. Core problem

A Telegram user who wants to use an LLM in Persian currently has to pick
between:

- **Hosted bots** they do not control (opaque providers, no data guarantees,
  often English-first and command-driven);
- **Raw API wrappers** that answer one message at a time with no conversations,
  no personas, no memory and no saved prompts;
- **Web apps** that require leaving the chat app, signing up, and managing
  another browser session.

None of the common open-source Telegram bridges (see
[`docs/research/competitor-analysis.md`](../research/competitor-analysis.md))
offer a *Persian-first* inline-menu UX combined with user-authored personas and
a persistent per-user memory store.

## 6. Proposed solution

A single-process aiogram 3 application that:

- persists users, conversations, messages, personas, prompts, memory and usage
  in SQLite through async SQLAlchemy repositories;
- composes every system prompt from the user's stored preferences
  (`src/services/chat/prompts.py`), so behaviour is data, not code;
- resolves model choice through a provider registry that layers an
  env-configured OpenAI-compatible endpoint plus admin-added rows
  (`src/services/ai/registry.py`);
- keeps handlers thin (`src/bot/handlers/*`), services business-logical
  (`src/services/*`), and SQL confined to repositories (`src/database/*`).

## 7. Target audiences

| Audience | Why they care | What they need first |
| --- | --- | --- |
| Persian-speaking Telegram users | Persian-first menus, RTL-safe copy, Persian replies | `/start` → language → one tap to chat |
| Bilingual professionals | Switch reply language without changing UI language | Settings → response language |
| Self-hosters / tinkerers | Own the bot token and the AI key; one Docker command | `.env.example`, `docker compose up` |
| Recruiters / reviewers of the author's portfolio | Evidence of production habits: tests, migrations, localization parity, ADRs | `README.md`, `docs/`, test suite |
| Bot operators (admins) | See usage, add providers, block abuse, broadcast | `/admin` |

## 8. User personas (summary)

Full narratives: [`user-personas.md`](user-personas.md).

- **Sara — Persian student (primary).** Mobile-only, wants summaries and
  translations of study material; never wants to type a command.
- **Amir — developer (secondary).** Uses coding tool modes, wants model choice
  and a code-review persona; tolerant of commands, prefers models with strong
  reasoning.
- **Nika — bilingual professional (secondary).** Drafts Persian↔English email
  copy; needs tone control and a stable "professional" persona.
- **Operator (admin).** Runs the deployment, monitors usage and cost, blocks
  abusers, adds a second provider when the primary rate-limits.

## 9. Main user pain points

1. *Context loss* — free bot wrappers forget the previous message.
2. *Menu poverty* — anything beyond chat requires slash commands and exact syntax.
3. *English-first UI* — Persian users get machine-translated menus, broken RTL
   and mixed-direction text.
4. *Persona drift* — no way to keep a consistent assistant personality across
   sessions.
5. *Provider lock-in* — one vendor hard-coded; no way to add a cheaper or
   local endpoint.
6. *Cost blindness* — no visibility into request volume, tokens or failures.

## 10. Unique value proposition

> **A Persian-first, tap-only AI workspace in Telegram — conversations,
> personas, memory and saved prompts that survive restarts, on top of any
> OpenAI-compatible endpoint, in one Docker container.**

Differentiators that actually exist in the code today:

| Differentiator | Implementation evidence |
| --- | --- |
| Enforced bilingual parity (not aspirational) | `tests/test_localization.py::test_catalogs_have_identical_keys` |
| Personas as first-class rows, assignable per conversation | `personas` table, `cvs.persona_id`, `src/bot/handlers/custom_personas.py` |
| Prompt Studio with categories + JSON import | `prompts` table, `PersonaStudioFlow.import_json`, `src/bot/handlers/prompt_studio.py` |
| Per-user memory injected into the system prompt | `user_memory` table, `build_system_prompt(..., memories=...)` |
| Provider-agnostic registry with capability-based auto-routing | `ProviderRegistry`, `ModelRouter.classify_task` |
| Deterministic, regex-based routing with **no extra model call** | `src/services/ai/router.py` |
| Ownership checks in every repository read/mutate | `ConversationRepository.get(id, user_id)`, `tests/test_database.py` |
| Usage accounting incl. token counts | `usage_logs.prompt_tokens/completion_tokens`, `UsageRepository.token_totals()` |

## 11. Core product principles

1. **Parity is a test, not a promise.** A locale key that exists in one catalog
   and not the other fails CI.
2. **Tap-first.** Every feature has a keyboard path; commands are shortcuts,
   never requirements.
3. **Thin handlers.** A handler validates input, calls one service or
   repository, and renders. Business rules never live in `bot/handlers`.
4. **Fail visibly, never silently.** Provider/GitHub failures surface a
   localized message (`errors.ai`, `gh.unavailable`) and are logged with the
   user id and latency.
5. **Data isolation by signature.** Any query that can touch user data takes
   `user_id`; a mismatch returns `None`, not a record.
6. **No secret in the repository.** Keys come from `.env` only; admin-added
   provider keys live in the local database and are documented as a known risk
   ([ADR-005](../architecture/decisions/ADR-005-secrets-and-provider-keys.md)).
7. **Boring technology.** aiogram + SQLAlchemy + httpx + SQLite; no queue, no
   cache server, no ORM magic.

## 12. Primary workflows

| # | Workflow | Entry point | Success condition |
| --- | --- | --- | --- |
| W1 | Onboard and start chatting | `/start` → language button → menu → message | Assistant replies in the detected/selected language and both turns are persisted |
| W2 | Use a one-shot tool | Tools → mode → send text | Tool output returned; no conversation rows written |
| W3 | Manage conversations | Menu → Conversations | Create / open / pin / rename / archive / summarise / export / delete |
| W4 | Shape the assistant | Personality → presets/styles/tones/creativity/custom | Next reply reflects the new system prompt |
| W5 | Curate long-term memory | Memory → toggle / clear | Facts present in `user_memory` are injected; toggle off removes them |
| W6 | Choose a model | Model → provider/model button | Subsequent replies route to the chosen model |
| W7 | Save and reuse prompts | Prompt Studio | Prompt stored with a category and re-runnable |
| W8 | Inspect the developer | Developer / About | GitHub profile and repo list rendered, cached 15 min |
| W9 | Operate the bot | `/admin` | Stats, health, providers, block/unblock, broadcast |

Detailed journeys with Mermaid diagrams: [`user-journeys.md`](user-journeys.md).

## 13. Differentiating capabilities (ranked)

1. Bilingual parity enforced by CI (rare in this category).
2. Persona + memory + prompts as persistent, user-owned data.
3. Provider registry with per-model capability routing (no latency tax).
4. Tool modes isolated from chat history (clean context, predictable cost).
5. Operator panel usable from the same chat window.

## 14. Product boundaries

**In scope today:** text chat, 6 tool families, conversation management,
personas, prompts, memory, model selection, developer profile (public GitHub
read-only), admin operations, FA/EN.

**Out of scope but adjacent:** voice notes, image generation/vision, group
moderation, inline (@bot) queries, Telegram Mini App, web dashboard.

## 15. Explicit non-goals

| Non-goal | Reason |
| --- | --- |
| Multi-tenant SaaS with billing | No payments, no org accounts, one operator per deployment |
| Public HTTP/REST API | The product's interface is the Telegram Bot API; there is no server surface to expose |
| RAG over user documents / embeddings | Not required by the stated workflows; would add a vector store and ingestion pipeline |
| Voice/vision pipelines | Text-only product decision; avoids file storage and media limits |
| Horizontal scale-out | Single-process polling + SQLite is the deployment model; see [ADR-006](../architecture/decisions/ADR-006-deployment-and-runtime.md) |
| Group chat support | All data scoping and UX assume one private 1:1 chat |

## 16. Business / portfolio objectives

- Demonstrate production engineering practice in a compact codebase: layered
  architecture, migrations, tests, ADRs, CI, threat model.
- Provide a reusable self-hosted assistant for Persian-speaking users.
- Serve as the author's public portfolio artifact
  (`DEVELOPER_GITHUB` branding section).

No revenue model is implemented or planned in this repository.
`[UNKNOWN — USER INPUT REQUIRED]` whether monetisation is ever intended.

## 17. Success metrics

> These are **proposed engineering targets**. None of them is measured in
> production today; the repository contains no telemetry beyond `usage_logs`.

| ID | Metric | Proposed target | How it would be measured |
| --- | --- | --- | --- |
| M-01 | AI request success rate | ≥ 98 % of `usage_logs.action='chat'` with `success=1` | `SELECT success, COUNT(*) FROM usage_logs GROUP BY 1` |
| M-02 | Median chat latency | ≤ 4 s on `gpt-4o-mini`-class models | `usage_logs.latency_ms` percentiles |
| M-03 | Localization parity | 100 % key parity, 0 missing | `pytest tests/test_localization.py` |
| M-04 | Test suite health | 100 % pass, runtime < 30 s | `pytest -q` |
| M-05 | Onboarding completion | ≥ 80 % of new users reach the main menu | requires new instrumentation (`[UNKNOWN]` today) |
| M-06 | Crash-free sessions | ≥ 99 % | requires error reporting (`[UNKNOWN]` today) |

## 18. Known constraints

| Constraint | Consequence | Where enforced |
| --- | --- | --- |
| Telegram message limit (4096 chars) | Long answers must be split | `utils.text.split_message`, `MAX_TELEGRAM_LENGTH` |
| Telegram flood limits (~30 msg/s global) | Broadcasts must pace themselves | `src/bot/handlers/admin.py` broadcast loop |
| SQLite single-writer | One bot process only | `DATABASE_URL` default, [ADR-002](../architecture/decisions/ADR-002-persistence-and-migrations.md) |
| Long polling (no public HTTPS endpoint) | No webhook ops, no inbound HTTP | `dp.start_polling` in `src/bot/main.py` |
| FSM in `MemoryStorage` | Multi-step flows lost on restart | `build_dispatcher()` |
| Provider rate limits (HTTP 429) | Must degrade gracefully, not crash | `src/services/ai/openai_compat.py` |
| Single AI key by default | All users share the operator's quota | `AI_API_KEY`, daily caps |

## 19. Open questions

| ID | Question | Impact if unanswered |
| --- | --- | --- |
| Q-01 | `[UNKNOWN — USER INPUT REQUIRED]` Where is the bot hosted in production (VPS, PaaS, home server)? | Affects backup/restore and monitoring docs only |
| Q-02 | `[UNKNOWN — USER INPUT REQUIRED]` Is a second deployment region or a multi-process setup planned? | Would force the Redis rate-limit bucket work (see roadmap P2) |
| Q-03 | `[UNKNOWN — USER INPUT REQUIRED]` Should provider API keys be encrypted at rest now or deferred? | Security posture and a migration |
| Q-04 | `[UNKNOWN — USER INPUT REQUIRED]` Is published-license intent confirmed as MIT? | `LICENSE` already states MIT to match the README badge |

## 20. Assumptions register

| ID | Assumption | Evidence / rationale | Validation |
| --- | --- | --- | --- |
| A-01 | Primary audience reads Persian first | `DEFAULT_LANGUAGE=fa`, `bot_name_fa` default, Persian copy authored by hand | Product analytics on `/start` language choice |
| A-02 | Traffic fits one process | SQLite + polling design; no queue in `requirements.txt` | Monitor `usage_logs` volume per day |
| A-03 | Users tolerate inline-menu navigation | All 10 menu sections are keyboard-driven | Observe tool/conversation engagement |
| A-04 | One operator controls deployment | `ADMIN_IDS` env list; no roles table | None needed until a second operator appears |
| A-05 | OpenAI-compatible endpoints cover target providers | `OpenAICompatibleProvider` speaks `/chat/completions` | Add a non-compatible provider → implement `AIProvider` |
| A-06 | 20-message context window is enough | `MAX_CONTEXT_MESSAGES=20` default (2–200 range) | User feedback; token cost per request |

## 21. Change log for this document

| Date | Change | Author |
| --- | --- | --- |
| 2026-11-16 | Initial Product DNA derived from the implemented codebase | Documentation pass |
