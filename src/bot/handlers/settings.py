from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.helpers import get_prefs
from bot.keyboards import common as kb
from bot.ui import safe_edit, t
from bot.views import settings_text
from core.container import container

router = Router(name="settings")

_RESPONSE_CYCLE = ["auto", "fa", "en"]


async def _render(call: CallbackQuery, user, lang: str) -> None:
    prefs = await get_prefs(user)
    model = prefs.model or container.config.ai_model
    await safe_edit(
        call,
        settings_text(lang, prefs, model, prefs.memory_enabled),
        kb.settings_kb(lang, prefs, prefs.memory_enabled),
    )


@router.callback_query(F.data == "menu:settings")
async def cb_settings(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    await _render(call, user, lang)


@router.callback_query(F.data == "set:rlang")
async def cb_response_lang(call: CallbackQuery, user, lang: str) -> None:
    prefs = await get_prefs(user)
    try:
        index = _RESPONSE_CYCLE.index(prefs.response_language)
    except ValueError:
        index = 0
    await container.user_settings.update(
        user.id, response_language=_RESPONSE_CYCLE[(index + 1) % len(_RESPONSE_CYCLE)]
    )
    await call.answer(t(lang, "common.saved"))
    await _render(call, user, lang)


@router.callback_query(F.data == "set:emoji")
async def cb_emoji(call: CallbackQuery, user, lang: str) -> None:
    prefs = await get_prefs(user)
    await container.user_settings.update(user.id, emoji_enabled=not prefs.emoji_enabled)
    await call.answer(t(lang, "common.saved"))
    await _render(call, user, lang)


@router.callback_query(F.data == "set:mem")
async def cb_memory(call: CallbackQuery, user, lang: str) -> None:
    prefs = await get_prefs(user)
    await container.user_settings.update(user.id, memory_enabled=not prefs.memory_enabled)
    await call.answer(t(lang, "common.saved"))
    await _render(call, user, lang)


@router.callback_query(F.data == "set:routing")
async def cb_routing(call: CallbackQuery, user, lang: str) -> None:
    prefs = await get_prefs(user)
    await container.user_settings.update(user.id, auto_routing=not prefs.auto_routing)
    await call.answer(t(lang, "common.saved"))
    await _render(call, user, lang)


@router.callback_query(F.data == "set:privacy")
async def cb_privacy(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    await safe_edit(call, t(lang, "settings.privacy_text"), kb.back_home_kb(lang, "menu:settings"))


@router.callback_query(F.data == "set:reset")
async def cb_reset(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    await safe_edit(
        call,
        t(lang, "settings.reset_confirm"),
        kb.confirm_kb(lang, "set:resetok", "menu:settings"),
    )


@router.callback_query(F.data == "set:resetok")
async def cb_reset_confirm(call: CallbackQuery, user, lang: str) -> None:
    await container.user_settings.reset(user.id)
    await call.answer(t(lang, "settings.reset_done"))
    await _render(call, user, lang)
