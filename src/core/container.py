"""Application-wide service container."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.config import Settings
    from database.base import Database
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


class Container:
    config: "Settings"
    db: "Database"
    users: "UserRepository"
    user_settings: "SettingsRepository"
    conversations: "ConversationRepository"
    messages: "MessageRepository"
    memory_repo: "MemoryRepository"
    personas: "PersonaRepository"
    prompts: "PromptRepository"
    providers: "ProviderRepository"
    usage: "UsageRepository"
    registry: "ProviderRegistry"
    router: "ModelRouter"
    chat_engine: "ChatEngine"
    memory: "MemoryService"
    tools: "ToolService"
    github: "GitHubClient"

    def __init__(self) -> None:
        self._ready = False

    def mark_ready(self) -> None:
        self._ready = True

    @property
    def ready(self) -> bool:
        return self._ready


container = Container()