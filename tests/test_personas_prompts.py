from __future__ import annotations

import pytest

from database import Database, run_migrations
from database.repositories import (
    ConversationRepository,
    PromptRepository,
    UserRepository,
)
from database.repositories.personas import PersonaRepository


@pytest.fixture
async def env(tmp_path):
    db = Database(f"sqlite+aiosqlite:///{tmp_path}/p.db")
    await run_migrations(db)
    users = UserRepository(db)
    alice, _ = await users.get_or_create(1, first_name="A")
    bob, _ = await users.get_or_create(2, first_name="B")
    yield db, PersonaRepository(db), PromptRepository(db), ConversationRepository(db), alice, bob
    await db.dispose()


async def test_persona_crud_and_default(env) -> None:
    _db, personas, _prompts, _convs, alice, bob = env
    persona = await personas.create(alice.id, "Strict", "Be strict.", "🧐")
    assert persona.name == "Strict"

    # Same name updates instead of duplicating
    again = await personas.create(alice.id, "Strict", "Be very strict.")
    assert again.id == persona.id
    assert again.instructions == "Be very strict."

    assert await personas.set_default(persona.id, alice.id) is True
    listing = await personas.list_for_user(alice.id)
    assert listing[0].is_default is True

    # Isolation: another user cannot touch it
    assert await personas.get(persona.id, bob.id) is None
    assert await personas.delete(persona.id, bob.id) is False

    assert await personas.update_instructions(persona.id, alice.id, "New") is True
    assert await personas.delete(persona.id, alice.id) is True
    assert await personas.count(alice.id) == 0


async def test_prompt_crud_and_categories(env) -> None:
    _db, _personas, prompts, _convs, alice, bob = env
    prompt = await prompts.create(alice.id, "Email", "Write an email about {topic}", "work")
    await prompts.create(alice.id, "Blog", "Write a blog post", "work")
    await prompts.create(alice.id, "Recipe", "Invent a recipe", "food")

    assert set(await prompts.categories(alice.id)) == {"work", "food"}
    assert len(await prompts.list_for_user(alice.id, "work")) == 2
    assert await prompts.get(prompt.id, bob.id) is None

    assert await prompts.update_body(prompt.id, alice.id, "Updated") is True
    assert await prompts.delete(prompt.id, alice.id) is True
    assert len(await prompts.list_for_user(alice.id)) == 2


async def test_conversation_pin_persona_model_search(env) -> None:
    _db, _personas, prompts, convs, alice, bob = env
    conv = await convs.create(alice.id, "Planning meeting")
    await convs.create(alice.id, "Recipe ideas")

    assert await convs.set_pinned(conv.id, alice.id, True) is True
    listing = await convs.list_for_user(alice.id)
    assert listing[0].id == conv.id

    assert await convs.set_persona(conv.id, alice.id, 42) is True
    assert await convs.set_model(conv.id, alice.id, "some-model") is True
    assert await convs.set_summary(conv.id, alice.id, "short summary") is True

    refreshed = await convs.get(conv.id, alice.id)
    assert refreshed.persona_id == 42
    assert refreshed.model == "some-model"
    assert refreshed.summary == "short summary"

    assert len(await convs.search(alice.id, "Recipe")) == 1
    assert await convs.search(bob.id, "Recipe") == []
