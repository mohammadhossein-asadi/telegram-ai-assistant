from __future__ import annotations

import time
from typing import TYPE_CHECKING

from core.config import Settings
from core.logging import get_logger
from database.models import Conversation, User
from database.repositories import (
    ConversationRepository,
    MemoryRepository,
    MessageRepository,
    SettingsRepository,
    UsageRepository,
)
from services.ai import AIMessage, AIResponse, ProviderRegistry
from services.chat.prompts import build_system_prompt, temperature_for
from utils.text import detect_language

if TYPE_CHECKING:  # pragma: no cover
    from database.repositories import PersonaRepository
    from services.ai.router import ModelRouter

log = get_logger(__name__)


class ChatEngine:
    """Builds context, selects a model, calls the provider and persists turns."""

    def __init__(
        self,
        settings: Settings,
        registry: ProviderRegistry,
        conversations: ConversationRepository,
        messages: MessageRepository,
        user_settings: SettingsRepository,
        memory: MemoryRepository,
        usage: UsageRepository,
        personas: "PersonaRepository | None" = None,
        router: "ModelRouter | None" = None,
    ) -> None:
        self.settings = settings
        self.registry = registry
        self.conversations = conversations
        self.messages = messages
        self.user_settings = user_settings
        self.memory = memory
        self.usage = usage
        self.personas = personas
        self.router = router

    async def _resolve_model(self, prefs, conversation: Conversation, text: str):
        """Conversation override > auto-routing > user choice."""
        if conversation.model:
            found = self.registry.find_by_model(conversation.model)
            if found:
                return found[0], found[1]
            return self.registry.resolve(conversation.model)
        if prefs.auto_routing and self.router is not None:
            provider, model, task = self.router.choose(text)
            log.debug("Auto-routed task '%s' to %s/%s", task, provider.name, model)
            return provider, model
        return self.registry.resolve(prefs.model)

    async def _persona_instructions(self, user: User, conversation: Conversation) -> str | None:
        if not conversation.persona_id or self.personas is None:
            return None
        persona = await self.personas.get(conversation.persona_id, user.id)
        return persona.instructions if persona else None

    async def respond(
        self,
        user: User,
        conversation: Conversation,
        user_text: str,
    ) -> AIResponse:
        prefs = await self.user_settings.get_or_create(user.id)
        memories = await self.memory.list_for_user(user.id) if prefs.memory_enabled else []
        detected = detect_language(user_text)
        persona_instructions = await self._persona_instructions(user, conversation)

        system_prompt = build_system_prompt(
            prefs,
            ui_language=user.language,
            memories=memories,
            detected_language=detected,
            persona_instructions=persona_instructions,
        )
        if conversation.summary:
            system_prompt += f"\n\nEarlier conversation summary:\n{conversation.summary}"

        context: list[AIMessage] = [AIMessage("system", system_prompt)]
        if prefs.memory_enabled:
            history = await self.messages.recent(
                conversation.id, self.settings.max_context_messages
            )
            for msg in history:
                context.append(AIMessage(msg.role, msg.content))
        context.append(AIMessage("user", user_text))

        provider, model = await self._resolve_model(prefs, conversation, user_text)
        started = time.monotonic()
        try:
            response = await provider.chat(
                context,
                model=model,
                temperature=temperature_for(prefs.creativity),
            )
        except Exception as exc:
            await self.usage.log(
                user.id,
                action="chat",
                provider=provider.name,
                model=model or provider.model,
                success=False,
                error=str(exc),
                latency_ms=int((time.monotonic() - started) * 1000),
            )
            raise

        await self.messages.add(conversation.id, "user", user_text)
        await self.messages.add(conversation.id, "assistant", response.text)
        await self.conversations.touch(conversation.id)
        await self.usage.log(
            user.id,
            action="chat",
            provider=provider.name,
            model=response.model,
            latency_ms=int((time.monotonic() - started) * 1000),
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
        )
        return response

    async def regenerate(
        self, user: User, conversation: Conversation, user_text: str
    ) -> AIResponse:
        """Drop the previous assistant reply and answer the same turn again."""
        await self.messages.delete_last_assistant(conversation.id)
        return await self.respond(user, conversation, user_text)

    async def summarize_conversation(self, user: User, conversation: Conversation) -> str:
        """Produce (and persist) a short summary of a conversation."""
        history = await self.messages.all_for_conversation(conversation.id)
        if not history:
            raise ValueError("empty conversation")
        transcript = "\n".join(
            f"{m.role}: {m.content[:500]}" for m in history[-30:]
        )
        language = "Persian" if user.language == "fa" else "English"
        response = await self.run_tool(
            user,
            transcript,
            system=(
                "Summarize this conversation in 3-5 sentences. Capture the topic, "
                f"decisions and any open questions. Respond in {language}."
            ),
            action="summary",
        )
        await self.conversations.set_summary(conversation.id, user.id, response.text)
        return response.text

    async def run_tool(
        self,
        user: User,
        prompt: str,
        *,
        system: str | None = None,
        action: str = "tool",
    ) -> AIResponse:
        """One-shot completion for tools (no conversation history written)."""
        prefs = await self.user_settings.get_or_create(user.id)
        provider, model = self.registry.resolve(prefs.model)
        started = time.monotonic()
        try:
            response = await provider.complete(
                prompt,
                system=system,
                model=model,
                temperature=temperature_for(prefs.creativity),
            )
        except Exception as exc:
            await self.usage.log(
                user.id,
                action=action,
                provider=provider.name,
                model=model or provider.model,
                success=False,
                error=str(exc),
                latency_ms=int((time.monotonic() - started) * 1000),
            )
            raise
        await self.usage.log(
            user.id,
            action=action,
            provider=provider.name,
            model=response.model,
            latency_ms=int((time.monotonic() - started) * 1000),
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
        )
        return response
