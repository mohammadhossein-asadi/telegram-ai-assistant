# 22 — Release handoff

**Phase:** handoff · **Use when:** cutting a release.

## Role
Release manager producing a factual record.

## Inputs
- `docs/testing/acceptance-criteria.md`
- `CHANGELOG.md`, `HANDOFF.md`
- Test output and manual check results

## Task
1. Confirm the gates: tests, compile, locale parity, migration test, security checklist.
2. Update `CHANGELOG.md` (Added/Changed/Fixed/Known issues) — no unreleased claims.
3. Bump `BOT_VERSION` in `Settings` default and `.env.example`.
4. Tag `vX.Y.Z`; write release notes with upgrade and rollback steps.
5. Record what was **not** verified (e.g. no live provider test).
6. Hand over: current state, next three tasks, open questions.

## Constraints
- Never claim a check passed that was not run.
- Known issues stay in the notes; do not hide them behind "minor".
- No secrets, tokens or user data in release notes.

## Output
Release notes + updated changelog + handoff paragraph + unverified list.

## Verification
- Version string consistent across files.
- Upgrade and rollback steps are executable as written.
