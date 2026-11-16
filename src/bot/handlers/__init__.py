from __future__ import annotations

from bot.handlers import (
    admin,
    about,
    chat,
    conversations,
    custom_personas,
    developer,
    memory,
    model,
    personality,
    prompt_studio,
    settings,
    start,
    tools,
)

# Order matters: specific callback routers run before the generic chat fallback.
ROUTERS = [
    start.router,
    personality.router,
    custom_personas.router,
    memory.router,
    model.router,
    tools.router,
    prompt_studio.router,
    conversations.router,
    settings.router,
    developer.router,
    about.router,
    admin.router,
    chat.router,
]

__all__ = ["ROUTERS"]
