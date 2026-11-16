from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    language = State()


class ChatFlow(StatesGroup):
    chatting = State()


class PersonaFlow(StatesGroup):
    custom = State()


class ToolFlow(StatesGroup):
    summarize = State()
    translate = State()
    write = State()
    explain = State()
    coding = State()
    custom = State()


class ConversationFlow(StatesGroup):
    rename = State()
    search = State()


class PersonaStudioFlow(StatesGroup):
    new = State()
    import_json = State()
    edit = State()


class PromptFlow(StatesGroup):
    new = State()
    edit = State()
    run = State()


class AdminFlow(StatesGroup):
    broadcast = State()
    add_provider = State()
