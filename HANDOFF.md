# HANDOFF

> Source of truth for continuing development. Update after each milestone.
> Full documentation: [`docs/index.md`](docs/index.md) · Agent rules: [`AGENTS.md`](AGENTS.md)

**Last updated:** 2026-11-16

---

## 1. Where the project stands

| Aspect | State |
| --- | --- |
| Feature scope (v1.0) | complete — see [project status](docs/project/project-status.md) |
| Automated tests | 32 passing (`pytest -q`), offline |
| Documentation package | complete (`docs/`, `artifacts/`, `prompts/`, `skills/`, `templates/`, `manifest/`) |
| Live verification | **not done** — no bot token or AI key available here |
| Working tree | documentation added (untracked) + one source fix (uncommitted) |

## 2. What changed in the last milestone

1. **Documentation package written** — 71 markdown documents across product, research,
   architecture (+8 ADRs), database, bot interface, security, design, testing, DevOps,
   AI collaboration and project management, plus machine-readable artifacts.
2. **Generated artifacts**
   - `artifacts/database/schema.sql` — from SQLAlchemy metadata (10 tables, no `DROP`).
   - `artifacts/database/seed.sql` — dev-only, idempotent, reserved ids starting `900000001`.
   - `artifacts/api/telegram-interface.json` — 24 callback namespaces, 10 commands, 10 failure keys.
   - `artifacts/diagrams/*.mmd` — context, pipeline, chat sequence, lifecycle, ER.
3. **Agent layer** — `AGENTS.md` (canonical) with thin adapters `CLAUDE.md`, `GEMINI.md`,
   `.cursor/rules/*`, `.github/copilot-instructions.md`; 23 prompts; 4 skills.
4. **Repository hygiene** — `LICENSE` (MIT), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
   `SECURITY.md`, `.editorconfig`, `CHANGELOG.md`, issue/PR templates,
   `.github/workflows/{ci,security}.yml`.
5. **Source fix** — removed a duplicated `conv:unarch:` callback decorator in
   `src/bot/handlers/conversations.py` (aiogram registered the handler twice).

## 3. Verification actually performed

| Check | Command | Result |
| --- | --- | --- |
| Tests | `pytest -q` | 32 passed |
| Syntax | `python -m compileall -q src` | clean |
| DDL | executed `artifacts/database/schema.sql` in SQLite | 10 tables; `schema_version` 1–2 |
| Seed | applied `seed.sql` twice | idempotent, counts unchanged |
| Interface JSON | `python -m json.tool artifacts/api/telegram-interface.json` | valid |
| Docs links | relative-link + anchor scan over all markdown | see `manifest/generation-status.json` |

**Not verified:** live bot run, real provider call, container build, CI execution,
Telegram rendering of any screen.

## 4. Uncommitted state

- New: `docs/`, `artifacts/`, `prompts/`, `skills/`, `templates/`, `manifest/`,
  `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/`, `.github/*` (except existing files),
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE`, `.editorconfig`,
  `CHANGELOG.md`.
- Modified: `README.md` (docs index; corrected the Alembic and pydantic-settings claims),
  `HANDOFF.md` (this file), `docs/ARCHITECTURE.md` (cross-links),
  `src/bot/handlers/conversations.py` (duplicate decorator removed).
- Nothing was committed or pushed.

## 5. Database status

Schema is created at boot by `src/database/migrations.py` — `SCHEMA_VERSION = 2`,
additive and idempotent. 10 tables:

`users`, `user_settings`, `conversations`, `messages`, `personas`, `prompts`,
`user_memory`, `ai_providers`, `usage_logs`, `schema_version`.

Cascades come from the ORM (`PRAGMA foreign_keys` is not enabled). Details:
[data dictionary](docs/database/data-dictionary.md),
[indexes & constraints](docs/database/indexes-and-constraints.md).

> Note: `README.md` previously claimed Alembic; it does not use Alembic.

## 6. AI provider status

- `AIProvider` ABC + `OpenAICompatibleProvider` over `httpx`; registry resolves
  model strings; router handles capability-based selection.
- Unit-tested with a fake provider only.
- **Live calls unverified.** Set `AI_API_KEY` (plus optional `AI_BASE_URL`, `AI_MODEL`)
  and send one message.

## 7. Next actionable steps

1. **Live smoke test (TASK-101)** — `.env` from `.env.example`, set `BOT_TOKEN`,
   `AI_API_KEY`, `ADMIN_IDS`; `python run.py`; `/start` → language → message → reply;
   `/admin` → stats. Record the outcome in
   [project status §3](docs/project/project-status.md#3-verification-actually-performed).
2. **Run the CI workflow once** (TASK-102) — it has never executed.
3. **Encrypt `ai_providers.api_key`** (TASK-104) — the top known risk; needs the
   key-management decision in [open questions Q-08](docs/project/open-questions.md).
4. **Handler-level tests** for the four busiest callbacks (conversation list, open,
   settings, model pick) — currently only repository/service level is covered.
5. Optional: durable FSM + shared rate buckets (TASK-201/202) only if multi-process is
   ever required; archived-conversation pagination (TASK-203).

## 8. Known issues

| Issue | Impact | Where |
| --- | --- | --- |
| Provider keys stored plaintext | DB read exposes keys | [ADR-005](docs/architecture/decisions/ADR-005-secrets-and-provider-keys.md) |
| In-memory FSM | multi-step flows lost on restart | [ADR-008](docs/architecture/decisions/ADR-008-state-management-and-limits.md) |
| In-memory rate buckets | restart refunds quota; per-process only | [rate limiting](docs/api/rate-limiting.md) |
| No account deletion | privacy requests need manual SQL | [backup §5](docs/devops/backup-recovery.md#5-manual-erasure-user-deletion-requests) |
| No global error handler | unexpected exception → silent drop | [error handling](docs/api/error-handling.md) |
| Failed AI call stores no user turn | intentional (no orphan history) | [ADR-004](docs/architecture/decisions/ADR-004-chat-execution-and-context.md) |
| `.env.example` misses 6 vars | operators can't discover branding/GitHub settings | [env vars](docs/devops/environment-variables.md) |
| Container runs as root, no healthcheck | hardening gap | [deployment §10](docs/devops/deployment.md#10-hardening-gaps-in-the-current-image) |

## 9. Architectural decisions (summary)

Full records: [`docs/architecture/decisions/`](docs/architecture/decisions/).

- Handlers use a module-level `container` populated once in `bootstrap()` (ADR-001).
- Repositories always take `user_id`; ownership mismatch returns `None` (ADR-001).
- Model output is escaped, then Markdown → Telegram HTML (ADR-004, threat T-07).
- Tools are one-shot completions, never written into conversation history (ADR-004).
- Persist both turns **after** a successful provider call (ADR-004).
- Two complete locale catalogs, parity enforced by a test (ADR-007).
- Single process, long polling, SQLite on a volume (ADR-006).

## 10. Environment variables

See [`artifacts/configurations/env-reference.md`](artifacts/configurations/env-reference.md)
for every variable, default and validation rule. Minimum:

```dotenv
BOT_TOKEN=...
AI_API_KEY=...
ADMIN_IDS=123456789
```

`BOT_TOKEN` is the only variable that is fatal at boot.

## 11. Reading order for a new contributor

1. [`README.md`](README.md) — what it is, how to run it.
2. [`AGENTS.md`](AGENTS.md) — rules, invariants, where to change what.
3. [`docs/product/product-dna.md`](docs/product/product-dna.md) — scope and boundaries.
4. [`docs/architecture/system-architecture.md`](docs/architecture/system-architecture.md) — structure.
5. [`docs/project/project-status.md`](docs/project/project-status.md) — reality check.
6. [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to submit a change.
