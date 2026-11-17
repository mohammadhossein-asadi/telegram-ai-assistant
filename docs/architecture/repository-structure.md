# Repository Structure

Two trees are shown: **current** (exactly what exists on `main` today) and
**target** (current + the documentation/agent layer added by this package). Nothing
in the target tree is aspirational application code.

## 1. Current tree (source of truth)

```text
MhaAiAssistantBot/
├── .env.example                 # every env var, empty placeholders only
├── .gitignore                   # ignores .env, data/, caches
├── Dockerfile                   # python:3.12-slim, PYTHONPATH=/app/src
├── docker-compose.yml           # one service, ./data volume
├── pytest.ini                   # asyncio_mode=auto, testpaths=tests
├── requirements.txt             # 6 runtime deps
├── requirements-dev.txt         # runtime + pytest, pytest-asyncio
├── run.py                       # sys.path shim → bot.main.main()
├── README.md                    # product overview + quick start
├── HANDOFF.md                   # execution memory (canonical)
├── docs/
│   └── ARCHITECTURE.md          # original short architecture note
├── src/
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── main.py              # bootstrap(), build_dispatcher(), main()
│   │   ├── helpers.py           # get_prefs, ensure_conversation, current_model
│   │   ├── ui.py                # t(), safe_edit(), send_ai(), answer_ai()
│   │   ├── views.py             # text renderers (pure functions)
│   │   ├── keyboards/
│   │   │   ├── __init__.py
│   │   │   └── common.py        # ~40 keyboard builders
│   │   ├── middlewares/
│   │   │   ├── __init__.py
│   │   │   └── user.py          # UserMiddleware (identity + block gate)
│   │   └── handlers/
│   │       ├── __init__.py      # ROUTERS order (load-bearing)
│   │       ├── start.py         # /start /menu /help /lang /cancel + language CB
│   │       ├── chat.py          # text messages, /new, /retry
│   │       ├── conversations.py # CRUD, pin, archive, search, summary, export
│   │       ├── personality.py   # presets/styles/tones/creativity/custom
│   │       ├── custom_personas.py
│   │       ├── memory.py
│   │       ├── model.py
│   │       ├── tools.py         # summarize/translate/write/explain/coding/custom
│   │       ├── prompt_studio.py
│   │       ├── settings.py      # language, response language, emoji, reset, privacy
│   │       ├── developer.py     # GitHub profile + repos
│   │       ├── about.py
│   │       └── admin.py         # /admin /block /unblock + adm:* callbacks
│   ├── core/
│   │   ├── config.py            # Settings + validate_runtime
│   │   ├── container.py         # service locator singleton
│   │   └── logging.py           # setup_logging, get_logger
│   ├── database/
│   │   ├── base.py              # Database (engine, session factory, create_all)
│   │   ├── migrations.py        # versioned additive runner (SCHEMA_VERSION=2)
│   │   ├── models/__init__.py   # 9 models + TimestampMixin
│   │   └── repositories/
│   │       ├── users.py         # UserRepository, SettingsRepository
│   │       ├── chats.py         # ConversationRepository, MessageRepository
│   │       ├── memory.py
│   │       ├── personas.py
│   │       ├── prompts.py
│   │       ├── providers.py
│   │       └── usage.py         # log, counts, rate window, daily cap
│   ├── localization/
│   │   ├── __init__.py          # JSON loader, fallback, formatting
│   │   ├── en.json              # 21 namespaces
│   │   └── fa.json              # identical key set (ZWNJ-correct)
│   ├── services/
│   │   ├── ai/
│   │   │   ├── base.py          # AIMessage, AIResponse, AIError hierarchy
│   │   │   ├── provider.py      # AIProvider ABC (chat/complete + retry)
│   │   │   ├── openai_compat.py # httpx client for /chat/completions
│   │   │   ├── registry.py      # env provider + DB providers, health, resolve
│   │   │   └── router.py        # classify_task + ModelRouter
│   │   ├── chat/
│   │   │   ├── engine.py        # ChatEngine (respond/regenerate/summarize/run_tool)
│   │   │   └── prompts.py       # personality/style/tone/language/memory prompt
│   │   ├── memory/service.py    # MemoryService facade
│   │   ├── tools/service.py     # ToolService (5 families)
│   │   └── github/client.py     # public profile/repos + TTL cache
│   └── utils/
│       ├── states.py            # 8 StatesGroups
│       └── text.py              # split, escape, markdown→HTML, detect language
└── tests/
    ├── conftest.py              # in-memory DB fixtures
    ├── test_chat_engine.py      # 5 tests
    ├── test_database.py         # 3 tests
    ├── test_localization.py     # 4 tests
    ├── test_migrations.py       # 3 tests
    ├── test_personas_prompts.py # 3 tests
    ├── test_routing.py          # 3 tests
    └── test_text.py             # 6 tests
```

**Counts today:** 79 tracked files at v1.0 plus the documentation set; 32 tests.

## 2. Target tree (this documentation package added)

```text
MhaAiAssistantBot/
├── AGENTS.md                     # provider-neutral canonical instructions
├── CLAUDE.md  GEMINI.md          # thin adapters → AGENTS.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE                       # MIT (matches README badge)
├── .editorconfig
├── .github/
│   ├── copilot-instructions.md
│   ├── ISSUE_TEMPLATE/{bug_report.yml,feature_request.yml,config.yml}
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── labeler.yml
│   └── workflows/{ci.yml,security.yml}
├── .cursor/rules/{000-project.mdc,010-python.mdc}
├── docs/
│   ├── index.md                  # documentation map
│   ├── ARCHITECTURE.md           # kept (short overview)
│   ├── product/                  # DNA, FR, NFR, roadmap, personas, journeys, stories, rules
│   ├── research/                 # competitor, OSS, technical
│   ├── architecture/             # system, stack, structure, decisions/ADR-001..008
│   ├── database/                 # design, ER, dictionary, indexes, migrations, seed
│   ├── api/                      # Telegram interface contract, auth, errors, limits
│   ├── security/                 # architecture, threat model, authz, data, secrets, testing
│   ├── design/                   # direction, system, components, responsive, a11y
│   ├── testing/                  # strategy, plan, cases, acceptance, perf, security
│   ├── devops/                   # env, ci-cd, deploy, vars, monitoring, backup, runbook
│   ├── ai/                       # agent compatibility
│   └── project/                  # status, decisions log, open questions, implementation log
├── artifacts/
│   ├── api/telegram-interface.json
│   ├── database/{schema.sql,seed.sql}
│   ├── diagrams/*.mmd
│   └── configurations/env-reference.md
├── prompts/                      # 23 executable prompts in 7 phase folders
├── skills/                       # 4 project-specific SKILL.md packages
├── templates/{adr,documentation}/
└── manifest/{documentation-index.json,requirements-traceability.csv,generation-status.json}
```

## 3. Folder responsibilities and dependency rules

| Folder | Responsibility | May import | Must never import |
| --- | --- | --- | --- |
| `src/bot/handlers` | One module per domain; route + orchestrate | `bot/*`, `services/*`, `core/*`, `database/*`(repos), `utils` | — |
| `src/bot/keyboards` | Pure keyboard builders | aiogram types, localization | repositories, services |
| `src/bot/views` | Pure text renderers | models (read-only), localization | aiogram send calls |
| `src/bot/ui` | Delivery helpers (edit/send/chunk) | aiogram, localization, utils | repositories |
| `src/bot/middlewares` | Identity + block gate | core, localization, repositories via container | services |
| `src/services/*` | Business logic; no aiogram | database, core, utils | `bot/` |
| `src/database/repositories` | SQL only | models, base | services, bot |
| `src/database/models` | Schema | base | everything else |
| `src/core` | Config, container, logging | stdlib, pydantic | concrete app modules |
| `src/utils` | Pure functions | stdlib, aiogram FSM types | database, services |
| `tests` | Behavioural proof | everything under `src` | network |

**Invariants worth reviewing in every PR**

1. No `from aiogram` in `services/` or `database/`.
2. No `session`/`select` in `bot/handlers` — go through a repository.
3. New string ⇒ both catalogs.
4. New table column ⇒ `SCHEMA_VERSION` bump + additive entry.
5. New callback prefix ⇒ documented in `artifacts/api/telegram-interface.json`.

## 4. Naming and code conventions

| Kind | Convention | Example |
| --- | --- | --- |
| Modules | snake_case, one domain | `custom_personas.py` |
| Router var | `router` in every handler module | `router = Router(name="conversations")` |
| Callback data | `namespace:action[:id]` | `conv:open:12`, `adm:delprov:3` |
| FSM states | `<Domain>Flow` | `ConversationFlow.rename` |
| Repositories | `<Entity>Repository`, plural collection | `container.conversations` |
| Services | `<Domain>Service` / `<Domain>Engine` | `ToolService`, `ChatEngine` |
| Locale keys | `namespace.key`, snake_case leaf | `convs.ask_name` |
| Tests | `test_<behaviour>` | `test_engine_respects_max_context` |

## 5. Testing structure

- `tests/conftest.py` builds an isolated in-memory database; no test touches
  `./data/bot.db` or the network.
- One file per concern: engine behaviour, repositories, localization, migrations,
  persona/prompt CRUD, routing, text utilities.
- A fake provider (`tests/test_chat_engine.py`) implements `AIProvider` so the engine
  is tested without HTTP.
- **Missing:** handler-level tests (would need an aiogram update harness), coverage
  measurement, lint gate. See [testing-strategy](../testing/testing-strategy.md).

## 6. Deployment structure

| Artifact | Purpose | Notes |
| --- | --- | --- |
| `Dockerfile` | image build | no healthcheck, root user |
| `docker-compose.yml` | single-service run | `env_file`, `./data` volume |
| `.env.example` | variable inventory | mirrors `Settings` |
| `docs/devops/*` | runbooks | env vars, backup, incident steps |

## 7. Documentation structure rules

- One concern per file; no document over ~400 lines without a split.
- Every document starts with a status/scope line.
- Cross-links use relative paths; a link checker validates them
  (`manifest/documentation-index.json` lists the canonical set).
- Product facts point at code symbols, not at other prose.

## 8. Environment & configuration structure

```text
.env.example   →  Settings (pydantic)  →  container.config  →  services/handlers
```
No module reads `os.environ` directly; everything goes through `Settings`.
Exceptions: none. Tests construct objects directly instead of settings.
