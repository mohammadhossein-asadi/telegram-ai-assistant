from __future__ import annotations

import json

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.helpers import ensure_conversation, get_prefs
from bot.keyboards import common as kb
from bot.ui import safe_edit, t
from core.container import container
from utils.states import PersonaStudioFlow

router = Router(name="custom_personas")


@router.callback_query(F.data == "cps:list")
async def cb_list(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    personas = await container.personas.list_for_user(user.id)
    text = t(lang, "cpersona.title")
    if not personas:
        text += f"\n\n{t(lang, 'cpersona.empty')}"
    await safe_edit(call, text, kb.custom_personas_kb(lang, personas))


@router.callback_query(F.data == "cps:new")
async def cb_new(call: CallbackQuery, lang: str, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(PersonaStudioFlow.new)
    await safe_edit(call, t(lang, "cpersona.create_hint"), kb.back_home_kb(lang, "cps:list"))


@router.callback_query(F.data == "cps:import")
async def cb_import(call: CallbackQuery, lang: str, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(PersonaStudioFlow.import_json)
    await safe_edit(call, t(lang, "cpersona.import_hint"), kb.back_home_kb(lang, "cps:list"))


@router.message(StateFilter(PersonaStudioFlow.new), F.text)
async def on_new(message: Message, user, lang: str, state: FSMContext) -> None:
    parsed = _split(message.text or "")
    if not parsed:
        await message.answer(t(lang, "cpersona.invalid"))
        return
    name, instructions = parsed
    await container.personas.create(user.id, name, instructions)
    await state.clear()
    await message.answer(t(lang, "cpersona.created"))


@router.message(StateFilter(PersonaStudioFlow.import_json), F.text)
async def on_import(message: Message, user, lang: str, state: FSMContext) -> None:
    try:
        data = json.loads(message.text or "{}")
        name = str(data["name"]).strip()
        instructions = str(data["instructions"]).strip()
        emoji = str(data.get("emoji") or "🎭")[:8]
    except (ValueError, KeyError, TypeError):
        await message.answer(t(lang, "cpersona.invalid"))
        return
    if not name or not instructions:
        await message.answer(t(lang, "cpersona.invalid"))
        return
    await container.personas.create(user.id, name, instructions, emoji)
    await state.clear()
    await message.answer(t(lang, "cpersona.imported"))


@router.callback_query(F.data.regexp(r"^cps:\d+$"))
async def cb_detail(call: CallbackQuery, user, lang: str) -> None:
    persona = await container.personas.get(_id(call.data), user.id)
    if not persona:
        await call.answer()
        return
    await call.answer()
    text = t(lang, "cpersona.opened", name=f"{persona.emoji} {persona.name}",
             instructions=persona.instructions)
    await safe_edit(call, text, kb.custom_persona_detail_kb(lang, persona))


@router.callback_query(F.data.startswith("cps:default:"))
async def cb_default(call: CallbackQuery, user, lang: str) -> None:
    ok = await container.personas.set_default(_id(call.data), user.id)
    await call.answer(t(lang, "cpersona.default_set") if ok else t(lang, "common.error"))
    personas = await container.personas.list_for_user(user.id)
    await safe_edit(call, t(lang, "cpersona.title"), kb.custom_personas_kb(lang, personas))


@router.callback_query(F.data.startswith("cps:assign:"))
async def cb_assign(call: CallbackQuery, user, lang: str) -> None:
    persona_id = _id(call.data)
    prefs = await get_prefs(user)
    conv = await ensure_conversation(user, prefs)
    ok = await container.conversations.set_persona(conv.id, user.id, persona_id)
    await call.answer(t(lang, "cpersona.assigned") if ok else t(lang, "common.error"))


@router.callback_query(F.data.startswith("cps:edit:"))
async def cb_edit(call: CallbackQuery, user, lang: str, state: FSMContext) -> None:
    persona = await container.personas.get(_id(call.data), user.id)
    if not persona:
        await call.answer()
        return
    await state.set_state(PersonaStudioFlow.edit)
    await state.update_data(persona_id=persona.id)
    await call.answer()
    await safe_edit(call, t(lang, "cpersona.edit_hint"), kb.back_home_kb(lang, "cps:list"))


@router.message(StateFilter(PersonaStudioFlow.edit), F.text)
async def on_edit(message: Message, user, lang: str, state: FSMContext) -> None:
    data = await state.get_data()
    ok = await container.personas.update_instructions(
        data.get("persona_id", 0), user.id, message.text or ""
    )
    await state.clear()
    await message.answer(t(lang, "cpersona.edited") if ok else t(lang, "common.error"))


@router.callback_query(F.data.startswith("cps:del:"))
async def cb_delete(call: CallbackQuery, user, lang: str) -> None:
    ok = await container.personas.delete(_id(call.data), user.id)
    await call.answer(t(lang, "cpersona.deleted") if ok else t(lang, "common.error"))
    personas = await container.personas.list_for_user(user.id)
    await safe_edit(call, t(lang, "cpersona.title"), kb.custom_personas_kb(lang, personas))


@router.callback_query(F.data.startswith("cps:exp:"))
async def cb_export(call: CallbackQuery, user, lang: str) -> None:
    persona = await container.personas.get(_id(call.data), user.id)
    if not persona:
        await call.answer()
        return
    await call.answer()
    payload = json.dumps(
        {"name": persona.name, "instructions": persona.instructions, "emoji": persona.emoji},
        ensure_ascii=False,
        indent=2,
    )
    await call.message.answer(f"{t(lang, 'cpersona.exported')}\n\n<pre>{payload}</pre>",
                              parse_mode="HTML")


def _id(data: str) -> int:
    try:
        return int(data.rsplit(":", 1)[1])
    except (ValueError, IndexError):
        return 0


def _split(text: str, limit: int = 80) -> tuple[str, str] | None:
    if "|" not in text:
        return None
    name, instructions = text.split("|", 1)
    name = name.strip()[:limit]
    instructions = instructions.strip()[:2000]
    if not name or not instructions:
        return None
    return name, instructions
