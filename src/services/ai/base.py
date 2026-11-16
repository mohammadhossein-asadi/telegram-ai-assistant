from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AIMessage:
    role: str
    content: str


@dataclass(slots=True)
class AIResponse:
    text: str
    model: str
    provider: str
    raw: dict[str, Any] | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0


class AIError(Exception):
    """Raised for provider misconfiguration or upstream failures."""

    def __init__(self, message: str, *, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class AIConfigurationError(AIError):
    pass


class AITimeoutError(AIError):
    pass
