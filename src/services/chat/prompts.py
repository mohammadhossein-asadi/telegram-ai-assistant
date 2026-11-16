"""Prompt construction for personality, memory and tools."""

from __future__ import annotations

from database.models import UserMemory, UserSettings

PERSONALITY_PROMPTS: dict[str, str] = {
    "friendly": "You are a warm, approachable companion. You keep a natural, human tone.",
    "professional": "You are a polished, precise professional assistant. You are concise and credible.",
    "programmer": "You are a senior software engineer. You give correct, idiomatic, runnable code.",
    "creative": "You are an imaginative writer, offering fresh angles and vivid detail.",
    "teacher": "You are a patient teacher. You build understanding from first principles.",
    "analytical": "You are a rigorous thinker. You structure answers and justify conclusions.",
    "research": "You are a careful research assistant. You separate evidence from inference.",
    "funny": "You are witty and playful while still being accurate and helpful.",
    "supportive": "You are empathetic and validating. You help the user feel heard and capable.",
    "sarcastic": "You are dryly sarcastic and clever, but never cruel, and always useful.",
    "custom": "You follow the user's custom instructions exactly.",
}

STYLE_PROMPTS: dict[str, str] = {
    "short": "Answer in as few words as possible while staying complete.",
    "balanced": "Answer with a balanced level of detail.",
    "detailed": "Give a thorough, well-structured answer.",
    "step_by_step": "Structure the answer as clear numbered steps.",
    "technical": "Use precise technical language and specifics.",
    "beginner": "Explain in beginner-friendly language, avoiding jargon.",
}

TONE_PROMPTS: dict[str, str] = {
    "casual": "Use a casual, conversational tone.",
    "formal": "Use a formal, respectful tone.",
    "warm": "Use a warm and friendly tone.",
    "direct": "Be direct and to the point.",
    "humorous": "Use light humor where appropriate.",
}

TEMPERATURES: dict[str, float] = {"low": 0.2, "balanced": 0.7, "high": 1.1}

LANGUAGE_NAMES = {"fa": "Persian (فارسی)", "en": "English"}


def build_system_prompt(
    settings: UserSettings,
    *,
    ui_language: str,
    memories: list[UserMemory] | None = None,
    detected_language: str | None = None,
    persona_instructions: str | None = None,
) -> str:
    lines: list[str] = []

    if persona_instructions:
        lines.append(persona_instructions.strip())
    elif settings.personality == "custom" and settings.custom_instructions:
        lines.append(settings.custom_instructions.strip())
    else:
        lines.append(
            PERSONALITY_PROMPTS.get(settings.personality, PERSONALITY_PROMPTS["friendly"])
        )
        if settings.custom_instructions:
            lines.append(settings.custom_instructions.strip())

    lines.append(STYLE_PROMPTS.get(settings.style, STYLE_PROMPTS["balanced"]))
    lines.append(TONE_PROMPTS.get(settings.tone, TONE_PROMPTS["casual"]))

    if settings.response_language == "auto":
        target = detected_language or ui_language
    else:
        target = settings.response_language
    language_name = LANGUAGE_NAMES.get(target, LANGUAGE_NAMES["en"])
    lines.append(f"Reply in {language_name} unless the user explicitly asks otherwise.")

    if not settings.emoji_enabled:
        lines.append("Do not use emojis.")

    if memories and settings.memory_enabled:
        facts = "\n".join(f"- {m.key}: {m.value}" for m in memories[:20])
        lines.append("Known facts about this user (use them naturally):\n" + facts)

    return "\n".join(lines)


def temperature_for(creativity: str) -> float:
    return TEMPERATURES.get(creativity, 0.7)
