---
name: ai-provider-integration
description: Add an AI provider to this bot's abstraction — subclass AIProvider, implement chat(), map errors and timeouts, register it, and keep secrets out of logs.
---

# Skill: add an AI provider

Use when integrating a new model backend.

## What exists

```
services/ai/base.py       AIMessage · AIResponse · AIError · AIConfigurationError · AITimeoutError
services/ai/provider.py   AIProvider (ABC): abstract chat(), concrete complete() with retries
services/ai/openai_compat.py  OpenAICompatibleProvider — any /chat/completions endpoint
services/ai/registry.py   builds providers from ai_providers rows + env default
services/ai/router.py     capability-based selection (auto-routing)
services/ai/__init__.py   ProviderConfig, factory
```

`ChatEngine` (`services/chat/engine.py`) depends only on `AIProvider`; it never imports a
vendor SDK (ADR-003). Before writing code, check whether the new backend speaks
`/chat/completions` — most do, and then it needs **no** new class, just a row in
`ai_providers` with `base_url`, `api_key`, `model`.

## Steps

### 1. Subclass `AIProvider`

```python
from __future__ import annotations

import httpx

from services.ai.base import (
    AIConfigurationError, AIError, AIMessage, AIResponse, AITimeoutError,
)
from services.ai.provider import AIProvider


class MyProvider(AIProvider):
    name = "myprovider"

    def __init__(self, *, api_key: str, model: str, base_url: str, timeout: float = 60.0) -> None:
        self.api_key, self.model, self.base_url, self.timeout = api_key, model, base_url, timeout

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.model)

    async def chat(self, messages: list[AIMessage], *, model=None,
                   temperature: float = 0.7, max_tokens: int | None = None) -> AIResponse:
        if not self.configured:
            raise AIConfigurationError(f"Provider '{self.name}' is not configured")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(...)
        except httpx.TimeoutException as exc:
            raise AITimeoutError("AI request timed out") from exc
        except httpx.HTTPError as exc:
            raise AIError(f"Network error: {exc}") from exc
        ...
        return AIResponse(text=..., model=..., provider=self.name,
                          prompt_tokens=..., completion_tokens=...)
```

**Do not override `complete()`** — the base class builds the message list and applies the
single retry (`retries=1`, 1 s backoff) for you.

### 2. Error mapping (copy the existing contract)

| Upstream | Raise |
| --- | --- |
| missing key/model/base url | `AIConfigurationError` |
| 401 | `AIConfigurationError("Invalid API key (401)", status=401)` |
| 429 | `AIError("Rate limited by provider (429)", status=429)` |
| other 4xx/5xx | `AIError(f"Provider error {code}: {detail}", status=code)` |
| timeout | `AITimeoutError("AI request timed out")` |
| unparseable body | `AIError("Malformed response from provider")` |

Details are truncated to 300 characters (`_error_detail`); never include the key.

### 3. Usage must be populated

`usage_logs` records `prompt_tokens`/`completion_tokens`; return zeros when the provider
omits usage rather than `None`.

### 4. Health check

Optional `async def health_check(self) -> tuple[bool, str]` — the admin panel's
`adm:health` uses it. Keep it cheap and authenticated.

### 5. Register / configure

| Path | Change |
| --- | --- |
| OpenAI-compatible | no code — insert an `ai_providers` row (admin) or change env |
| New protocol | add the class + a branch in the factory (`services/ai/__init__.py`) |
| Capability routing | set `capabilities` so `router.py` can pick it |

### 6. Secrets

- Env default: `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, `AI_PROVIDER`.
- Admin-added rows store `api_key` **plaintext** today (ADR-005, known gap).
- Never echo a key; mask it (`sk-…abcd`). Never log prompts or completions at INFO.

### 7. Test offline

Use a fake transport or a subclass returning canned `AIResponse`; the suite must not hit
the network. Assert: text/usage mapping, `AIError` on 500, `AITimeoutError` on timeout,
`AIConfigurationError` when unconfigured.

## Verification

```bash
pytest -q
python -m compileall -q src
```

A live check (`/admin` → provider health) needs a real key — say plainly whether you ran
it.

## Known edge

An empty completion (`text == ""`) is stored and returned as-is; there is no
"empty reply" guard. A provider that can return empty text should raise `AIError` in
`chat()` instead, otherwise Telegram rejects the empty message.

## Do not

- Add a vendor SDK when an HTTP call suffices.
- Retry forever or swallow exceptions.
- Change `ChatEngine` to fit one provider's shape.
