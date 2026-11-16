# 02 — Persona definition

**Phase:** discovery · **Use when:** adding a persona, refining an existing one, or checking that a feature serves a real user.

## Role
Product researcher for a two-persona-priority bot (Persian students/professionals,
English-speaking developers).

## Inputs
- `docs/product/user-personas.md` (P1–P5)
- `docs/product/user-journeys.md`
- `docs/product/user-stories.md`

## Task
1. Choose or create a persona record with: name, context, goals, constraints,
   language, device, frequency, current workaround.
2. Map three concrete scenarios to existing journeys (J0–J10). Name the journey id.
3. For each scenario, identify the first point of friction in the current bot.
4. Propose one improvement per friction point, ordered by effort.
5. Note which requirements (`FR-*`, `US-*`) the improvement serves.

## Constraints
- Personas must be distinguishable by behaviour, not demographics alone.
- No invented statistics ("70% of users…"). Use qualitative statements.
- A persona that no journey exercises is a red flag — say so.

## Output
Persona table + scenario table + friction/improvement list.

## Verification
- Every scenario references a real journey id.
- Every improvement references at least one existing requirement id or states that a new
  one is needed.
