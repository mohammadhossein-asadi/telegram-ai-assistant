from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.helpers import ensure_conversation, get_prefs
from bot.keyboards import common as kb
from bot.ui import safe_edit, t
from core.container import container
from core.logging import get_logger
from services.ai import AIError
from utils.states import ConversationFlow

log = get_logger(__name__)

router = Router(name="conversations")
PAGE_SIZE = 5


async def _render_list(call: CallbackQuery, user, lang: str, page: int = 0) -> None:
    conversations = await container.conversations.list_for_user(user.id)
    total = max(1, (len(conversations) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, total - 1))
    window = conversations[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]
    text = t(lang, "convs.title")
    if not conversations:
        text = f"{text}\n\n{t(lang, 'convs.empty')}"
    await safe_edit(call, text, kb.conversations_kb(lang, window, page, total))


@router.callback_query(F.data == "menu:convs")
async def cb_list(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    await _render_list(call, user, lang, 0)


@router.callback_query(F.data.startswith("conv:list:"))
async def cb_page(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    try:
        page = int(call.data.rsplit(":", 1)[1])
    except ValueError:
        page = 0
    await _render_list(call, user, lang, page)


@router.callback_query(F.data == "conv:new")
async def cb_new(call: CallbackQuery, user, lang: str) -> None:
    conv = await container.conversations.create(user.id, title="New chat")
    await container.user_settings.update(user.id, current_conversation_id=conv.id)
    await call.answer(t(lang, "chat.new_chat"))
    await safe_edit(call, t(lang, "start.new_chat_started"), kb.chat_kb(lang))


@router.callback_query(F.data.startswith("conv:open:"))
async def cb_open(call: CallbackQuery, user, lang: str) -> None:
    conv_id = _id(call.data)
    conv = await container.conversations.get(conv_id, user.id)
    if not conv:
        await call.answer()
        return
    await container.user_settings.update(user.id, current_conversation_id=conv.id)
    await call.answer(t(lang, "convs.switched", title=conv.title))
    text = t(lang, "chat.hint", title=conv.title)
    if conv.summary:
        text += f"\n\n🧾 {conv.summary[:400]}"
    await safe_edit(call, text, kb.open_conversation_kb(lang, conv.id))


@router.callback_query(F.data.startswith("conv:pin:"))
async def cb_pin(call: CallbackQuery, user, lang: str) -> None:
    conv = await container.conversations.get(_id(call.data), user.id)
    if not conv:
        await call.answer()
        return
    will_pin = not conv.is_pinned
    ok = await container.conversations.set_pinned(conv.id, user.id, will_pin)
    if ok:
        await call.answer(t(lang, "convs.pin" if will_pin else "convs.unpin"))
    else:
        await call.answer(t(lang, "common.error"))
    await _render_list(call, user, lang, 0)


@router.callback_query(F.data == "conv:search")
async def cb_search(call: CallbackQuery, lang: str, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(ConversationFlow.search)
    await safe_edit(call, t(lang, "convs.search_hint"), kb.back_home_kb(lang, "menu:convs"))


@router.message(StateFilter(ConversationFlow.search), F.text)
async def on_search(message: Message, user, lang: str, state: FSMContext) -> None:
    query = (message.text or "").strip()
    await state.clear()
    results = await container.conversations.search(user.id, query)
    text = t(lang, "convs.search_results", query=query)
    if not results:
        text += f"\n\n{t(lang, 'convs.empty')}"
    await message.answer(text, reply_markup=kb.conversations_kb(lang, results, 0, 1))


@router.callback_query(F.data.startswith("conv:exp:"))
async def cb_export(call: CallbackQuery, user, lang: str) -> None:
    conv = await container.conversations.get(_id(call.data), user.id)
    if not conv:
        await call.answer()
        return
    await call.answer()
    history = await container.messages.all_for_conversation(conv.id)
    lines = [f"# {conv.title}", f"# exported from {container.config.bot_name_en}", ""]
    for msg in history:
        lines.append(f"[{msg.role}] {msg.content}")
        lines.append("")
    payload = "\n".join(lines).encode("utf-8")
    await call.message.answer_document(
        BufferedInputFile(payload, filename=f"conversation-{conv.id}.txt"),
        caption=t(lang, "convs.exported"),
    )


@router.callback_query(F.data.startswith("conv:sum:"))
async def cb_summary(call: CallbackQuery, user, lang: str) -> None:
    conv = await container.conversations.get(_id(call.data), user.id)
    if not conv:
        await call.answer()
        return
    await call.answer(t(lang, "convs.summarizing"))
    try:
        summary = await container.chat_engine.summarize_conversation(user, conv)
    except ValueError:
        await call.message.answer(t(lang, "chat.empty"))
        return
    except AIError as exc:
        await call.message.answer(t(lang, "errors.ai", detail=str(exc)[:300]))
        return
    except Exception as exc:  # noqa: BLE001
        log.exception("Summary failed: %s", exc)
        await call.message.answer(t(lang, "errors.generic"))
        return
    await call.message.answer(f"🧾 {summary}")


@router.callback_query(F.data.startswith("conv:rn:"))
async def cb_rename(call: CallbackQuery, user, lang: str, state: FSMContext) -> None:
    conv_id = _id(call.data)
    conv = await container.conversations.get(conv_id, user.id)
    if not conv:
        await call.answer()
        return
    await state.set_state(ConversationFlow.rename)
    await state.update_data(conv_id=conv_id)
    await call.answer()
    await safe_edit(call, t(lang, "convs.ask_name"), kb.back_home_kb(lang, "menu:convs"))


@router.message(StateFilter(ConversationFlow.rename), F.text)
async def on_rename(message: Message, user, lang: str, state: FSMContext) -> None:
    data = await state.get_data()
    await container.conversations.rename(data.get("conv_id", 0), user.id, message.text)
    await state.clear()
    await message.answer(t(lang, "convs.renamed"), reply_markup=kb.back_home_kb(lang, "menu:convs"))


@router.callback_query(F.data.startswith("conv:arch:"))
async def cb_archive(call: CallbackQuery, user, lang: str) -> None:
    conv_id = _id(call.data)
    ok = await container.conversations.set_archived(conv_id, user.id, True)
    prefs = await get_prefs(user)
    if ok and prefs.current_conversation_id == conv_id:
        await container.user_settings.update(user.id, current_conversation_id=None)
    await call.answer(t(lang, "convs.archived") if ok else t(lang, "common.error"))
    await _render_list(call, user, lang, 0)


@router.callback_query(F.data.startswith("conv:unarch:"))
async def cb_unarchive(call: CallbackQuery, user, lang: str) -> None:
    ok = await container.conversations.set_archived(_id(call.data), user.id, False)
    await call.answer(t(lang, "convs.unarchived") if ok else t(lang, "common.error"))
    await _render_list(call, user, lang, 0)


@router.callback_query(F.data.startswith("conv:del:"))
async def cb_delete(call: CallbackQuery, user, lang: str) -> None:
    conv = await container.conversations.get(_id(call.data), user.id)
    if not conv:
        await call.answer()
        return
    await call.answer()
    await safe_edit(
        call,
        t(lang, "convs.confirm_delete", title=conv.title),
        kb.confirm_kb(lang, f"conv:delok:{conv.id}", "menu:convs"),
    )


@router.callback_query(F.data.startswith("conv:delok:"))
async def cb_delete_confirm(call: CallbackQuery, user, lang: str) -> None:
    conv_id = _id(call.data)
    ok = await container.conversations.delete(conv_id, user.id)
    prefs = await get_prefs(user)
    if ok and prefs.current_conversation_id == conv_id:
        await container.user_settings.update(user.id, current_conversation_id=None)
    await call.answer(t(lang, "convs.deleted") if ok else t(lang, "common.error"))
    await _render_list(call, user, lang, 0)


def _id(data: str) -> int:
    try:
        return int(data.rsplit(":", 1)[1])
    except (ValueError, IndexError):
        return 0
