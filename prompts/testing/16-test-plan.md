# 16 — Test plan

**Phase:** testing · **Use when:** planning verification for a release or a risky change.

## Role
Test planner for an offline-first suite (pytest, in-memory SQLite, fake provider).

## Inputs
- `docs/testing/testing-strategy.md` (current 31 tests)
- `docs/testing/test-cases.md`
- The change or release scope

## Task
1. Map each changed behaviour to a test level (unit / service / manual).
2. List new test cases with IDs, following the existing `T-xx` scheme.
3. Identify what cannot be automated here (Telegram rendering, real provider, FSM flows)
   and write the manual steps.
4. Define entry and exit criteria, including which existing tests must still pass.
5. Estimate runtime; keep the suite under a few seconds.

## Constraints
- No network, no real tokens, no sleeps, no order dependence.
- Manual steps must be executable by someone with only a bot token.
- Do not propose coverage gates the project cannot enforce in CI today.

## Output
Test-case table + manual checklist + exit criteria + gaps.

## Verification
- Every new case names the observable assertion.
- No case duplicates an existing `T-xx`.
