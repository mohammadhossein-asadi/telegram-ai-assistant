# ADR-003 — Provider-agnostic AI layer with a registry and heuristic routing

- **Status:** Accepted (implemented)
- **Date:** 2026-11-16
- **Related:** [technology stack](../technology-stack.md), [functional requirements FR-MODEL-*](../../product/functional-requirements.md)

## Context

The bot could depend on one vendor SDK, or speak a protocol. Users want to choose a
model; the operator wants to add a cheaper or local endpoint without a redeploy; the
project wants to avoid vendor lock-in for a portfolio artifact. Latency and cost are
dominated by the model call, so any routing mechanism must not add its own request.

## Problem

How do we support multiple AI providers/models with one code path, allow runtime
provider addition, and route tasks to capable models — without introducing an SDK
dependency, a plugin framework, or an extra inference call?

## Considered alternatives

| Option | Pros | Cons | Verdict |
| --- | --- | --- | --- |
| A. `AIProvider` ABC + `OpenAICompatibleProvider` over httpx + registry + regex router | one request shape; any compatible base URL; no SDK; zero-cost routing | non-compatible APIs need a new class | **Chosen** |
| B. Official `openai` SDK only | simplest code | vendor lock-in; SDK-specific retries/timeouts; other vendors via base URL only, awkwardly | Rejected |
| C. LiteLLM / LangChain abstraction | many providers "for free" | heavy dependency, opaque behaviour, own retry/cost semantics, version churn | Rejected |
| D. One class per vendor (OpenAI, Anthropic, Google…) from day one | native APIs | unused breadth; each class is untested surface | Deferred — add per protocol when needed |
| E. LLM-based router (ask a model to pick a model) | better classification | doubles cost and latency per message | Rejected |
| F. No routing (user picks manually) | simplest | users cannot express "use the coding model for code" | Rejected as default; kept as the default *behaviour* (`auto_routing=False`) |

## Decision

1. **Interface:** `AIProvider` (`services/ai/provider.py`) with
   `chat(messages, model, temperature, max_tokens)` plus a `complete()` helper that
   retries once with linear backoff.
2. **Implementation:** `OpenAICompatibleProvider` speaks
   `POST {base_url}/chat/completions` over httpx; parses content, model and token
   usage defensively; maps failures to `AIError` / `AIConfigurationError` /
   `AITimeoutError` with an HTTP status when available.
3. **Registry:** `ProviderRegistry.refresh()` always inserts the env-configured
   provider, then merges admin rows from `ai_providers`; `resolve(model_string)`
   maps a stored model back to its provider and falls back to the first provider.
4. **Capabilities:** each provider declares a `frozenset` of task classes
   (`general, coding, reasoning, creative, translation, summarization`).
5. **Routing:** `classify_task()` uses ordered regexes; `ModelRouter.choose()`
   picks the first configured provider advertising the class, else the default.
   Routing runs **only** when `user_settings.auto_routing` is true.
6. **Precedence:** conversation `model` override → auto-routing → user model → default.

## Consequences

**Positive**

- Adding a compatible endpoint at runtime requires no code change.
- The engine is testable with a fake provider implementing the same ABC.
- Routing is deterministic, instant and free.

**Negative / accepted costs**

- Claude/Gemini-native protocols are not supported without a new provider class.
- Regex classification is approximate (Persian keywords partially covered:
  `ترجمه`, `خلاصه` are included; other classes are English-centric).
- `resolve()` matches on the *model string*, so two providers exposing the same model
  name are ambiguous — the first match wins.

## Risks

| Risk | Mitigation |
| --- | --- |
| Misclassification routes to a weaker model | conservative regexes; user can disable auto-routing per account |
| Provider returns unexpected schema | defensive `.get()` with defaults; `AIError` on missing content |
| Admin adds a broken provider | `health()` reports it; requests to it are logged as failures |
| Stored model removed upstream | `resolve()` falls back to the first configured provider |

## Verification

- `tests/test_routing.py` — classification table, capability preference, fallback.
- `tests/test_chat_engine.py` — conversation model override reaches the provider.
- `tests/test_chat_engine.py::test_respond_persists_both_turns` — usage and history
  written on success with the fake provider.
