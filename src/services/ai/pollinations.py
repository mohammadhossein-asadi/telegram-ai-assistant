from __future__ import annotations

import re
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

# Regex to extract wait time from Pollinations 402 error message
FREE_LIMIT_RE = re.compile(r"(\d+)\s*seconds?")


class PollinationsProvider(AIProvider):
    """Free Pollinations.ai provider (no API key required)."""

    def __init__(
        self,
        *,
        name: str = "pollinations",
        model: str = "openai-fast",
        timeout: float = 60.0,
        capabilities: set[str] | frozenset[str] | None = None,
    ) -> None:
        self.name = name
        self.model = model
        self.timeout = timeout
        self.capabilities = frozenset(capabilities) if capabilities else frozenset(
            {"general", "coding", "reasoning", "creative", "translation", "summarization"}
        )
        self._text_base_url = "https://text.pollinations.ai"
        self._image_base_url = "https://image.pollinations.ai"

    @property
    def configured(self) -> bool:
        return True

    async def chat(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIResponse:
        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self._text_base_url, json=payload, headers={"Content-Type": "application/json"}
                )
        except httpx.TimeoutException as exc:
            raise AITimeoutError("AI request timed out") from exc
        except httpx.HTTPError as exc:
            raise AIError(f"Network error: {exc}") from exc

        if response.status_code == 429:
            raise AIError("Rate limited by provider (429)", status=429)
        
        # Handle Pollinations free tier limit (402 Payment Required)
        if response.status_code == 402:
            detail = response.text[:300]
            match = FREE_LIMIT_RE.search(detail)
            wait_seconds = int(match.group(1)) if match else 45
            error_msg = f"Free tier limit reached: wait {wait_seconds}s"
            raise AIError(error_msg, status=402, detail={"wait_seconds": wait_seconds})

        if response.status_code >= 400:
            detail = response.text[:300]
            raise AIError(
                f"Provider error {response.status_code}: {detail}", status=response.status_code
            )

        # Pollinations returns plain text, not JSON
        text = response.text
        return AIResponse(
            text=text.strip() if text else "",
            model=payload["model"],
            provider=self.name,
            raw={"response": text},
            prompt_tokens=0,
            completion_tokens=0,
        )

    async def generate_image(
        self,
        prompt: str,
        *,
        width: int = 1024,
        height: int = 1024,
    ) -> str:
        """Generate an image URL using Pollinations.ai."""
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        return f"{self._image_base_url}/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"

    async def health_check(self) -> tuple[bool, str]:
        """Check if the Pollinations API is reachable."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self._text_base_url)
            if response.status_code < 400:
                return True, f"OK ({response.status_code})"
            return False, f"HTTP {response.status_code}"
        except httpx.HTTPError as exc:
            return False, str(exc)[:120]