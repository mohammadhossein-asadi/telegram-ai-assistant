# 15 — Bug fix

**Phase:** implementation · **Use when:** a defect has a reproduction.

## Role
Debugger following evidence, not guesses.

## Inputs
- Reproduction steps and logs
- `docs/api/error-handling.md`, `HANDOFF.md` known issues
- The suspected module

## Task
1. Reproduce or trace the failure to a specific line using code reading and, where
   possible, a test.
2. State the root cause in one sentence. If you cannot, list what you ruled out instead
   of guessing.
3. Write a failing test that captures the defect (repository/service level if possible).
4. Apply the minimal fix.
5. Confirm the test passes and the suite is green.
6. Note any adjacent path with the same pattern (and whether it is fixed or left).

## Constraints
- Fix the cause, not the symptom (no swallowed exceptions, no retry masking).
- Do not change public behaviour beyond the defect.
- Do not "fix" a test assertion to match broken behaviour.

## Output
Root cause, test, fix, before/after output, related-path note.

## Verification
- Failing test demonstrated before the fix (paste the assertion error).
- `pytest -q` passes after.
