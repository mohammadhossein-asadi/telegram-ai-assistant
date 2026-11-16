# 18 — Regression review

**Phase:** testing · **Use when:** before merging a change that touches shared code.

## Role
Reviewer hunting for collateral damage.

## Inputs
- The diff
- `docs/testing/regression-testing.md` (R1–R6 failure modes)
- `docs/testing/test-cases.md`

## Task
1. Identify every shared symbol the diff changes (utils, repositories, prompts, config).
2. For each, list call sites and whether they were considered.
3. Check the historically fragile areas: duplicate router decorators, callback namespace
   collisions, locale parity, migration idempotency, README/doc claims.
4. Verify the automated suite still passes and no test was weakened.
5. State residual risk in one sentence.

## Constraints
- "Tests pass" alone is not a regression review.
- Do not accept deleted assertions without a stated behaviour change.
- Do not re-run unrelated suites; target the affected area.

## Output
Call-site table, checklist results, residual risk, blocking issues (if any).

## Verification
- Paste the test command and its result.
- Each risk has either a test or an explicit "uncovered".
