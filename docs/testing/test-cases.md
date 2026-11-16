# Test Cases

IDs are stable and referenced from requirements traceability. **Status** reflects
reality: `AUTO` = covered by an existing test, `GAP` = no test exists, `MANUAL` = only
verifiable with a Telegram client.

## 1. Chat engine

| ID | Requirement | Case | Expected | Status |
| --- | --- | --- | --- | --- |
| T-01 | FR-CHAT-001 | send a first message | assistant reply returned; 2 message rows | AUTO `test_respond_persists_both_turns` |
| T-02 | FR-CHAT-002 | 30 messages in history, limit 20 | provider receives ≤ 21 messages (20 + new) | AUTO `test_engine_respects_max_context` |
| T-03 | FR-CHAT-003 | conversation.model set | provider called with that model | AUTO `test_conversation_model_override` |
| T-04 | FR-PERS-002 | persona assigned to conversation | persona instructions appear in the system prompt | AUTO `test_persona_instructions_reach_system_prompt` |
| T-05 | FR-TOOL-002 | run summarize tool | provider called; no message rows created | AUTO `test_tool_run_does_not_write_history` |
| T-06 | FR-CHAT-004 | provider raises `AIError` | exception propagates; no user/assistant rows; failed usage row | GAP |
| T-07 | FR-MEM-001 | memory disabled | memory facts absent from prompt | GAP |
| T-08 | FR-CHAT-005 | summary present | summary text included in system prompt | GAP |
| T-09 | FR-MEM-003 | 25 memory facts stored | prompt includes at most 20 | GAP |
| T-10 | FR-I18N-04 | reply language `fa` | instruction forces Persian output | GAP |

## 2. Conversations

| ID | Requirement | Case | Expected | Status |
| --- | --- | --- | --- | --- |
| T-11 | FR-CONV-001 | create conversation | row exists, becomes current | GAP |
| T-12 | FR-CONV-002 | rename persists; long titles truncated to the column limit | new title visible in list | GAP |
| T-13 | FR-CONV-003 | pin then list | pinned appears first | AUTO `test_conversation_pin_persona_model_search` |
| T-14 | FR-CONV-004 | archive then list (default) | archived hidden; shown under archived filter | GAP |
| T-15 | FR-CONV-005 | delete with confirm | conversation + messages removed | AUTO (repository level; cascade asserted in `test_conversation_and_messages_are_isolated`) |
| T-16 | FR-CONV-006 | export | text contains all messages in order | GAP |
| T-17 | FR-CONV-007 | search by title fragment | matching conversations only, scoped to the caller | AUTO `test_conversation_pin_persona_model_search` |
| T-18 | FR-CONV-008 | summary generation | `conversations.summary` non-empty; usage row action=summarize | GAP |

## 3. Ownership and authorization

| ID | Requirement | Case | Expected | Status |
| --- | --- | --- | --- | --- |
| T-20 | NFR-SEC-002 | user B fetches user A's conversation | `None` | AUTO `test_conversation_and_messages_are_isolated` |
| T-21 | NFR-SEC-002 | `conv:open:<foreign id>` | empty toast, no data leak | GAP (handler level; repository level is AUTO) |
| T-22 | FR-ADMIN-001 | non-admin sends `/admin` | no panel | GAP |
| T-23 | FR-ADMIN-001 | non-admin triggers `adm:stats` | no data | GAP |
| T-24 | FR-ADMIN-002 | blocked user sends a message | no reply, no new messages | MANUAL |
| T-25 | FR-CPERS-004 | delete another user's persona | not found, row intact | AUTO `test_persona_crud_and_default` |

## 4. Settings and personalization

| ID | Requirement | Case | Expected | Status |
| --- | --- | --- | --- | --- |
| T-30 | FR-I18N-01 | switch language to EN | `users.language='en'`; next screen EN | MANUAL |
| T-31 | FR-I18N-03 | switch reply language to FA | prompt contains Persian instruction | GAP |
| T-32 | FR-PERS-001 | choose personality `teacher` | stored; prompt reflects it | GAP |
| T-33 | FR-PERS-003 | creativity high | temperature 1.1 passed | GAP |
| T-34 | FR-PERS-004 | custom instructions set | appended to system prompt | GAP |
| T-35 | FR-ADMIN-003 | reset settings → confirm | defaults restored; conversations kept | GAP |

## 5. Memory

| ID | Case | Expected | Status |
| --- | --- | --- | --- |
| T-40 | add memory key | row created | AUTO `test_database.py` (upsert) |
| T-41 | add duplicate key | value updated, not duplicated | AUTO |
| T-42 | clear all memory | no rows for the user | AUTO |
| T-43 | memory toggle off | facts not injected | GAP |

## 6. Personas and prompts

| ID | Case | Expected | Status |
| --- | --- | --- | --- |
| T-50 | create persona | row with user_id | AUTO `test_personas_prompts.py` |
| T-51 | duplicate persona name | `create()` upserts: same id, instructions/emoji updated | AUTO `test_persona_crud_and_default` |
| T-52 | set default persona | previous default cleared | AUTO |
| T-53 | delete persona | row gone; conversation keeps history | GAP |
| T-54 | create prompt | row created | AUTO |
| T-55 | run prompt | body sent to provider with placeholders filled | GAP |

## 7. Models and routing

| ID | Case | Expected | Status |
| --- | --- | --- | --- |
| T-60 | classify "fix this bug" | `coding` | AUTO `test_routing.py` |
| T-61 | classify Persian "ترجمه کن" | `translation` | GAP |
| T-62 | auto-routing on, provider lacks capability | falls back to general provider | AUTO |
| T-63 | unknown model string | resolves to default provider | AUTO |
| T-64 | auto-routing off | user model used | GAP |

## 8. Localization

| ID | Case | Expected | Status |
| --- | --- | --- | --- |
| T-70 | both catalogs load | non-empty dicts | AUTO |
| T-71 | key sets identical | no diff | AUTO |
| T-72 | format with kwargs | substituted | AUTO |
| T-73 | unknown language | falls back to default | AUTO |
| T-74 | placeholder set parity | identical placeholders | GAP (recommended) |

## 9. Persistence and migrations

| ID | Case | Expected | Status |
| --- | --- | --- | --- |
| T-80 | fresh schema | 10 tables, version=2 | AUTO `test_migrations.py` |
| T-81 | run migrations twice | no error, single version rows | AUTO |
| T-82 | v1 legacy schema upgrade | v2 columns present with defaults | AUTO |
| T-83 | conversation isolation | each user sees only own rows | AUTO `test_conversation_and_messages_are_isolated` |
| T-84 | cascade delete conversation | messages removed | AUTO (same test, after `convs.delete`) |

## 10. Text utilities

| ID | Case | Expected | Status |
| --- | --- | --- | --- |
| T-90 | split 8000 chars | chunks ≤ 3500 | AUTO |
| T-91 | escape `<b>` | `&lt;b&gt;` | AUTO |
| T-92 | markdown bold → HTML | `<b>` | AUTO `test_markdown_is_escaped_and_converted` |
| T-93 | fenced code → `<pre>` | preserved, escaped | AUTO |
| T-94 | detect Persian text | `fa` | AUTO |
| T-95 | detect English text | `en` | AUTO |

## 11. Rate limiting

| ID | Case | Expected | Status |
| --- | --- | --- | --- |
| T-100 | 21st request in a minute | blocked, localized error, no provider call | GAP |
| T-101 | daily cap reached | blocked, `errors.daily_limited` | GAP |
| T-102 | admin not limited | request proceeds | GAP |
| T-103 | repository `daily_allowed` with `max_daily_requests=0` | returns True (unlimited branch; not reachable via env) | GAP |

## 12. Errors and delivery

| ID | Case | Expected | Status |
| --- | --- | --- | --- |
| T-110 | Telegram rejects HTML | plain-text resend | GAP |
| T-111 | edit with no change | error swallowed, no crash | GAP |
| T-112 | provider 401 | `errors.ai`, failed usage row | GAP |
| T-113 | provider timeout | `errors.ai` after one retry (complete) | GAP |
| T-114 | GitHub 403 | Developer screen shows fallback | MANUAL |

## 13. Summary

| Status | Count (of the cases above) |
| --- | --- |
| AUTO | 35 |
| GAP | 32 |
| MANUAL | 3 |

The AUTO cases are the existing 32 tests mapped to cases (some tests cover more than
one case). The GAP list is the actionable backlog; T-20/T-21 should be first.
