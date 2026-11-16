from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from aiogram.types import CallbackQuery

from bot.helpers import current_model, ensure_conversation, get_prefs
from bot.keyboards import common as kb
from bot.ui import safe_edit, send_ai, t
from core.container import container
from core.logging import get_logger
from services.ai import AIConfigurationError, AIError, AITimeoutError
from utils.text import derive_title

log = get_logger(__name__)
router = Router(name="chat")

_locks: dict[int, asyncio.Lock] = {}


def _lock_for(user_id: int) -> asyncio.Lock:
    return _locks.setdefault(user_id, asyncio.Lock())


@router.callback_query(F.data == "menu:chat")
async def cb_chat(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    prefs = await get_prefs(user)
    conv = await ensure_conversation(user, prefs)
    text = t(lang, "chat.hint", title=conv.title)
    if conv.summary:
        text += f"\n\n🧾 {conv.summary[:400]}"
    await safe_edit(call, text, kb.open_conversation_kb(lang, conv.id))


@router.message(Command("new"))
async def cmd_new(message: Message, user, lang: str) -> None:
    conv = await container.conversations.create(user.id, title="New chat")
    await container.user_settings.update(user.id, current_conversation_id=conv.id)
    await message.answer(t(lang, "start.new_chat_started"), reply_markup=kb.chat_kb(lang))


@router.message(Command("retry"))
async def cmd_retry(message: Message, user, lang: str) -> None:
    prefs = await get_prefs(user)
    conv = await ensure_conversation(user, prefs)
    history = await container.messages.recent(conv.id, 4)
    last_user = next((m for m in reversed(history) if m.role == "user"), None)
    if last_user is None:
        await message.answer(t(lang, "chat.empty"))
        return
    await _generate(message, user, lang, conv, last_user.content, regenerate=True)


@router.message(StateFilter(None), F.text)
async def on_text(message: Message, user, lang: str) -> None:
    text = (message.text or "").strip()
    if not text or text.startswith("/"):
        return

    if not container.usage.check_rate(user.telegram_id):
        await message.answer(t(lang, "errors.rate_limited"))
        return
    if not await container.usage.daily_allowed(user.id):
        await message.answer(
            t(lang, "errors.daily_limited", limit=container.config.max_daily_requests)
        )
        return

    prefs = await get_prefs(user)
    conv = await ensure_conversation(user, prefs)
    await _generate(message, user, lang, conv, text)


async def _generate(message: Message, user, lang: str, conv, text: str, regenerate: bool = False) -> None:
    lock = _lock_for(user.id)
    if lock.locked():
        await message.answer(t(lang, "errors.rate_limited"))
        return

    async with lock:
        await message.bot.send_chat_action(message.chat.id, "typing")
        try:
            if regenerate:
                response = await container.chat_engine.regenerate(user, conv, text)
            else:
                response = await container.chat_engine.respond(user, conv, text)
        except AIConfigurationError:
            await message.answer(t(lang, "chat.blocked"))
            return
        except AITimeoutError:
            await message.answer(t(lang, "errors.ai_timeout"))
            return
        except AIError as exc:
            await message.answer(t(lang, "errors.ai", detail=str(exc)[:300]))
            return
        except Exception as exc:  # noqa: BLE001 - last-resort guard
            log.exception("Chat failure: %s", exc)
            await message.answer(t(lang, "errors.generic"))
            return

        # Give the conversation a meaningful title from its first user message.
        history = await container.messages.recent(conv.id, 3)
        user_turns = [m for m in history if m.role == "user"]
        if len(user_turns) == 1 and conv.title in ("New chat", ""):
            await container.conversations.rename(conv.id, user.id, derive_title(text))

        await send_ai(message, response.text, kb.chat_kb(lang))
