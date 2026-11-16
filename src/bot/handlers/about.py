from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards import common as kb
from bot.ui import safe_edit, t
from bot.views import about_text, bot_info_text, developer_text
from core.container import container

router = Router(name="about")


@router.callback_query(F.data == "menu:about")
async def cb_about(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    await safe_edit(call, about_text(lang), kb.about_kb(lang))


@router.callback_query(F.data == "ab:dev")
async def cb_developer(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    cfg = container.config
    text = developer_text(lang, cfg.developer_name, cfg.developer_role, cfg.developer_github)
    rows = [
        [InlineKeyboardButton(text=t(lang, "about.github"), url=cfg.developer_github)],
        [InlineKeyboardButton(text=t(lang, "about.about_bot"), callback_data="ab:bot")],
    ]
    rows += kb.back_home(lang, "menu:about")
    await safe_edit(call, text, InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data == "ab:bot")
async def cb_bot(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    cfg = container.config
    text = bot_info_text(lang, cfg.bot_version, lang.upper(), cfg.ai_model)
    await safe_edit(call, f"{text}\n\n{t(lang, 'about.credits')}", kb.back_home_kb(lang, "menu:about"))


@router.callback_query(F.data == "ab:support")
async def cb_support(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    text = f"{t(lang, 'about.developer', name=container.config.developer_name, role=container.config.developer_role, github=container.config.developer_github)}"
    rows = [
        [InlineKeyboardButton(text=t(lang, "about.github"), url=container.config.developer_github)],
    ]
    rows += kb.back_home(lang, "menu:about")
    await safe_edit(call, text, InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data == "menu:profile")
async def cb_profile(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    await cb_developer(call, lang)
