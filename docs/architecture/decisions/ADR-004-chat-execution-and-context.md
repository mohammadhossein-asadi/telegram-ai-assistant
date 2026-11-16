# ADR-004 — Persist after success, bounded context, tools outside history

- **Status:** Accepted (implemented)
- **Date:** 2026-11-16
- **Related:** [system architecture §7](../system-architecture.md), [FR-CHAT-*](../../product/functional-requirements.md)

## Context

A chat assistant must decide (a) what history to send, (b) when to write history,
and (c) whether one-shot tool calls share the conversation. Each choice affects
cost, correctness of follow-up questions, and the user's ability to retry.

Constraints: Telegram replies are slow relative to a UI; provider calls can fail;
the operator pays per token; a shared key must not be inflated by unnecessary
context.

## Problem

Define a chat execution model that keeps follow-ups coherent, bounds cost, and
leaves the database in a consistent state when the provider fails.

## Considered alternatives

| Decision point | Options | Verdict |
| --- | --- | --- |
| History write timing | write user turn before the call / write both after success | **both after success** |
| Context window | fixed char budget / last N messages / full history | **last N messages (default 20)** |
| History scope | per conversation / per user across conversations | **per conversation** (intentional isolation) |
| Failure handling | queue and retry / surface error + no write / store user turn only | **surface error, no write** |
| Tool calls | append to history / one-shot completion | **one-shot, no history write** |
| Streaming | stream tokens to Telegram / single response then chunk | **single response then chunk** |

## Decision

1. `ChatEngine.respond(user, conversation, text)`:
   - loads `UserSettings` (`get_or_create`), memories (only when enabled), persona
     instructions (only when assigned), and detects input language;
   - builds the system prompt, appends the conversation summary when present;
   - loads `messages.recent(conversation.id, MAX_CONTEXT_MESSAGES)` and appends the
     new user message;
   - resolves provider/model and calls `provider.chat(...)` with a temperature from
     the creativity level;
   - **on success only**: writes the user row and assistant row, touches the
     conversation, logs usage with latency and tokens;
   - on failure: logs a failed usage row (with the provider error text) and re-raises
     so the handler can render `errors.ai`.
2. `run_tool()` performs a one-shot `provider.complete()` with a system instruction,
   logs usage under `action=<tool>`, and writes nothing to `messages`.
3. `summarize_conversation()` reads up to the last 30 messages, builds a compact
   transcript, produces a 3–5 sentence summary in the user's language, and persists
   it to `conversations.summary`, which is then appended to future system prompts.
4. Replies are delivered as a single string split at 3500 characters, escaped and
   Markdown-converted before sending.

## Consequences

**Positive**

- No orphan user turns: history always has a paired assistant reply.
- Cost is bounded by `MAX_CONTEXT_MESSAGES` and ≤ 20 memory facts.
- Tool output cannot pollute conversation context (predictable prompts, no drift).
- Retry semantics are clean: the last exchange is removable as a unit.

**Negative / accepted costs**

- On provider failure the user's message is not stored, so no "retry payload" exists
  in the DB; the user must resend (documented in `HANDOFF.md`).
- No streaming: perceived latency is the full generation time.
- Summaries consume tokens and are regenerated on demand only.

## Risks

| Risk | Mitigation |
| --- | --- |
| Context exceeds provider limits with huge messages | Telegram caps messages at 4096 chars; 20 turns ≈ ≤ 80k chars worst case — monitor if larger models/limits are used |
| Summary drifts from the transcript | summary is regenerated explicitly; shows in the conversation view |
| Double-send from a user tapping twice | per-user `asyncio.Lock` serialises |
| Failed call still costs tokens upstream | unavoidable; usage row records the failure for visibility |

## Verification

- `test_respond_persists_both_turns` — pairing and usage row.
- `test_engine_respects_max_context` — history is bounded by settings.
- `test_tool_run_does_not_write_history` — tools never touch `messages`.
- `test_persona_instructions_reach_system_prompt` — persona precedence.
