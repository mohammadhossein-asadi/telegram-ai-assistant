# Decisions Log

Chronological record of decisions that shaped the project and this documentation set.
Architecture decisions have full ADRs; the rest are recorded here so they are not lost.

| # | Date | Decision | Rationale | Where |
| --- | --- | --- | --- | --- |
| D-01 | pre-2026 | aiogram 3 (not python-telegram-bot) | native async, FSM, routers, middleware | ADR-001 |
| D-02 | pre-2026 | SQLAlchemy 2 async + SQLite | zero-ops single-file store for one operator | ADR-002 |
| D-03 | pre-2026 | Hand-rolled additive migrations | avoids Alembic for a 10-table schema | ADR-002 |
| D-04 | pre-2026 | Provider abstraction over a vendor SDK | provider-agnostic, testable, no SDK lock-in | ADR-003 |
| D-05 | pre-2026 | Hand-written container instead of a DI framework | one composition point, no magic | ADR-001 |
| D-06 | pre-2026 | Long polling, single process | no public URL, no TLS, simplest ops | ADR-006 |
| D-07 | pre-2026 | Persist history only after a successful AI call | no orphan turns, retry stays honest | ADR-004 |
| D-08 | pre-2026 | Persian-first, English second, both complete | primary audience; parity test enforces | ADR-007 |
| D-09 | pre-2026 | In-memory FSM and rate buckets accepted | single process, restart is rare | ADR-008 |
| D-10 | pre-2026 | Admin keys stored in DB (plaintext) | self-service provider management | ADR-005, risk in BR-044 |
| D-11 | 2026-11-16 | Documentation set generated **from the code**, not from the README | README has two factual errors | this log, `AGENTS.md` |
| D-12 | 2026-11-16 | `artifacts/database/schema.sql` generated from SQLAlchemy metadata | hand-written DDL drifts | `artifacts/database/` |
| D-13 | 2026-11-16 | Bot interface documented as a command/callback contract, not OpenAPI | there is no HTTP API | ADR-001, `docs/api/` |
| D-14 | 2026-11-16 | MIT licence file added to match the README badge | the claim existed without the file | `LICENSE` |
| D-15 | 2026-11-16 | `AGENTS.md` is canonical; tool files are adapters | avoids five divergent rule sets | `docs/ai/agent-compatibility.md` |
| D-16 | 2026-11-16 | Duplicate `conv:unarch:` decorator removed | aiogram registers the handler twice | `src/bot/handlers/conversations.py` |
| D-17 | 2026-11-16 | CI/security workflows added, not executed | value only after the first run | `.github/workflows/` |

## Rejected options (and why)

| Option | Rejected because |
| --- | --- |
| FastAPI + web UI | outside the product boundary; adds a second runtime |
| Redis for FSM/limits now | new service for a single-process bot (deferred to TASK-201/202) |
| Alembic | heavier than the schema needs; would need an ADR to adopt |
| Vector store / RAG | not in scope; memory is key/value by design |
| Vendor SDK | protocol client suffices and keeps tests offline |
| Multi-tenant / teams | single-user conversations are the model |
| AutoDeploy on push | operator-driven deployment is deliberate (ADR-006) |
| OpenAPI spec | no HTTP surface to describe |

## How to add a decision

1. If it changes a boundary or is expensive to reverse → write an ADR
   ([template](../../templates/adr/ADR-template.md)).
2. Otherwise add a row here with date, decision, rationale, and where it is visible.
3. Link the row from the affected document.
