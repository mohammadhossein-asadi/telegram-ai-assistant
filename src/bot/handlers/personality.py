from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.helpers import get_prefs
from bot.keyboards import common as kb
from bot.ui import safe_edit, t
from bot.views import persona_text
from core.container import container
from utils.states import PersonaFlow

router = Router(name="personality")


@router.callback_query(F.data == "menu:persona")
async def cb_persona(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    prefs = await get_prefs(user)
    await safe_edit(call, persona_text(lang, prefs), kb.persona_kb(lang, prefs))


@router.callback_query(F.data == "pv:presets")
async def cb_presets(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    prefs = await get_prefs(user)
    await safe_edit(call, t(lang, "persona.presets"), kb.presets_kb(lang, prefs.personality))


@router.callback_query(F.data == "pv:style")
async def cb_styles(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    prefs = await get_prefs(user)
    await safe_edit(call, t(lang, "persona.style"), kb.styles_kb(lang, prefs.style))


@router.callback_query(F.data == "pv:tone")
async def cb_tones(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    prefs = await get_prefs(user)
    await safe_edit(call, t(lang, "persona.tone"), kb.tones_kb(lang, prefs.tone))


@router.callback_query(F.data == "pv:cr")
async def cb_creativity(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    prefs = await get_prefs(user)
    await safe_edit(call, t(lang, "persona.creativity"), kb.creativity_kb(lang, prefs.creativity))


@router.callback_query(F.data.startswith("ps:"))
async def cb_set_preset(call: CallbackQuery, user, lang: str) -> None:
    value = call.data.split(":", 1)[1]
    if value in kb.PRESETS:
        await container.user_settings.update(user.id, personality=value)
    prefs = await get_prefs(user)
    await call.answer(t(lang, "common.saved"))
    await safe_edit(call, persona_text(lang, prefs), kb.persona_kb(lang, prefs))


@router.callback_query(F.data.startswith("st:"))
async def cb_set_style(call: CallbackQuery, user, lang: str) -> None:
    value = call.data.split(":", 1)[1]
    if value in kb.STYLES:
        await container.user_settings.update(user.id, style=value)
    prefs = await get_prefs(user)
    await call.answer(t(lang, "common.saved"))
    await safe_edit(call, t(lang, "persona.style"), kb.styles_kb(lang, prefs.style))


@router.callback_query(F.data.startswith("tn:"))
async def cb_set_tone(call: CallbackQuery, user, lang: str) -> None:
    value = call.data.split(":", 1)[1]
    if value in kb.TONES:
        await container.user_settings.update(user.id, tone=value)
    prefs = await get_prefs(user)
    await call.answer(t(lang, "common.saved"))
    await safe_edit(call, t(lang, "persona.tone"), kb.tones_kb(lang, prefs.tone))


@router.callback_query(F.data.startswith("cr:"))
async def cb_set_creativity(call: CallbackQuery, user, lang: str) -> None:
    value = call.data.split(":", 1)[1]
    if value in kb.CREATIVITY:
        await container.user_settings.update(user.id, creativity=value)
    prefs = await get_prefs(user)
    await call.answer(t(lang, "common.saved"))
    await safe_edit(call, t(lang, "persona.creativity"), kb.creativity_kb(lang, prefs.creativity))


@router.callback_query(F.data == "pv:custom")
async def cb_custom(call: CallbackQuery, lang: str, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(PersonaFlow.custom)
    await safe_edit(call, t(lang, "persona.ask_custom"), kb.back_home_kb(lang))


@router.message(StateFilter(PersonaFlow.custom), F.text)
async def on_custom_persona(message: Message, user, lang: str, state: FSMContext) -> None:
    await container.user_settings.update(
        user.id, custom_instructions=message.text[:2000], personality="custom"
    )
    await state.clear()
    await message.answer(t(lang, "persona.custom_saved"), reply_markup=kb.persona_kb(lang, await get_prefs(user)))
