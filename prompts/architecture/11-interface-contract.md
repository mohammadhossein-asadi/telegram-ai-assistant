# 11 — Interface contract

**Phase:** architecture · **Use when:** adding a command, callback namespace, or changing an existing payload.

## Role
Owner of the bot's public interface (there is no HTTP API).

## Inputs
- `docs/api/api-design.md`
- `artifacts/api/telegram-interface.json`
- `src/bot/handlers/__init__.py` (router order)

## Task
1. Choose a namespace that does not collide (grep `F.data.startswith("ns:"`).
2. Define payloads as `namespace:action[:id]` with integer ids only.
3. Specify: auth tier, ownership check, success response, failure response, and whether
   the action is idempotent or destructive.
4. Update `docs/api/api-design.md` and the JSON contract in the same change.
5. State the compatibility impact: old inline keyboards may still carry the old payload.

## Constraints
- One namespace, one owning router.
- Callback data ≤ 64 bytes.
- Destructive actions require a distinct confirm payload.
- Unknown payloads must acknowledge with a toast and do nothing.

## Output
Contract row(s) + handler stub plan + compatibility note.

## Verification
- `python -m json.tool artifacts/api/telegram-interface.json`
- Grep shows exactly one handler per payload prefix.
