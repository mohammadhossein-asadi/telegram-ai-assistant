from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from core.container import container
from localization import loc


class UserMiddleware(BaseMiddleware):
    """Resolves (or creates) the DB user and injects it into handler data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = data.get("event_from_user")
        if tg_user is None:
            return await handler(event, data)

        user, created = await container.users.get_or_create(
            tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            language=container.config.default_language,
        )
        data["user"] = user
        data["lang"] = user.language
        data["is_admin"] = container.config.is_admin(tg_user.id)
        data["new_user"] = created

        if user.is_blocked:
            text = loc.t(user.language, "start.blocked")
            if isinstance(event, CallbackQuery):
                await event.answer(text, show_alert=True)
            elif isinstance(event, Message):
                await event.answer(text)
            return None

        return await handler(event, data)
