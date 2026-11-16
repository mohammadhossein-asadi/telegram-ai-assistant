from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import common as kb
from bot.ui import safe_edit, send_ai, t
from core.container import container
from core.logging import get_logger
from services.ai import AIConfigurationError, AIError, AITimeoutError
from utils.states import ToolFlow

log = get_logger(__name__)
router = Router(name="tools")


@router.callback_query(F.data == "menu:tools")
async def cb_tools(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    await safe_edit(call, t(lang, "tools.title"), kb.tools_kb(lang))


@router.callback_query(F.data == "tools:summarize")
async def cb_summarize(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    await safe_edit(call, t(lang, "tools.sum_mode"), kb.summary_modes_kb(lang))


@router.callback_query(F.data == "tools:translate")
async def cb_translate(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    await safe_edit(call, t(lang, "tools.trans_target"), kb.translate_kb(lang))


@router.callback_query(F.data == "tools:write")
async def cb_write(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    await safe_edit(call, t(lang, "tools.write_mode"), kb.write_modes_kb(lang))


@router.callback_query(F.data == "tools:explain")
async def cb_explain(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    await safe_edit(call, t(lang, "tools.explain_mode"), kb.explain_modes_kb(lang))


@router.callback_query(F.data == "tools:coding")
async def cb_coding(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    await safe_edit(call, t(lang, "coding.mode"), kb.coding_kb(lang))


@router.callback_query(F.data.startswith("tc:"))
async def cb_coding_mode(call: CallbackQuery, lang: str, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(ToolFlow.coding)
    await state.update_data(mode=call.data.split(":", 1)[1])
    await safe_edit(call, t(lang, "tools.input_hint"), kb.back_home_kb(lang, "menu:tools"))


@router.callback_query(F.data == "tools:custom")
async def cb_custom(call: CallbackQuery, lang: str, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(ToolFlow.custom)
    await safe_edit(call, t(lang, "tools.custom_hint"), kb.back_home_kb(lang, "menu:tools"))


@router.callback_query(F.data.startswith("ts:"))
async def cb_summary_mode(call: CallbackQuery, lang: str, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(ToolFlow.summarize)
    await state.update_data(mode=call.data.split(":", 1)[1])
    await safe_edit(call, t(lang, "tools.input_hint"), kb.back_home_kb(lang, "menu:tools"))


@router.callback_query(F.data.startswith("tt:"))
async def cb_translate_target(call: CallbackQuery, lang: str, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(ToolFlow.translate)
    await state.update_data(target=call.data.split(":", 1)[1])
    await safe_edit(call, t(lang, "tools.input_hint"), kb.back_home_kb(lang, "menu:tools"))


@router.callback_query(F.data.startswith("tw:"))
async def cb_write_mode(call: CallbackQuery, lang: str, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(ToolFlow.write)
    await state.update_data(mode=call.data.split(":", 1)[1])
    await safe_edit(call, t(lang, "tools.input_hint"), kb.back_home_kb(lang, "menu:tools"))


@router.callback_query(F.data.startswith("te:"))
async def cb_explain_mode(call: CallbackQuery, lang: str, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(ToolFlow.explain)
    await state.update_data(mode=call.data.split(":", 1)[1])
    await safe_edit(call, t(lang, "tools.input_hint"), kb.back_home_kb(lang, "menu:tools"))


async def _run(message: Message, user, lang: str, state: FSMContext, runner) -> None:
    text = (message.text or "").strip()
    if not text:
        return
    await message.bot.send_chat_action(message.chat.id, "typing")
    try:
        result = await runner(text)
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
        log.exception("Tool failure: %s", exc)
        await message.answer(t(lang, "errors.generic"))
        return
    await state.clear()
    await send_ai(message, result, kb.tools_kb(lang))


@router.message(StateFilter(ToolFlow.summarize), F.text)
async def on_summarize(message: Message, user, lang: str, state: FSMContext) -> None:
    data = await state.get_data()
    mode = data.get("mode", "short")
    await _run(message, user, lang, state, lambda text: container.tools.summarize(user, text, mode))


@router.message(StateFilter(ToolFlow.translate), F.text)
async def on_translate(message: Message, user, lang: str, state: FSMContext) -> None:
    data = await state.get_data()
    target = data.get("target", "auto")
    await _run(message, user, lang, state, lambda text: container.tools.translate(user, text, target))


@router.message(StateFilter(ToolFlow.write), F.text)
async def on_write(message: Message, user, lang: str, state: FSMContext) -> None:
    data = await state.get_data()
    mode = data.get("mode", "improve")
    await _run(message, user, lang, state, lambda text: container.tools.write(user, text, mode))


@router.message(StateFilter(ToolFlow.explain), F.text)
async def on_explain(message: Message, user, lang: str, state: FSMContext) -> None:
    data = await state.get_data()
    mode = data.get("mode", "simple")
    await _run(message, user, lang, state, lambda text: container.tools.explain(user, text, mode))


@router.message(StateFilter(ToolFlow.coding), F.text)
async def on_coding(message: Message, user, lang: str, state: FSMContext) -> None:
    data = await state.get_data()
    mode = data.get("mode", "explain")
    await _run(message, user, lang, state, lambda text: container.tools.coding(user, text, mode))


@router.message(StateFilter(ToolFlow.custom), F.text)
async def on_custom(message: Message, user, lang: str, state: FSMContext) -> None:
    await _run(message, user, lang, state, lambda text: container.tools.custom(user, text))
