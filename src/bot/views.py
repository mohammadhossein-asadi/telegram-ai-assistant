"""Reusable screen text builders shared by several handlers."""

from __future__ import annotations

from bot.ui import t
from database.models import User, UserSettings


def main_menu_text(lang: str, prefs: UserSettings, conversation_title: str, model: str) -> str:
    persona = t(lang, f"presets.{prefs.personality}")
    style = t(lang, f"styles.{prefs.style}")
    tone = t(lang, f"tones.{prefs.tone}")
    memory = t(lang, "common.on") if prefs.memory_enabled else t(lang, "common.off")
    summary = (
        f"💬 {conversation_title}\n"
        f"🎭 {persona} · {style} · {tone}\n"
        f"🤖 {model or '—'}\n"
        f"🧠 {t(lang, 'settings.memory')}: {memory}"
    )
    return t(lang, "menu.title", summary=summary)


def persona_text(lang: str, prefs: UserSettings) -> str:
    summary = "\n".join(
        [
            t(lang, "persona.current", label=t(lang, "persona.presets"),
              value=t(lang, f"presets.{prefs.personality}")),
            t(lang, "persona.current", label=t(lang, "persona.style"),
              value=t(lang, f"styles.{prefs.style}")),
            t(lang, "persona.current", label=t(lang, "persona.tone"),
              value=t(lang, f"tones.{prefs.tone}")),
            t(lang, "persona.current", label=t(lang, "persona.creativity"),
              value=t(lang, f"creativity.{prefs.creativity}")),
        ]
    )
    return t(lang, "persona.title", summary=summary)


def memory_text(lang: str, prefs: UserSettings, context: int, count: int) -> str:
    status = t(lang, "common.on") if prefs.memory_enabled else t(lang, "common.off")
    return t(lang, "memory.title", status=status, context=context, count=count)


def model_text(lang: str, model: str, provider: str) -> str:
    return t(lang, "model.title", model=model or "—", provider=provider or "—")


def settings_text(lang: str, prefs: UserSettings, model: str, memory_enabled: bool) -> str:
    summary = "\n".join(
        [
            t(lang, "persona.current", label=t(lang, "settings.personality"),
              value=t(lang, f"presets.{prefs.personality}")),
            t(lang, "persona.current", label=t(lang, "settings.style"),
              value=t(lang, f"styles.{prefs.style}")),
            t(lang, "persona.current", label=t(lang, "settings.tone"),
              value=t(lang, f"tones.{prefs.tone}")),
            t(lang, "persona.current", label=t(lang, "settings.creativity"),
              value=t(lang, f"creativity.{prefs.creativity}")),
            t(lang, "persona.current", label=t(lang, "settings.model"), value=model or "—"),
            t(lang, "persona.current", label=t(lang, "settings.memory"),
              value=t(lang, "common.on") if memory_enabled else t(lang, "common.off")),
        ]
    )
    return t(lang, "settings.title", summary=summary)


def about_text(lang: str) -> str:
    return f"<b>{t(lang, 'about.title')}</b>\n\n{t(lang, 'about.body')}"


def developer_text(lang: str, name: str, role: str, github: str) -> str:
    return t(lang, "about.developer", name=name, role=role, github=github)


def bot_info_text(lang: str, version: str, language: str, model: str) -> str:
    return t(lang, "about.bot_info", version=version, language=language, model=model or "—")


def user_display_name(user: User) -> str:
    return user.first_name or user.username or "there"
