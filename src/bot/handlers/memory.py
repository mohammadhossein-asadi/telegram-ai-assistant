from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.helpers import ensure_conversation, get_prefs
from bot.keyboards import common as kb
from bot.ui import safe_edit, t
from bot.views import memory_text
from core.container import container

router = Router(name="memory")


@router.callback_query(F.data == "menu:memory")
async def cb_memory(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    prefs = await get_prefs(user)
    count = await container.memory.count(user.id)
    await safe_edit(
        call,
        memory_text(lang, prefs, container.config.max_context_messages, count),
        kb.memory_kb(lang, prefs.memory_enabled),
    )


@router.callback_query(F.data == "mem:toggle")
async def cb_toggle(call: CallbackQuery, user, lang: str) -> None:
    prefs = await get_prefs(user)
    prefs = await container.user_settings.update(user.id, memory_enabled=not prefs.memory_enabled)
    await call.answer(
        t(lang, "memory.toggled_on") if prefs.memory_enabled else t(lang, "memory.toggled_off")
    )
    count = await container.memory.count(user.id)
    await safe_edit(
        call,
        memory_text(lang, prefs, container.config.max_context_messages, count),
        kb.memory_kb(lang, prefs.memory_enabled),
    )


@router.callback_query(F.data == "mem:clear")
async def cb_clear(call: CallbackQuery, user, lang: str) -> None:
    prefs = await get_prefs(user)
    conv = await ensure_conversation(user, prefs)
    await container.messages.clear(conv.id)
    await call.answer(t(lang, "memory.cleared"))
    count = await container.memory.count(user.id)
    await safe_edit(
        call,
        memory_text(lang, prefs, container.config.max_context_messages, count),
        kb.memory_kb(lang, prefs.memory_enabled),
    )


@router.callback_query(F.data == "mem:clearall")
async def cb_clear_all(call: CallbackQuery, user, lang: str) -> None:
    prefs = await get_prefs(user)
    await container.memory.clear(user.id)
    for conv in await container.conversations.list_for_user(user.id, include_archived=True):
        await container.messages.clear(conv.id)
    await call.answer(t(lang, "memory.cleared_all"))
    await safe_edit(
        call,
        memory_text(lang, prefs, container.config.max_context_messages, 0),
        kb.memory_kb(lang, prefs.memory_enabled),
    )
