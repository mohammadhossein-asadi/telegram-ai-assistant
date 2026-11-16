"""Lightweight task classification + capability-based model routing.

This is deliberately heuristic rather than another model call: routing must not
cost a request or add latency. When auto-routing is disabled the user's chosen
model is always used.
"""

from __future__ import annotations

import re

from core.logging import get_logger
from services.ai.provider import AIProvider
from services.ai.registry import ProviderRegistry

log = get_logger(__name__)

CODING_RE = re.compile(
    r"\b(code|bug|error|traceback|function|class|python|javascript|typescript|react|sql|"
    r"compile|stack ?trace|regex|api|docker|git|npm|pip)\b|```",
    re.IGNORECASE,
)
REASONING_RE = re.compile(
    r"\b(why|prove|derive|analy[sz]e|compare|trade-?off|strategy|logic|step by step|"
    r"reason|evaluate)\b",
    re.IGNORECASE,
)
CREATIVE_RE = re.compile(
    r"\b(write|story|poem|blog|draft|creative|slogan|headline|email|caption)\b",
    re.IGNORECASE,
)
TRANSLATION_RE = re.compile(r"\b(translate|ترجمه|translation)\b", re.IGNORECASE)
SUMMARY_RE = re.compile(r"\b(summarize|summar|tl;?dr|خلاصه|bullet points|key takeaways)\b", re.IGNORECASE)


def classify_task(text: str) -> str:
    text = text or ""
    if TRANSLATION_RE.search(text):
        return "translation"
    if SUMMARY_RE.search(text):
        return "summarization"
    if CODING_RE.search(text):
        return "coding"
    if REASONING_RE.search(text):
        return "reasoning"
    if CREATIVE_RE.search(text):
        return "creative"
    return "general"


class ModelRouter:
    """Selects a provider/model pair for a task when auto-routing is enabled."""

    def __init__(self, registry: ProviderRegistry) -> None:
        self.registry = registry

    def choose(self, text: str) -> tuple[AIProvider, str | None, str]:
        task = classify_task(text)
        for provider in self.registry.providers():
            if provider.configured and task in provider.capabilities:
                return provider, provider.model, task
        provider, model = self.registry.resolve(None)
        return provider, model, task
