from __future__ import annotations

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from core.logging import get_logger
from localization import loc
from utils.text import markdown_to_telegram_html, split_message

log = get_logger(__name__)


def t(lang: str, key: str, **kwargs) -> str:
    return loc.t(lang, key, **kwargs)


async def safe_edit(
    call: CallbackQuery,
    text: str,
    keyboard: InlineKeyboardMarkup | None = None,
    *,
    parse_mode: str = "HTML",
) -> None:
    """Edit the menu message, ignoring harmless 'message is not modified' errors."""
    message = call.message
    if message is None:
        return
    try:
        await message.edit_text(text, reply_markup=keyboard, parse_mode=parse_mode)
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc):
            return
        log.debug("edit_text failed, retrying as plain text: %s", exc)
        try:
            await message.edit_text(text, reply_markup=keyboard)
        except TelegramBadRequest as inner:
            log.warning("edit_text fallback failed: %s", inner)


async def answer_ai(call: CallbackQuery, text: str, keyboard: InlineKeyboardMarkup | None = None) -> None:
    """Send model output as safe HTML, splitting long answers."""
    chunks = split_message(text, 3500)
    if not chunks:
        chunks = [t("en", "common.empty")]
    for index, chunk in enumerate(chunks):
        html = markdown_to_telegram_html(chunk)
        kb = keyboard if index == len(chunks) - 1 else None
        try:
            await call.message.answer(html, reply_markup=kb, parse_mode="HTML")
        except TelegramBadRequest:
            await call.message.answer(chunk, reply_markup=kb)


async def send_ai(message: Message, text: str, keyboard: InlineKeyboardMarkup | None = None) -> None:
    chunks = split_message(text, 3500)
    if not chunks:
        chunks = ["…"]
    for index, chunk in enumerate(chunks):
        html = markdown_to_telegram_html(chunk)
        kb = keyboard if index == len(chunks) - 1 else None
        try:
            await message.answer(html, reply_markup=kb, parse_mode="HTML")
        except TelegramBadRequest:
            await message.answer(chunk, reply_markup=kb)
