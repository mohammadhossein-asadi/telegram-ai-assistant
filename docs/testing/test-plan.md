# Test Plan

Scope: release-level verification of the Telegram AI Assistant. Levels refer to
[testing strategy](testing-strategy.md).

## 1. Objectives

1. Prove the eight user journeys work end to end in both languages.
2. Prove no user can read or modify another user's data.
3. Prove an upgrade from schema v1 preserves data.
4. Prove the bot degrades instead of crashing on provider failures.

## 2. Scope

**In scope:** chat engine, context assembly, prompt composition, conversations CRUD,
personas, prompts, memory, models/routing, tools, settings, developer screen, about,
admin, localization, migrations, rate limiting, error rendering.

**Out of scope:** Telegram platform behaviour, AI model quality/hallucination, host
networking, Docker image internals beyond boot.

## 3. Test levels and ownership

| Level | Who | When | Artefact |
| --- | --- | --- | --- |
| Unit + service (automated) | contributor | every commit | `pytest` |
| Handler (automated, target) | contributor | every PR touching handlers | TASK-101 |
| Migration (automated) | contributor | every schema change | `test_migrations.py` |
| Manual smoke (real token) | maintainer | before release | §6 checklist |
| Manual language pass | maintainer/native speaker | before release | FA + EN walkthrough |
| Security checks | maintainer | before release | [security testing](../security/security-testing.md) |

## 4. Entry criteria

- `pytest -q` passes locally (32 tests).
- `.env` configured with a real `BOT_TOKEN` and a working `AI_API_KEY` for smoke tests.
- A test Telegram account (not the operator's main account) exists.
- Database backed up before migration tests against real data.

## 5. Exit criteria

| Criterion | Threshold |
| --- | --- |
| Automated suite | 100% pass, no skips added for this release |
| Smoke scenarios (S1–S10) | all pass |
| Language pass | both locales, no missing keys, no truncation |
| Security checks | no open High item introduced by the release |
| Migration test | v1 → current upgrade verified on a copy of a real DB |
| Known defects | documented in the implementation log with severity |

## 6. Smoke scenarios (manual, real bot)

| # | Scenario | Steps | Expected |
| --- | --- | --- | --- |
| S1 | Onboarding | new account → `/start` | welcome, menu, user row created |
| S2 | First chat | tap Chat → send "hello" | typing indicator, reply persisted (2 messages) |
| S3 | Follow-up context | send "and in Persian?" | reply references the first message |
| S4 | Persona | Persona → Teacher → chat | answer style changes; persona shown on screen |
| S5 | Memory | Memory → ask "remember my name is X" (manual add) → chat | name used in a later reply |
| S6 | Conversation mgmt | `/new`, rename, pin, archive, delete (confirm) | list reflects each change |
| S7 | Tool | Tools → Summarize → paste text | summary returned, no message rows written |
| S8 | Model switch | Model → pick provider/model → chat | provider field on usage row matches |
| S9 | Language | `/lang` → English → navigate | all screens English; reply language unchanged unless set |
| S10 | Error path | temporarily set a bad `AI_API_KEY` → chat → restore | localized error, no crash, failed usage row |

## 7. Automated test inventory (current)

```bash
pytest -q
# tests/test_chat_engine.py        5
# tests/test_database.py           3
# tests/test_localization.py       4
# tests/test_migrations.py         3
# tests/test_personas_prompts.py   3
# tests/test_routing.py            8
# tests/test_text.py               6
# 32 passed
```

## 8. Environment matrix

| Environment | Purpose | Database |
| --- | --- | --- |
| Local dev | iteration | `./data/bot.db` or in-memory |
| CI | regression | in-memory |
| Staging bot (optional) | smoke with real provider | separate SQLite file, separate bot token |
| Production | real users | `./data/bot.db` on a volume |

**Never** point a test run at the production database. Migration tests must use a copy.

## 9. Risks to the plan

| Risk | Mitigation |
| --- | --- |
| No API key available to contributors | fake provider covers logic; maintainer runs smoke |
| Manual steps skipped under time pressure | exit criteria are mandatory for a tagged release |
| Test DB drift | tests always create the schema from models |
| i18n regressions in Persian | native-speaker review in the checklist |

## 10. Reporting

- Automated results: CI log (once the workflow runs) or pasted local output.
- Manual results: a short table in the release notes/`CHANGELOG.md` listing S1–S10 with
  pass/fail and the build identifier.
- Defects: recorded in [implementation log](../project/implementation-log.md) with
  severity and owner.
