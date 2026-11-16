from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import common as kb
from bot.ui import safe_edit, t
from core.container import container
from core.logging import get_logger
from utils.states import AdminFlow

log = get_logger(__name__)
router = Router(name="admin")


async def _stats_text(lang: str) -> str:
    users = await container.users.count()
    blocked = await container.users.count_blocked()
    convs = await container.conversations.count()
    messages = await container.messages.count()
    requests = await container.usage.count_total()
    active = await container.users.count_active_since(24)
    prompt_tokens, completion_tokens = await container.usage.token_totals()
    base = t(
        lang,
        "admin.stats_body",
        users=users,
        blocked=blocked,
        convs=convs,
        messages=messages,
        requests=requests,
        active=active,
    )
    return base + "\n" + t(
        lang, "admin.tokens", prompt=prompt_tokens, completion=completion_tokens
    )


@router.message(Command("admin"))
async def cmd_admin(message: Message, lang: str, is_admin: bool) -> None:
    if not is_admin:
        await message.answer(t(lang, "common.not_admin"))
        return
    await message.answer(t(lang, "admin.title"), reply_markup=kb.admin_kb(lang))


@router.message(Command("block"))
async def cmd_block(message: Message, lang: str, is_admin: bool) -> None:
    if not is_admin:
        return
    target = _id_from_command(message.text)
    if not target:
        await message.answer("Usage: /block <telegram_id>")
        return
    user = await container.users.get_by_telegram_id(target)
    if not user:
        await message.answer(t(lang, "common.unknown"))
        return
    await container.users.set_blocked(user.id, True)
    await message.answer(t(lang, "common.saved"))


@router.message(Command("unblock"))
async def cmd_unblock(message: Message, lang: str, is_admin: bool) -> None:
    if not is_admin:
        return
    target = _id_from_command(message.text)
    if not target:
        await message.answer("Usage: /unblock <telegram_id>")
        return
    user = await container.users.get_by_telegram_id(target)
    if not user:
        await message.answer(t(lang, "common.unknown"))
        return
    await container.users.set_blocked(user.id, False)
    await message.answer(t(lang, "common.saved"))


@router.callback_query(F.data == "adm:home")
async def cb_home(call: CallbackQuery, lang: str, is_admin: bool) -> None:
    if not is_admin:
        await call.answer(t(lang, "common.not_admin"), show_alert=True)
        return
    await call.answer()
    await safe_edit(call, t(lang, "admin.title"), kb.admin_kb(lang))


@router.callback_query(F.data == "adm:stats")
async def cb_stats(call: CallbackQuery, lang: str, is_admin: bool) -> None:
    if not is_admin:
        await call.answer(t(lang, "common.not_admin"), show_alert=True)
        return
    await call.answer()
    await safe_edit(call, await _stats_text(lang), kb.back_home_kb(lang, "adm:home"))


@router.callback_query(F.data == "adm:limits")
async def cb_limits(call: CallbackQuery, lang: str, is_admin: bool) -> None:
    if not is_admin:
        await call.answer(t(lang, "common.not_admin"), show_alert=True)
        return
    await call.answer()
    text = t(
        lang,
        "admin.limits_body",
        rate=container.config.user_rate_limit,
        daily=container.config.max_daily_requests,
    )
    await safe_edit(call, text, kb.back_home_kb(lang, "adm:home"))


@router.callback_query(F.data == "adm:health")
async def cb_health(call: CallbackQuery, lang: str, is_admin: bool) -> None:
    if not is_admin:
        await call.answer(t(lang, "common.not_admin"), show_alert=True)
        return
    await call.answer()
    lines = [f"<b>{t(lang, 'admin.health')}</b>", ""]
    for name, model, ok, detail in await container.registry.health():
        status = t(lang, "admin.health_ok") if ok else t(lang, "admin.health_fail", detail=detail)
        lines.append(t(lang, "admin.health_line", name=name, model=model, status=status))
    await safe_edit(call, "\n".join(lines), kb.back_home_kb(lang, "adm:home"))


@router.callback_query(F.data == "adm:broadcast")
async def cb_broadcast(call: CallbackQuery, lang: str, is_admin: bool, state: FSMContext) -> None:
    if not is_admin:
        await call.answer(t(lang, "common.not_admin"), show_alert=True)
        return
    await call.answer()
    await state.set_state(AdminFlow.broadcast)
    await safe_edit(call, t(lang, "admin.broadcast_ask"), kb.back_home_kb(lang, "adm:home"))


@router.message(StateFilter(AdminFlow.broadcast), F.text)
async def on_broadcast(message: Message, lang: str, is_admin: bool, state: FSMContext) -> None:
    if not is_admin:
        return
    await state.clear()
    sent = 0
    for telegram_id in await container.users.all_ids():
        try:
            await message.bot.send_message(telegram_id, message.text)
            sent += 1
        except Exception:  # noqa: BLE001 - per-recipient failures are expected
            continue
        await asyncio.sleep(0.05)
    await message.answer(t(lang, "admin.broadcast_done", count=sent))


@router.callback_query(F.data == "adm:providers")
async def cb_providers(call: CallbackQuery, lang: str, is_admin: bool) -> None:
    if not is_admin:
        await call.answer(t(lang, "common.not_admin"), show_alert=True)
        return
    await call.answer()
    providers = await container.providers.list_active()
    text = t(lang, "admin.providers")
    if not providers:
        text += f"\n\n{t(lang, 'admin.no_providers')}"
    await safe_edit(call, text, kb.providers_kb(lang, providers))


@router.callback_query(F.data == "adm:addprov")
async def cb_add_provider(call: CallbackQuery, lang: str, is_admin: bool, state: FSMContext) -> None:
    if not is_admin:
        await call.answer(t(lang, "common.not_admin"), show_alert=True)
        return
    await call.answer()
    await state.set_state(AdminFlow.add_provider)
    await safe_edit(call, t(lang, "admin.add_provider_hint"), kb.back_home_kb(lang, "adm:providers"))


@router.message(StateFilter(AdminFlow.add_provider), F.text)
async def on_add_provider(message: Message, lang: str, is_admin: bool, state: FSMContext) -> None:
    if not is_admin:
        return
    parts = [part.strip() for part in (message.text or "").split("|")]
    if len(parts) not in (4, 5) or not all(parts[:3]):
        await message.answer(t(lang, "admin.capabilities_hint"))
        return
    name, base_url, model, api_key = parts[:4]
    capabilities = parts[4] if len(parts) == 5 else ""
    provider = await container.providers.add(name, base_url, model, api_key)
    if capabilities:
        await container.providers.set_capabilities(provider.id, capabilities)
    await container.registry.refresh()
    await state.clear()
    await message.answer(t(lang, "admin.provider_added"))


@router.callback_query(F.data.startswith("adm:delprov:"))
async def cb_del_provider(call: CallbackQuery, lang: str, is_admin: bool) -> None:
    if not is_admin:
        await call.answer(t(lang, "common.not_admin"), show_alert=True)
        return
    provider_id = _id_from_data(call.data)
    ok = await container.providers.delete(provider_id)
    await container.registry.refresh()
    await call.answer(t(lang, "admin.provider_deleted") if ok else t(lang, "common.error"))
    providers = await container.providers.list_active()
    text = t(lang, "admin.providers")
    if not providers:
        text += f"\n\n{t(lang, 'admin.no_providers')}"
    await safe_edit(call, text, kb.providers_kb(lang, providers))


def _id_from_data(data: str) -> int:
    try:
        return int(data.rsplit(":", 1)[1])
    except (ValueError, IndexError):
        return 0


def _id_from_command(text: str | None) -> int:
    parts = (text or "").split()
    if len(parts) < 2 or not parts[1].lstrip("-").isdigit():
        return 0
    return int(parts[1])
