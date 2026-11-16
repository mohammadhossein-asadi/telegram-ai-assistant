from __future__ import annotations

import pytest

from core.config import Settings
from services.ai import ModelRouter, ProviderRegistry, classify_task
from services.ai.provider import AIProvider


class StubProvider(AIProvider):
    def __init__(self, name: str, model: str, capabilities: set[str]) -> None:
        self.name = name
        self.model = model
        self.capabilities = frozenset(capabilities)

    async def chat(self, messages, *, model=None, temperature=0.7, max_tokens=None):
        raise NotImplementedError


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Translate this to English", "translation"),
        ("Summarize the article in bullets", "summarization"),
        ("Why is my python function raising a traceback?", "coding"),
        ("Analyse the trade-offs of this strategy", "reasoning"),
        ("Write a poem about the sea", "creative"),
        ("Hello there", "general"),
    ],
)
def test_classify_task(text: str, expected: str) -> None:
    assert classify_task(text) == expected


def test_router_prefers_capable_provider() -> None:
    registry = ProviderRegistry(Settings(), None)  # type: ignore[arg-type]
    registry._cache = {  # type: ignore[attr-defined]
        "general": StubProvider("general", "cheap-model", {"general"}),
        "coder": StubProvider("coder", "code-model", {"coding", "general"}),
    }
    router = ModelRouter(registry)
    provider, model, task = router.choose("debug this python error")
    assert task == "coding"
    assert provider.name == "coder"
    assert model == "code-model"


def test_router_falls_back_when_nothing_matches() -> None:
    registry = ProviderRegistry(Settings(), None)  # type: ignore[arg-type]
    registry._cache = {"only": StubProvider("only", "m1", {"general"})}  # type: ignore[attr-defined]
    provider, model, task = ModelRouter(registry).choose("write me a regex for emails")
    assert task == "coding"
    assert provider.name == "only"
