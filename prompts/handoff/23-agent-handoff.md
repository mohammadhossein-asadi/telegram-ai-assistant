# 23 — Agent handoff

**Phase:** handoff · **Use when:** ending a session, or handing work to another agent or human.

## Role
Engineer leaving a state that a stranger can continue without asking questions.

## Inputs
- Your session's changes and command output
- `HANDOFF.md`, `docs/project/implementation-log.md`, `docs/project/open-questions.md`

## Task
1. State what is done, verified, and **how** it was verified.
2. State what is in progress, including the exact next action.
3. List modified files, and which are committed vs uncommitted.
4. Record decisions made and why (link ADRs if any).
5. Record blockers and unverified claims explicitly.
6. Update `HANDOFF.md` and the implementation log; add open questions with owners.

## Constraints
- No "should work" claims. Either it ran, or it is unverified.
- No hidden state: mention uncommitted edits, generated files, changed configs.
- Do not leave a half-applied schema or migration.
- Do not commit or push unless asked.

## Output
Handoff block: **Done**, **Verified**, **In progress + next action**, **Files**,
**Decisions**, **Blockers/unverified**, **Open questions**.

## Verification
- A reader can reproduce your verification commands from the handoff alone.
