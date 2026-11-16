# 06 — Technical feasibility

**Phase:** research · **Use when:** evaluating whether a requested capability fits the current stack.

## Role
Engineer assessing feasibility inside a single-process aiogram + SQLite deployment.

## Inputs
- `docs/architecture/system-architecture.md`
- `docs/architecture/technology-stack.md`
- `docs/research/technical-research.md`

## Task
1. Restate the capability as a technical requirement.
2. Determine where it would live (handler, service, repository, provider, infra).
3. Identify hard blockers: Telegram API limits, SQLite single-writer, no HTTP surface,
   in-memory FSM, provider protocol shape.
4. Estimate effort in the project's own terms (files touched, new tables, new deps).
5. Offer at most two alternatives, compare on effort/risk/reversibility.
6. State what cannot be verified without credentials or a real Telegram client.

## Constraints
- Do not assume a webhook, queue, cache server, or multi-process deployment.
- Do not propose replacing aiogram/SQLAlchemy.
- Be explicit when a feature is impossible without an architectural change.

## Output
Feasibility verdict (fits / fits with caveats / requires architecture change) +
evidence table + options + unverifiable items.

## Verification
- Each blocker cites a file, config field, or documented platform limit.
