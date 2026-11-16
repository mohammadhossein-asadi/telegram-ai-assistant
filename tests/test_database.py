from __future__ import annotations

import pytest

from database import Database, run_migrations
from database.repositories import (
    ConversationRepository,
    MemoryRepository,
    MessageRepository,
    SettingsRepository,
    UserRepository,
)


@pytest.fixture
async def db(tmp_path):
    database = Database(f"sqlite+aiosqlite:///{tmp_path}/test.db")
    await run_migrations(database)
    yield database
    await database.dispose()


async def test_user_and_settings_creation(db) -> None:
    users = UserRepository(db)
    settings = SettingsRepository(db)

    user, created = await users.get_or_create(123, username="a", first_name="A")
    assert created is True
    again, created_again = await users.get_or_create(123)
    assert created_again is False
    assert again.id == user.id

    prefs = await settings.get_or_create(user.id)
    assert prefs.personality == "friendly"

    updated = await settings.update(user.id, tone="formal")
    assert updated.tone == "formal"

    reset = await settings.reset(user.id)
    assert reset.tone == "casual"


async def test_conversation_and_messages_are_isolated(db) -> None:
    users = UserRepository(db)
    convs = ConversationRepository(db)
    messages = MessageRepository(db)

    alice, _ = await users.get_or_create(1)
    bob, _ = await users.get_or_create(2)

    alice_conv = await convs.create(alice.id, "Alice chat")
    await messages.add(alice_conv.id, "user", "hello")
    await messages.add(alice_conv.id, "assistant", "hi")

    assert await convs.get(alice_conv.id, bob.id) is None
    assert await convs.get(alice_conv.id, alice.id) is not None

    recent = await messages.recent(alice_conv.id, 10)
    assert [m.role for m in recent] == ["user", "assistant"]

    assert await convs.delete(alice_conv.id, bob.id) is False
    assert await convs.delete(alice_conv.id, alice.id) is True
    assert await messages.recent(alice_conv.id, 10) == []


async def test_memory_upsert_and_clear(db) -> None:
    users = UserRepository(db)
    memory = MemoryRepository(db)
    user, _ = await users.get_or_create(7)

    await memory.upsert(user.id, "name", "Sam")
    await memory.upsert(user.id, "name", "Samuel")
    assert await memory.count(user.id) == 1

    await memory.clear(user.id)
    assert await memory.count(user.id) == 0
