---
name: telegram-handler
description: Add or modify a Telegram command/callback in this aiogram 3 bot — new router, callback namespace, keyboard, view and locale keys, without breaking router order or ownership checks.
---

# Skill: add a Telegram handler

Use when adding a command, a callback action, or an inline keyboard to this bot.

## Preconditions

- Read `docs/api/api-design.md` for the payload grammar and tiers.
- Read `src/bot/handlers/__init__.py` — router order is a contract.
- Confirm the namespace is unused: `grep -rn 'startswith("ns:"' src/bot/handlers`.

## Steps

### 1. Pick the payload

```
namespace:action[:integer-id]
conv:open:12        persona:edit:3      set:lang:fa
```

Rules: lowercase, `:` separated, ≤ 64 bytes, integer ids only, one namespace per router.
Destructive actions get a separate `ns:del` + `ns:delok:<id>` pair.

### 2. Add the handler module or extend an existing one

```python
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards import common as kb
from bot.ui import safe_edit, t
from core.container import container
from core.logging import get_logger

logger = get_logger(__name__)
router = Router(name="domain")


@router.callback_query(F.data.startswith("dom:"))
async def on_action(cb: CallbackQuery, user, lang: str) -> None:
    await cb.answer()
    ...
```

`user` and `lang` are injected by `UserMiddleware`; do not re-query them. `t(lang, key,
**kwargs)` is imported from `bot.ui` and falls back to the key string when missing, so a
mistake is silent at runtime — the parity test is your guard.

### 3. Register the router (correct position)

In `src/bot/handlers/__init__.py:ROUTERS`, insert **before** `chat.router`.
The chat router catches plain text, so anything after it becomes unreachable.

### 4. Ownership

Never trust the id in the payload:

```python
conv = await container.conversations.get(conv_id, user.id)   # user_id is optional but mandatory here
if conv is None:
    await cb.answer(t(lang, "common.error"))   # no dedicated not-found string exists
    return
```

### 5. Rendering

- Text: `src/bot/views.py` (pure function taking the model).
- Keyboard: `src/bot/keyboards/common.py`.
- Delivery: `safe_edit()` from `bot/ui.py` for edits, `send_long()` for AI output.
- Escape user/model text with `utils/text.escape_html` before `markdown_to_html`.

### 6. Locale keys

Add to **both** `src/localization/en.json` and `fa.json`, same namespace, same
placeholders. Persian needs ZWNJ. Run `pytest -q tests/test_localization.py`.

### 7. Document the contract

Add the namespace to `artifacts/api/telegram-interface.json` and a row to
`docs/api/api-design.md`.

## Verification

```bash
grep -rn 'namespace:action' src/bot/handlers            # exactly one owner
pytest -q tests/test_localization.py
pytest -q
python -m compileall -q src
```

## Failure modes seen in this repo

| Mistake | Symptom |
| --- | --- |
| Router registered after `chat` | handler never fires |
| Duplicate decorator on one function | aiogram raises at startup |
| Missing `cb.answer()` | spinner hangs on the button |
| Editing an unchanged message | `TelegramBadRequest: message is not modified` |
| Raw model HTML | injection or silent formatting loss |
| Key in one catalog only | `KeyError` in that language |
