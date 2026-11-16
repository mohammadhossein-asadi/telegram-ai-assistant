# ADR-001 — Layered modular monolith with a service container

- **Status:** Accepted (implemented)
- **Date:** 2026-11-16 (recorded; the decision predates this document)
- **Deciders:** repository maintainer
- **Supersedes:** —
- **Related:** [ADR-002](ADR-002-persistence-and-migrations.md), [system architecture](../system-architecture.md)

## Context

The product is a Telegram bot with 13 functional domains (chat, conversations,
personas, prompts, memory, models, tools, settings, developer, about, admin,
onboarding, custom personas). It is deployed as a single process by one operator.
The team size is one developer plus AI assistants, and the codebase must remain
readable in an afternoon.

Forces at play:

- aiogram handlers are functions without constructor injection; a shared dependency
  graph must be reachable from them.
- Business rules (prompt composition, model resolution, limits) must be testable
  without Telegram.
- The domain is small; service discovery, message buses and repositories-per-feature
  would add ceremony without payoff.

## Problem

How should the code be organised so that handlers stay thin, business rules stay
testable, and the process has exactly one composition point — without adopting a
framework (DI container, Django-style apps, microservices)?

## Considered alternatives

| Option | Pros | Cons | Verdict |
| --- | --- | --- | --- |
| A. Layered monolith + module-level `container` | one construction point; tiny signatures; trivially debuggable; matches aiogram idioms | implicit dependency; handlers hard to unit test in isolation | **Chosen** |
| B. aiogram DI via middleware `data` | explicit per-handler deps; testable handlers | every handler must declare services; middleware wiring duplicated for messages/callbacks; more boilerplate for 13 routers | Rejected |
| C. Full DI framework (`dependency-injector`) | explicit wiring, scopes | new dependency, config overhead, unfamiliarity | Rejected |
| D. Clean/hexagonal with ports+adapters per domain | maximum isolation | 3× the files for a 5k-line codebase; adapters for a single DB and a single HTTP client | Rejected |
| E. Microservices (bot / AI gateway / admin) | independent scaling | one operator, one SQLite file, no scale requirement; network failure modes added | Rejected |

## Decision

Adopt **option A**: a layered modular monolith with the structure

```
bot/handlers → services → repositories → models → SQLite
        ↘ core.container (populated once in bot/main.bootstrap())
```

Rules that make the pattern hold:

1. `core/container.py` declares only *attributes* (with `TYPE_CHECKING` imports);
   no module-level instantiation of concrete services.
2. `bootstrap()` is the single place that constructs repositories and services and
   assigns them to `container`.
3. Handlers import `container` and call exactly one business operation.
4. `services/` and `database/` never import `aiogram`.
5. Router registration order is declared in one list (`handlers/__init__.py`), with
   the generic chat router last.

## Consequences

**Positive**

- Handler files stay ~100–250 lines and read as orchestration.
- Services are constructible in tests with fakes (`ChatEngine` is tested with a fake
  provider and a real in-memory repository stack).
- One place to see the whole dependency graph (`bootstrap()`).

**Negative / accepted costs**

- Importing a handler module before `bootstrap()` yields `AttributeError` on
  `container.<x>`; startup order is now load-bearing and documented.
- Handler-level unit tests would need to monkeypatch the container; the project
  tests services/repositories instead and accepts that gap.
- The container is mutable global state; parallel tests must not depend on it.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Container attribute missing / typo | All attributes are declared in the class body (type-checkable) |
| Circular imports | `TYPE_CHECKING` imports in `container.py`; services import repositories, never the reverse |
| Handler grows business logic | Review rule: if a handler exceeds ~40 lines of logic, extract into `services/` |
| Router order regression | Documented invariant + T-21 style test suggestion in [test-cases](../../testing/test-cases.md) |

## Verification

- `src/core/container.py` contains no concrete construction.
- `src/bot/main.py::bootstrap()` assigns every service.
- `grep -r "from aiogram" src/services src/database` returns nothing.
