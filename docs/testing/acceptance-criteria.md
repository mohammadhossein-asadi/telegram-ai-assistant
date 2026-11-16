# Acceptance Criteria (Release Level)

Story-level acceptance criteria live in
[user-stories](../product/user-stories.md) (US-001…US-026). This document defines what
must be true for a **release** to be accepted, expressed as verifiable statements.

## 1. Functional acceptance

| ID | Criterion | Verified by | Status |
| --- | --- | --- | --- |
| ACC-01 | A new user can start the bot, see a menu and send a message that receives an AI reply | S1, S2 | requires real token — **not run** |
| ACC-02 | Follow-up messages include prior context up to 20 turns | T-02 | AUTO |
| ACC-03 | Conversations can be created, renamed, pinned, archived, listed, searched and deleted | T-11…T-17 | partial (pin/search/delete AUTO, rest GAP) |
| ACC-04 | Personas can be created, edited, set default, assigned and deleted; ownership enforced | T-50…T-53 | AUTO (ownership + CRUD) |
| ACC-05 | Saved prompts can be created, categorised, edited, run and deleted | T-54, T-55 | partial (CRUD AUTO, run GAP) |
| ACC-06 | Memory facts can be added, overwritten, cleared and disabled | T-40…T-43 | AUTO (CRUD), GAP (toggle effect) |
| ACC-07 | All five tool families produce output without writing to history | T-05 | AUTO for summarize; others GAP |
| ACC-08 | Model selection and auto-routing choose a valid provider | T-60…T-64 | AUTO (classification/fallback), GAP (auto off) |
| ACC-09 | UI switches between Persian and English with complete catalogs | T-70…T-73 | AUTO |
| ACC-10 | AI reply language is independent of UI language | T-10, T-31 | GAP |
| ACC-11 | Developer screen renders GitHub profile and repos, and degrades when GitHub fails | S-gh, T-114 | MANUAL |
| ACC-12 | Admin can view stats/limits/health, add/delete providers, broadcast, block/unblock | T-22, T-23 | GAP / MANUAL |
| ACC-13 | Rate and daily limits block excess usage before the provider call | T-100…T-103 | GAP |

## 2. Non-functional acceptance

| ID | Criterion | Threshold | Verified by |
| --- | --- | --- | --- |
| ACC-20 | No user can read or modify another user's data through any handler | zero violations | T-20, T-25 (AUTO) + review of all repository calls |
| ACC-21 | Model output cannot inject HTML into a message | escaping before conversion | T-91, T-92 (AUTO) |
| ACC-22 | A provider failure never crashes the polling loop | error surfaced, process alive | manual (S10) |
| ACC-23 | Message chunking keeps every payload ≤ 4096 chars | ≤ 3500 per chunk | T-90 (AUTO) |
| ACC-24 | Upgrading a v1 database preserves rows and adds v2 columns | no data loss | T-82 (AUTO) |
| ACC-25 | No secret is committed or logged | scans clean | manual + provided CI job (not run) |
| ACC-26 | Bot boots from a clean checkout with only `.env` provided | `docker compose up` works | manual |
| ACC-27 | Backup and restore reproduce the same data | counts match | manual |

## 3. Quality gates

| Gate | Rule | Current |
| --- | --- | --- |
| Tests | 100% pass | 32/32 pass locally |
| Lint | **none configured** | — |
| Type check | **none configured** | — |
| Coverage | not measured | — |
| Review | at least one review for non-trivial changes | process, not enforced |
| Docs | new feature documented + traceability row | required by this package |

## 4. Release acceptance procedure

```markdown
1. [ ] pytest -q → all pass
2. [ ] CHANGELOG.md updated
3. [ ] Smoke scenarios S1–S10 executed (test-plan §6) with a real token
4. [ ] Language pass in FA and EN
5. [ ] Migration test on a copy of a real database
6. [ ] Security checklist (security-testing §3)
7. [ ] Known issues updated in project/implementation-log.md
8. [ ] Version tag created
```

## 5. Conditional acceptance

These are acceptable to ship **with disclosure**:

| Item | Disclosure location |
| --- | --- |
| Provider keys plaintext at rest | `SECURITY.md`, threat model T7 |
| In-memory FSM/limits reset on restart | HANDOFF known issues |
| No account deletion | privacy screen copy + data-protection §4 |
| No lint/type gate | CONTRIBUTING (quality section) |
| Handler-level tests missing | testing strategy §7 |

## 6. Sign-off

| Role | Name | Date |
| --- | --- | --- |
| Maintainer | Mohammadhossein Asadi | `[UNKNOWN — USER INPUT REQUIRED]` |
| Reviewer (optional) | `[UNKNOWN — USER INPUT REQUIRED]` | — |
