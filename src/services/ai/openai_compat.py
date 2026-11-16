from __future__ import annotations

from typing import Any

import httpx

from core.logging import get_logger
from services.ai.base import (
    AIConfigurationError,
    AIError,
    AIMessage,
    AIResponse,
    AITimeoutError,
)
from services.ai.provider import AIProvider

log = get_logger(__name__)

DEFAULT_CAPABILITIES = frozenset(
    {"general", "coding", "reasoning", "creative", "translation", "summarization"}
)


class OpenAICompatibleProvider(AIProvider):
    """Any /chat/completions endpoint (OpenAI, OpenRouter, Groq, Ollama, …)."""

    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 60.0,
        extra_headers: dict[str, str] | None = None,
        capabilities: set[str] | frozenset[str] | None = None,
    ) -> None:
        self.name = name
        self.base_url = (base_url or "").rstrip("/")
        self.api_key = api_key or ""
        self.model = model
        self.timeout = timeout
        self.extra_headers = extra_headers or {}
        self.capabilities = frozenset(capabilities) if capabilities else DEFAULT_CAPABILITIES

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)

    async def chat(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIResponse:
        if not self.configured:
            raise AIConfigurationError(f"Provider '{self.name}' is not configured")

        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **self.extra_headers,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions", json=payload, headers=headers
                )
        except httpx.TimeoutException as exc:
            raise AITimeoutError("AI request timed out") from exc
        except httpx.HTTPError as exc:
            raise AIError(f"Network error: {exc}") from exc

        if response.status_code == 401:
            raise AIConfigurationError("Invalid API key (401)", status=401)
        if response.status_code == 429:
            raise AIError("Rate limited by provider (429)", status=429)
        if response.status_code >= 400:
            detail = _error_detail(response)
            raise AIError(
                f"Provider error {response.status_code}: {detail}", status=response.status_code
            )

        try:
            data = response.json()
            text = data["choices"][0]["message"]["content"] or ""
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise AIError("Malformed response from provider") from exc

        usage = data.get("usage") or {}
        return AIResponse(
            text=text.strip(),
            model=payload["model"],
            provider=self.name,
            raw=data,
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
        )

    async def health_check(self) -> tuple[bool, str]:
        """Cheap authenticated probe of the endpoint."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
            if response.status_code < 400:
                return True, f"OK ({response.status_code})"
            return False, f"HTTP {response.status_code}"
        except httpx.HTTPError as exc:
            return False, str(exc)[:120]


def _error_detail(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text[:300]
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict):
            return str(error.get("message", error))[:300]
        if error:
            return str(error)[:300]
    return response.text[:300]
