from __future__ import annotations

import math

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import common as kb
from bot.ui import safe_edit, send_ai, t
from core.container import container
from core.logging import get_logger
from services.ai import AIConfigurationError, AIError, AITimeoutError
from utils.states import PromptFlow

log = get_logger(__name__)
router = Router(name="prompt_studio")
PAGE_SIZE = 5


async def _render(call: CallbackQuery, user, lang: str, page: int = 0, category: str | None = None):
    prompts = await container.prompts.list_for_user(user.id, category)
    total_pages = max(1, math.ceil(len(prompts) / PAGE_SIZE))
    page = max(0, min(page, total_pages - 1))
    window = prompts[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]

    text = t(lang, "prompts.title")
    if category:
        text += f"\n🏷 {category}"
    if not prompts:
        text += f"\n\n{t(lang, 'prompts.empty')}"
    await safe_edit(
        call, text, kb.prompts_kb(lang, window, page, total_pages, category)
    )


@router.callback_query(F.data.startswith("pr:list:"))
async def cb_list(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    try:
        page = int(call.data.rsplit(":", 1)[1])
    except ValueError:
        page = 0
    await _render(call, user, lang, page)


@router.callback_query(F.data == "menu:prompts")
async def cb_open(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    await _render(call, user, lang, 0)


@router.callback_query(F.data == "pr:new")
async def cb_new(call: CallbackQuery, lang: str, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(PromptFlow.new)
    await safe_edit(call, t(lang, "prompts.create_hint"), kb.back_home_kb(lang, "pr:list:0"))


@router.message(StateFilter(PromptFlow.new), F.text)
async def on_new(message: Message, user, lang: str, state: FSMContext) -> None:
    text = message.text or ""
    if "|" not in text:
        await message.answer(t(lang, "prompts.invalid"))
        return
    title, body = text.split("|", 1)
    title, body = title.strip(), body.strip()
    if not title or not body:
        await message.answer(t(lang, "prompts.invalid"))
        return
    await container.prompts.create(user.id, title, body)
    await state.clear()
    await message.answer(t(lang, "prompts.created"))


@router.callback_query(F.data == "pr:cats")
async def cb_categories(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    categories = await container.prompts.categories(user.id)
    await safe_edit(
        call, t(lang, "prompts.categories"), kb.prompt_categories_kb(lang, categories)
    )


@router.callback_query(F.data.startswith("pr:cat:"))
async def cb_filter(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    try:
        index = int(call.data.rsplit(":", 1)[1])
    except ValueError:
        return
    categories = await container.prompts.categories(user.id)
    if not (0 <= index < len(categories)):
        return
    await _render(call, user, lang, 0, categories[index])


@router.callback_query(F.data.regexp(r"^pr:\d+$"))
async def cb_detail(call: CallbackQuery, user, lang: str) -> None:
    prompt = await container.prompts.get(_id(call.data), user.id)
    if not prompt:
        await call.answer()
        return
    await call.answer()
    text = t(lang, "prompts.detail", title=prompt.title, category=prompt.category,
             body=prompt.body[:1500])
    await safe_edit(call, text, kb.prompt_detail_kb(lang, prompt))


@router.callback_query(F.data.startswith("pr:run:"))
async def cb_run(call: CallbackQuery, user, lang: str, state: FSMContext) -> None:
    prompt = await container.prompts.get(_id(call.data), user.id)
    if not prompt:
        await call.answer()
        return
    await state.set_state(PromptFlow.run)
    await state.update_data(prompt_id=prompt.id)
    await call.answer()
    await safe_edit(call, t(lang, "prompts.run_hint"), kb.back_home_kb(lang, "pr:list:0"))


@router.message(StateFilter(PromptFlow.run), F.text)
async def on_run(message: Message, user, lang: str, state: FSMContext) -> None:
    data = await state.get_data()
    prompt = await container.prompts.get(data.get("prompt_id", 0), user.id)
    if not prompt:
        await state.clear()
        await message.answer(t(lang, "common.error"))
        return
    user_input = (message.text or "").strip()
    payload = prompt.body if user_input in {"", "-"} else f"{prompt.body}\n\n---\n{user_input}"
    await state.clear()
    await message.bot.send_chat_action(message.chat.id, "typing")
    try:
        result = await container.tools.custom(user, payload)
    except AIConfigurationError:
        await message.answer(t(lang, "chat.blocked"))
        return
    except AITimeoutError:
        await message.answer(t(lang, "errors.ai_timeout"))
        return
    except AIError as exc:
        await message.answer(t(lang, "errors.ai", detail=str(exc)[:300]))
        return
    except Exception as exc:  # noqa: BLE001
        log.exception("Prompt run failed: %s", exc)
        await message.answer(t(lang, "errors.generic"))
        return
    await send_ai(message, result, kb.tools_kb(lang))


@router.callback_query(F.data.startswith("pr:edit:"))
async def cb_edit(call: CallbackQuery, user, lang: str, state: FSMContext) -> None:
    prompt = await container.prompts.get(_id(call.data), user.id)
    if not prompt:
        await call.answer()
        return
    await state.set_state(PromptFlow.edit)
    await state.update_data(prompt_id=prompt.id)
    await call.answer()
    await safe_edit(call, t(lang, "prompts.edit_hint"), kb.back_home_kb(lang, "pr:list:0"))


@router.message(StateFilter(PromptFlow.edit), F.text)
async def on_edit(message: Message, user, lang: str, state: FSMContext) -> None:
    data = await state.get_data()
    ok = await container.prompts.update_body(
        data.get("prompt_id", 0), user.id, message.text or ""
    )
    await state.clear()
    await message.answer(t(lang, "common.saved") if ok else t(lang, "common.error"))


@router.callback_query(F.data.startswith("pr:del:"))
async def cb_delete(call: CallbackQuery, user, lang: str) -> None:
    ok = await container.prompts.delete(_id(call.data), user.id)
    await call.answer(t(lang, "prompts.deleted") if ok else t(lang, "common.error"))
    await _render(call, user, lang, 0)


@router.callback_query(F.data.startswith("pr:exp:"))
async def cb_export(call: CallbackQuery, user, lang: str) -> None:
    prompt = await container.prompts.get(_id(call.data), user.id)
    if not prompt:
        await call.answer()
        return
    await call.answer()
    await call.message.answer(
        f"{t(lang, 'prompts.exported')}\n\n<b>{prompt.title}</b>\n<pre>{prompt.body[:3000]}</pre>",
        parse_mode="HTML",
    )


def _id(data: str) -> int:
    try:
        return int(data.rsplit(":", 1)[1])
    except (ValueError, IndexError):
        return 0
