"""Shared handler helpers: preference loading and conversation bootstrap."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup

from bot import views
from bot.keyboards import common as kb
from core.container import container
from database.models import Conversation, User, UserSettings


async def get_prefs(user: User) -> UserSettings:
    return await container.user_settings.get_or_create(user.id)


async def ensure_conversation(user: User, prefs: UserSettings | None = None) -> Conversation:
    """Return the user's active conversation, creating one when needed."""
    prefs = prefs or await get_prefs(user)

    if prefs.current_conversation_id:
        conv = await container.conversations.get(prefs.current_conversation_id, user.id)
        if conv and not conv.is_archived:
            return conv

    conversations = await container.conversations.list_for_user(user.id)
    if conversations:
        conv = conversations[0]
    else:
        conv = await container.conversations.create(user.id, title="New chat")

    await container.user_settings.update(user.id, current_conversation_id=conv.id)
    prefs.current_conversation_id = conv.id
    return conv


async def current_model(user: User, prefs: UserSettings | None = None) -> str:
    prefs = prefs or await get_prefs(user)
    return prefs.model or container.config.ai_model


async def build_main_menu(user: User, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    prefs = await get_prefs(user)
    conv = await ensure_conversation(user, prefs)
    model = prefs.model or container.config.ai_model
    text = views.main_menu_text(lang, prefs, conv.title, model)
    return text, kb.main_menu(lang)
