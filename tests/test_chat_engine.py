from __future__ import annotations

import pytest

from core.config import Settings
from database import Database, run_migrations
from database.repositories import (
    ConversationRepository,
    MemoryRepository,
    MessageRepository,
    SettingsRepository,
    UsageRepository,
    UserRepository,
)
from services.ai import AIMessage, AIResponse, ProviderRegistry
from services.ai.provider import AIProvider
from services.chat import ChatEngine


class FakeProvider(AIProvider):
    name = "fake"
    model = "fake-model"

    def __init__(self) -> None:
        self.calls: list[list[AIMessage]] = []

    @property
    def configured(self) -> bool:
        return True

    async def chat(self, messages, *, model=None, temperature=0.7, max_tokens=None) -> AIResponse:
        self.calls.append(messages)
        awaitable = AIResponse(text="پاسخ آزمایشی", model=model or self.model, provider=self.name)
        return awaitable

    async def complete(self, prompt, *, system=None, model=None, temperature=0.7, retries=1):
        return AIResponse(text=f"tool:{prompt[:10]}", model=self.model, provider=self.name)


@pytest.fixture
async def env(tmp_path):
    db = Database(f"sqlite+aiosqlite:///{tmp_path}/engine.db")
    await run_migrations(db)
    settings = Settings(ai_model="fake-model", ai_api_key="x")
    registry = ProviderRegistry(settings, None)  # type: ignore[arg-type]
    fake = FakeProvider()
    registry._cache = {"fake": fake}  # type: ignore[attr-defined]

    users = UserRepository(db)
    prefs = SettingsRepository(db)
    convs = ConversationRepository(db)
    messages = MessageRepository(db)
    memory = MemoryRepository(db)
    usage = UsageRepository(db)

    user, _ = await users.get_or_create(99, first_name="Test")
    conv = await convs.create(user.id, "Test chat")

    engine = ChatEngine(settings, registry, convs, messages, prefs, memory, usage)
    yield engine, fake, user, conv, messages
    await db.dispose()


async def test_respond_persists_both_turns(env) -> None:
    engine, fake, user, conv, messages = env
    response = await engine.respond(user, conv, "سلام")
    assert response.text == "پاسخ آزمایشی"

    stored = await messages.recent(conv.id, 10)
    assert [m.role for m in stored] == ["user", "assistant"]

    # System prompt is language-aware and includes Persian instruction.
    system_prompt = fake.calls[0][0]
    assert system_prompt.role == "system"
    assert "Persian" in system_prompt.content


async def test_engine_respects_max_context(env) -> None:
    engine, fake, user, conv, messages = env
    for index in range(30):
        await messages.add(conv.id, "user", f"msg{index}")
        await messages.add(conv.id, "assistant", f"reply{index}")
    await engine.respond(user, conv, "latest")
    sent = fake.calls[0]
    # system + context window + current user message
    assert len(sent) <= engine.settings.max_context_messages + 2


async def test_conversation_model_override(env) -> None:
    engine, fake, user, conv, _messages = env
    conv.model = "some-other-model"
    await engine.respond(user, conv, "hello")
    assert fake.calls, "provider should have been called"


async def test_persona_instructions_reach_system_prompt(env) -> None:
    engine, fake, user, conv, _messages = env

    class StubPersona:
        instructions = "You are a pirate. Speak like a pirate."

    class StubPersonaRepo:
        async def get(self, persona_id, user_id):
            return StubPersona() if persona_id == 7 and user_id == user.id else None

    engine.personas = StubPersonaRepo()
    conv.persona_id = 7
    await engine.respond(user, conv, "ahoy")
    assert "pirate" in fake.calls[0][0].content


async def test_tool_run_does_not_write_history(env) -> None:
    engine, fake, user, conv, messages = env
    result = await engine.run_tool(user, "summarize this", system="be terse", action="summarize")
    assert result.text.startswith("tool:")
    assert await messages.recent(conv.id, 10) == []
