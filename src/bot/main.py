from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import ROUTERS
from bot.middlewares.user import UserMiddleware
from core.config import Settings, get_settings
from core.container import container
from core.logging import get_logger, setup_logging
from database import Database, run_migrations
from database.repositories import (
    ConversationRepository,
    MemoryRepository,
    MessageRepository,
    PersonaRepository,
    PromptRepository,
    ProviderRepository,
    SettingsRepository,
    UsageRepository,
    UserRepository,
)
from services.ai import ModelRouter, ProviderRegistry
from services.chat import ChatEngine
from services.github import GitHubClient
from services.memory import MemoryService
from services.tools import ToolService

log = get_logger(__name__)


async def bootstrap(settings: Settings) -> None:
    """Construct the service graph and prepare the database."""
    db = Database(settings.database_url)
    await run_migrations(db)

    container.config = settings
    container.db = db
    container.users = UserRepository(db)
    container.user_settings = SettingsRepository(db)
    container.conversations = ConversationRepository(db)
    container.messages = MessageRepository(db)
    container.memory_repo = MemoryRepository(db)
    container.personas = PersonaRepository(db)
    container.prompts = PromptRepository(db)
    container.providers = ProviderRepository(db)
    container.usage = UsageRepository(
        db,
        max_daily_requests=settings.max_daily_requests,
        rate_limit=settings.user_rate_limit,
    )

    container.registry = ProviderRegistry(settings, container.providers)
    await container.registry.refresh()
    container.router = ModelRouter(container.registry)
    container.github = GitHubClient(
        username=settings.github_username,
        token=settings.github_token,
        ttl=settings.github_cache_ttl,
    )

    container.chat_engine = ChatEngine(
        settings,
        container.registry,
        container.conversations,
        container.messages,
        container.user_settings,
        container.memory_repo,
        container.usage,
        personas=container.personas,
        router=container.router,
    )
    container.memory = MemoryService(container.memory_repo)
    container.tools = ToolService(container.chat_engine, container.registry, settings)
    container.mark_ready()
    log.info("Services ready (language default: %s)", settings.default_language)


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    middleware = UserMiddleware()
    dp.message.outer_middleware(middleware)
    dp.callback_query.outer_middleware(middleware)
    for router in ROUTERS:
        dp.include_router(router)
    return dp


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)

    for problem in settings.validate_runtime():
        log.warning("CONFIG: %s", problem)

    if not settings.bot_token or settings.bot_token.upper() == "TOKEN":
        raise SystemExit(
            "BOT_TOKEN is not configured. Copy .env.example to .env and set BOT_TOKEN."
        )

    await bootstrap(settings)

    bot = Bot(settings.bot_token)
    dp = build_dispatcher()
    log.info("Starting polling…")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await container.db.dispose()
        log.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
