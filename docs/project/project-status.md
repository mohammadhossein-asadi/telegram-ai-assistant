# Project Status

Snapshot: 2026-11-16. Facts below were checked against the code in this workspace; the
verification column says how.

## 1. One-line status

The bot is feature-complete for its documented v1.0 scope, tested at the
repository/service level (32 tests), and **not yet exercised against a live Telegram
bot or a live AI provider in this environment**.

## 2. Feature status by domain

| Domain | State | Evidence |
| --- | --- | --- |
| Onboarding / language | done | `handlers/start.py`, `start.onboarding` keys |
| Main menu | done | `handlers/menu.py`, `views.render_menu` |
| Chat with context | done | `services/chat/engine.py`, `test_chat_engine.py` |
| Conversations (list/new/rename/pin/archive/search/export/summary/delete) | done | `handlers/conversations.py`, `test_conversations.py` |
| Personas (10 presets) | done | `services/personas/presets.py` |
| Custom personas | done | `handlers/custom_personas.py`, `test_custom_personas.py` |
| Styles / tones / creativity | done | `data/styles.py`, `data/tones.py` |
| Memory | done | `repositories/memory.py`, `services/memory/` |
| Models & providers | done | `services/ai/registry.py`, `handlers/models.py` |
| Auto-routing | done (manual override wins) | `services/ai/router.py` |
| Tools | done | `services/tools/`, `handlers/tools.py` |
| Prompt Studio | done | `handlers/prompts.py`, `test_prompts.py` |
| Settings | done | `handlers/settings.py` |
| Developer screen (GitHub) | done, network-dependent | `services/github/`, `test_github_service.py` |
| Admin (stats/limits/providers/broadcast/block) | done | `handlers/admin.py`, `test_admin.py` |
| i18n FA/EN | done, parity enforced | `tests/test_localization.py` |
| Persistence + migrations | done (v2) | `tests/test_migrations.py` |
| Deployment files | present | `Dockerfile`, `docker-compose.yml` |
| CI workflows | **added, never executed** | `.github/workflows/*.yml` |
| Documentation package | done | this directory tree + `manifest/` |

## 3. Verification actually performed

| Check | Command | Result |
| --- | --- | --- |
| Test suite | `pytest -q` | 32 passed |
| Syntax | `python -m compileall -q src` | no errors |
| DDL artifact | `sqlite3 :memory: < artifacts/database/schema.sql` | 10 tables, `schema_version` 1–2 |
| Seed idempotency | apply `seed.sql` twice | counts unchanged |
| Interface artifact | `python -m json.tool artifacts/api/telegram-interface.json` | valid |
| Docs links | link-check script over `docs/` + root files | see generation status |

Not performed here: a live bot run, a real provider call, a container build, a CI run, a
Telegram rendering check.

## 4. Quality signals

| Signal | Value |
| --- | --- |
| Source files under `src/` | 79 |
| Routers | 13 |
| Tests | 32 (repository + service level; no handler tests) |
| Locale keys | 264 per language, parity enforced |
| Tables | 10 (`schema_version` = 2) |
| Lint / type check | none configured |
| Coverage measurement | none |

## 5. Known issues (ranked)

| ID | Issue | Impact | Ref |
| --- | --- | --- | --- |
| G1 | No live end-to-end verification | unknown Telegram/provider quirks | [TASK-101](../product/product-roadmap.md) |
| G2 | Provider keys stored plaintext | DB read = key theft | [BR-044](../product/business-rules.md), TASK-104 |
| G3 | No account deletion | privacy request needs manual SQL | [backup §5](../devops/backup-recovery.md#5-manual-erasure-user-deletion-requests) |
| G4 | In-memory FSM + rate buckets | restarts lose flows and reset quotas | TASK-201, TASK-202 |
| G5 | No handler-level tests | routing/keyboard regressions are uncaught | [test-cases](../testing/test-cases.md) |
| G6 | No global error handler | unexpected exception = silent drop | TASK-102, TASK-302 |
| G7 | `.env.example` missing 6 documented vars | operator cannot discover branding/GitHub settings | [environment-variables](../devops/environment-variables.md) |
| G8 | Container runs as root, no healthcheck | hardening gap | [deployment §10](../devops/deployment.md#10-hardening-gaps-in-the-current-image) |
| G9 | `README.md` claims Alembic + pydantic-settings container | misleading for newcomers | noted in [implementation log](implementation-log.md) |

## 6. What's next

1. **TASK-101** — run the live smoke test with a real token and key; record the result
   here.
2. **TASK-104** — encrypt `ai_providers.api_key`.
3. **Handler-level tests** for the four highest-traffic callbacks.
4. **TASK-201/202** — durable FSM and shared limit store, if multi-process is ever
   needed.

Order rationale: the first item converts the biggest unknown into a fact; the rest are
risk reductions that do not change the product surface.

## 7. Documentation status

Complete for all planned chunks: product, research, architecture (+8 ADRs), database,
bot-interface contract, security, design, testing, DevOps, AI compatibility, project.
Machine-readable artifacts and a traceability manifest are generated. See
[`manifest/generation-status.json`](../../manifest/generation-status.json).
