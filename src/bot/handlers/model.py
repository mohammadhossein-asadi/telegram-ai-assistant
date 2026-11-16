from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.helpers import get_prefs
from bot.keyboards import common as kb
from bot.ui import safe_edit, t
from bot.views import model_text
from core.container import container

router = Router(name="model")


@router.callback_query(F.data == "menu:model")
async def cb_model(call: CallbackQuery, user, lang: str) -> None:
    await call.answer()
    prefs = await get_prefs(user)
    models = container.registry.models()
    current = prefs.model or container.config.ai_model
    provider = prefs.provider or container.config.ai_provider
    await safe_edit(
        call, model_text(lang, current, provider), kb.model_kb(lang, models, current)
    )


@router.callback_query(F.data.startswith("mdl:"))
async def cb_set_model(call: CallbackQuery, user, lang: str) -> None:
    try:
        index = int(call.data.split(":", 1)[1])
    except ValueError:
        await call.answer()
        return
    models = container.registry.models()
    if 0 <= index < len(models):
        provider, model = models[index]
        await container.user_settings.update(user.id, model=model, provider=provider)
        await call.answer(t(lang, "common.saved"))
    else:
        await call.answer()
    prefs = await get_prefs(user)
    current = prefs.model or container.config.ai_model
    await safe_edit(
        call,
        model_text(lang, current, prefs.provider or container.config.ai_provider),
        kb.model_kb(lang, container.registry.models(), current),
    )
