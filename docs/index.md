# Documentation

Engineering documentation for **MhaAiAssistantBot** — a Persian-first, bilingual
Telegram AI assistant (aiogram 3 · SQLAlchemy 2 async · SQLite · no HTTP API, no web UI).

Start with the path that matches why you are here.

## Reading paths

| You want to… | Read, in order |
| --- | --- |
| Understand the product | [product DNA](product/product-dna.md) → [personas](product/user-personas.md) → [journeys](product/user-journeys.md) |
| Contribute code | [AGENTS.md](../AGENTS.md) → [system architecture](architecture/system-architecture.md) → [repository structure](architecture/repository-structure.md) → [CONTRIBUTING](../CONTRIBUTING.md) |
| Run it | [development environment](devops/development-environment.md) → [deployment](devops/deployment.md) → [operations runbook](devops/operations-runbook.md) |
| Change the database | [database design](database/database-design.md) → [migrations strategy](database/migrations-strategy.md) → [data dictionary](database/data-dictionary.md) |
| Add a command or button | [bot interface](api/api-design.md) → [skills/telegram-handler](../skills/telegram-handler/SKILL.md) |
| Review a change | [code review prompt](../prompts/review/19-code-review.md) → [security threat model](security/threat-model.md) → [regression testing](testing/regression-testing.md) |
| Know what is actually done | [project status](project/project-status.md) → [open questions](project/open-questions.md) → [HANDOFF](../HANDOFF.md) |

## Chunks

### Product — why it exists, for whom

| Document | Contents |
| --- | --- |
| [product-dna.md](product/product-dna.md) | identity, vision, boundaries, metrics, principles |
| [user-personas.md](product/user-personas.md) | P1–P5, needs, constraints |
| [user-journeys.md](product/user-journeys.md) | J0–J10 end-to-end flows |
| [user-stories.md](product/user-stories.md) | US-001… with acceptance notes |
| [functional-requirements.md](product/functional-requirements.md) | FR-* (76 requirements) with source symbols |
| [non-functional-requirements.md](product/non-functional-requirements.md) | NFR-* targets vs facts |
| [business-rules.md](product/business-rules.md) | BR-* invariants and enforcement |
| [product-roadmap.md](product/product-roadmap.md) | phases, TASK-*, acceptance |

### Research — evidence, not assertion

| Document | Contents |
| --- | --- |
| [competitor-analysis.md](research/competitor-analysis.md) | C1–C4, capability matrix, sources |
| [opensource-research.md](research/opensource-research.md) | licences, patterns worth borrowing |
| [technical-research.md](research/technical-research.md) | TR-01… platform findings |

### Architecture — how it is built

| Document | Contents |
| --- | --- |
| [system-architecture.md](architecture/system-architecture.md) | layers, flows, failure modes, trade-offs |
| [technology-stack.md](architecture/technology-stack.md) | every dependency and why |
| [repository-structure.md](architecture/repository-structure.md) | folder map, import rules |
| [decisions/](architecture/decisions/) | ADR-001 … ADR-008 |

| ADR | Decision |
| --- | --- |
| [ADR-001](architecture/decisions/ADR-001-architecture-pattern.md) | layered modular monolith + service container |
| [ADR-002](architecture/decisions/ADR-002-persistence-and-migrations.md) | SQLite + hand-rolled additive migrations |
| [ADR-003](architecture/decisions/ADR-003-ai-provider-abstraction.md) | provider abstraction, no vendor SDK |
| [ADR-004](architecture/decisions/ADR-004-chat-execution-and-context.md) | chat execution and context bounds |
| [ADR-005](architecture/decisions/ADR-005-secrets-and-provider-keys.md) | secrets and provider keys |
| [ADR-006](architecture/decisions/ADR-006-deployment-and-runtime.md) | single container, long polling |
| [ADR-007](architecture/decisions/ADR-007-localization.md) | two complete catalogs, parity test |
| [ADR-008](architecture/decisions/ADR-008-state-management-and-limits.md) | in-memory FSM and rate limits |

### Database

[database-design](database/database-design.md) ·
[entity-relationship-diagram](database/entity-relationship-diagram.md) ·
[data-dictionary](database/data-dictionary.md) ·
[indexes-and-constraints](database/indexes-and-constraints.md) ·
[migrations-strategy](database/migrations-strategy.md) ·
[seed-data-strategy](database/seed-data-strategy.md)

Artifacts: [`schema.sql`](../artifacts/database/schema.sql) (generated from metadata),
[`seed.sql`](../artifacts/database/seed.sql) (dev-only, idempotent),
[`er.mmd`](../artifacts/diagrams/er.mmd).

### Bot interface (the "API")

[api-design](api/api-design.md) · [authentication](api/authentication.md) ·
[error-handling](api/error-handling.md) · [rate-limiting](api/rate-limiting.md)

Machine-readable: [`telegram-interface.json`](../artifacts/api/telegram-interface.json)
(24 callback namespaces, 10 commands, 10 user-facing failure keys). There is no OpenAPI document because
there is no HTTP surface.

### Security

[security-architecture](security/security-architecture.md) ·
[threat-model](security/threat-model.md) · [authentication-authorization](security/authentication-authorization.md) ·
[data-protection](security/data-protection.md) · [secrets-management](security/secrets-management.md) ·
[security-testing](security/security-testing.md) · [SECURITY.md](../SECURITY.md)

### Design (chat UX, not screens)

[design-principles](design/design-principles.md) · [design-system](design/design-system.md) ·
[components](design/components.md) · [responsive-design](design/responsive-design.md) ·
[accessibility](design/accessibility.md)

### Testing

[testing-strategy](testing/testing-strategy.md) · [test-plan](testing/test-plan.md) ·
[test-cases](testing/test-cases.md) (T-01…T-114 with AUTO/GAP/MANUAL) ·
[acceptance-criteria](testing/acceptance-criteria.md) · [performance-testing](testing/performance-testing.md) ·
[regression-testing](testing/regression-testing.md)

### DevOps

[development-environment](devops/development-environment.md) · [environment-variables](devops/environment-variables.md) ·
[ci-cd](devops/ci-cd.md) · [deployment](devops/deployment.md) · [monitoring-logging](devops/monitoring-logging.md) ·
[backup-recovery](devops/backup-recovery.md) · [operations-runbook](devops/operations-runbook.md)

Reference: [`env-reference.md`](../artifacts/configurations/env-reference.md).

### AI collaboration

[agent-compatibility.md](ai/agent-compatibility.md) — which tool reads which file, context
packs per task, and the guard rails against the usual agent failures.

### Project

[project-status](project/project-status.md) · [decisions-log](project/decisions-log.md) ·
[open-questions](project/open-questions.md) · [implementation-log](project/implementation-log.md)

## Reusable assets

| Folder | Contents |
| --- | --- |
| [`prompts/`](../prompts/README.md) | 23 executable prompts, seven phases |
| [`skills/`](../skills/) | `telegram-handler`, `database-migration`, `persian-localization`, `ai-provider-integration` |
| [`templates/adr/`](../templates/adr/README.md) | ADR template and process |
| [`templates/documentation/`](../templates/documentation/README.md) | doc template and writing conventions |
| [`manifest/`](../manifest/) | documentation index, requirements traceability, generation status |
| [`artifacts/diagrams/`](../artifacts/diagrams/) | Mermaid sources: context, pipeline, chat sequence, lifecycle, ER |

## Conventions in this documentation set

- **Grounded:** every behavioural claim names a file, symbol, config field, or table.
- **Honest:** gaps are documented, not smoothed over — see [project status §5](project/project-status.md#5-known-issues-ranked).
- **Traceable:** `FR-*` → `TASK-*` → tests, in
  [`requirements-traceability.csv`](../manifest/requirements-traceability.csv).
- **Unknowns are marked:** `[UNKNOWN — USER INPUT REQUIRED]` means nobody has answered yet.
- **Unverified is labelled:** live bot runs, provider calls, CI execution and deployments
  are stated as unverified wherever they are relevant.

## Keeping it true

1. Change code → update the doc that states the contract.
2. Change a requirement → update the CSV row.
3. Add a document → add it to `manifest/documentation-index.json`.
4. Run the link check before merging docs.
