from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.helpers import build_main_menu
from bot.keyboards import common as kb
from bot.ui import safe_edit, t
from bot.views import about_text, user_display_name
from core.container import container
from localization import loc
from utils.states import Onboarding

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, user, lang: str, new_user: bool, state: FSMContext) -> None:
    await state.clear()

    if new_user:
        await state.set_state(Onboarding.language)
        await message.answer(t(lang, "start.onboarding"), reply_markup=kb.language_kb(lang))
        return

    text, keyboard = await build_main_menu(user, lang)
    greeting = t(lang, "start.welcome_back", name=user_display_name(user))
    await message.answer(f"{greeting}\n\n{text}", reply_markup=keyboard, parse_mode="HTML")


@router.message(Command("menu"))
async def cmd_menu(message: Message, user, lang: str, state: FSMContext) -> None:
    await state.clear()
    text, keyboard = await build_main_menu(user, lang)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message, lang: str) -> None:
    await message.answer(about_text(lang), reply_markup=kb.about_kb(lang), parse_mode="HTML")


@router.message(Command("lang"))
async def cmd_lang(message: Message, lang: str) -> None:
    await message.answer(t(lang, "settings.language"), reply_markup=kb.language_kb(lang))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, user, lang: str, state: FSMContext) -> None:
    await state.clear()
    text, keyboard = await build_main_menu(user, lang)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "home")
async def cb_home(call: CallbackQuery, user, lang: str, state: FSMContext) -> None:
    await state.clear()
    await call.answer()
    text, keyboard = await build_main_menu(user, lang)
    await safe_edit(call, text, keyboard)


@router.callback_query(F.data.startswith("lang:"))
async def cb_language(call: CallbackQuery, user, state: FSMContext) -> None:
    code = call.data.split(":", 1)[1]
    if not loc.has_language(code):
        await call.answer()
        return

    await container.users.update_language(user.id, code)
    user.language = code
    current_state = await state.get_state()
    await state.clear()

    await call.answer(t(code, "start.lang_set"))
    text, keyboard = await build_main_menu(user, code)

    if current_state == Onboarding.language.state:
        greeting = t(code, "start.welcome", name=user_display_name(user))
        credit = ""
        if container.config.bot_branding_enabled:
            credit = "\n\n" + t(code, "start.dev_credit", developer=container.config.developer_name)
        await safe_edit(call, f"{greeting}\n\n{text}{credit}", keyboard)
    else:
        await safe_edit(call, text, keyboard)


@router.callback_query(F.data == "noop")
async def cb_noop(call: CallbackQuery) -> None:
    await call.answer()
