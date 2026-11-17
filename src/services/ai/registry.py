from __future__ import annotations

from core.config import Settings
from core.logging import get_logger
from database.repositories import ProviderRepository
from services.ai.openai_compat import OpenAICompatibleProvider
from services.ai.pollinations import PollinationsProvider
from services.ai.provider import AIProvider

log = get_logger(__name__)


def _parse_capabilities(raw: str | None) -> set[str] | None:
    if not raw:
        return None
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


class ProviderRegistry:
    """Builds and caches providers from env config plus admin-added DB rows."""

    def __init__(self, settings: Settings, repo: ProviderRepository) -> None:
        self.settings = settings
        self.repo = repo
        self._cache: dict[str, AIProvider] = {}

    async def refresh(self) -> None:
        self._cache.clear()
        default = OpenAICompatibleProvider(
            name=self.settings.ai_provider,
            base_url=self.settings.ai_base_url,
            api_key=self.settings.ai_api_key,
            model=self.settings.ai_model,
        )
        self._cache[default.name] = default
        # Add free Pollinations provider (no API key needed)
        pollinations = PollinationsProvider()
        self._cache[pollinations.name] = pollinations
        for row in await self.repo.list_active():
            provider = OpenAICompatibleProvider(
                name=row.name,
                base_url=row.base_url,
                api_key=row.api_key,
                model=row.model,
                capabilities=_parse_capabilities(row.capabilities),
            )
            self._cache[provider.name] = provider

    def providers(self) -> list[AIProvider]:
        return list(self._cache.values())

    def get(self, name: str | None) -> AIProvider:
        if name and name in self._cache:
            return self._cache[name]
        # Prefer first configured provider
        for provider in self._cache.values():
            if provider.configured:
                return provider
        return next(iter(self._cache.values()))

    def models(self) -> list[tuple[str, str]]:
        """Return (provider_name, model) pairs available to users."""
        return [
            (provider.name, provider.model)
            for provider in self._cache.values()
            if provider.configured
        ]

    def resolve(self, selected: str | None) -> tuple[AIProvider, str | None]:
        """Resolve a user's stored model string back to a provider + model."""
        if not selected:
            # Prefer first configured provider
            for provider in self._cache.values():
                if provider.configured:
                    return provider, None
            # Fallback to first provider (may be unconfigured)
            provider = next(iter(self._cache.values()))
            return provider, None
        for provider in self._cache.values():
            if provider.model == selected and provider.configured:
                return provider, selected
        # Model not found or provider not configured - fallback to first configured
        for provider in self._cache.values():
            if provider.configured:
                return provider, None
        provider = next(iter(self._cache.values()))
        return provider, selected

    def find_by_model(self, model: str | None) -> tuple[AIProvider, str | None] | None:
        if not model:
            return None
        for provider in self._cache.values():
            if provider.model == model and provider.configured:
                return provider, model
        return None

    async def health(self) -> list[tuple[str, str, bool, str]]:
        results: list[tuple[str, str, bool, str]] = []
        for provider in self._cache.values():
            checker = getattr(provider, "health_check", None)
            if checker is None:
                results.append((provider.name, provider.model, True, "n/a"))
                continue
            ok, detail = await checker()
            results.append((provider.name, provider.model, ok, detail))
        return results
