from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod

from services.ai.base import AIMessage, AIResponse


class AIProvider(ABC):
    """Abstraction over any chat-completion backend."""

    name: str = "base"
    model: str = ""
    capabilities: frozenset[str] = frozenset(
        {"general", "coding", "reasoning", "creative", "translation", "summarization"}
    )

    @property
    def configured(self) -> bool:
        return True

    @abstractmethod
    async def chat(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIResponse:
        raise NotImplementedError

    async def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        retries: int = 1,
    ) -> AIResponse:
        messages: list[AIMessage] = []
        if system:
            messages.append(AIMessage("system", system))
        messages.append(AIMessage("user", prompt))
        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                return await self.chat(
                    messages, model=model, temperature=temperature
                )
            except Exception as exc:  # noqa: BLE001 - retried then re-raised
                last_error = exc
                if attempt < retries:
                    await asyncio.sleep(1.0 * (attempt + 1))
        assert last_error is not None
        raise last_error
