from __future__ import annotations

from core.config import Settings
from services.ai import ProviderRegistry
from services.chat.engine import ChatEngine
from database.models import User
from utils.text import detect_language

SUMMARY_MODES = {
    "short": "Write a short summary (2-3 sentences).",
    "detailed": "Write a detailed summary covering all important points.",
    "bullets": "Summarize as concise bullet points.",
    "takeaways": "Extract the key takeaways as a short numbered list.",
}

WRITE_MODES = {
    "improve": "Improve the writing while keeping the original meaning.",
    "rewrite": "Rewrite the text to be clearer and more effective.",
    "tone": "Rewrite the text with a more appropriate, polished tone.",
    "grammar": "Fix grammar, spelling and punctuation only; keep the wording.",
    "ideas": "Generate 5 concrete ideas based on the text.",
    "email": "Draft a well-structured email based on the text.",
}

EXPLAIN_MODES = {
    "simple": "Explain the concept in simple terms for a beginner.",
    "step": "Explain it step by step.",
    "technical": "Explain it with technical depth and precision.",
}

TARGET_LANGUAGES = {"fa": "Persian (فارسی)", "en": "English"}

CODING_MODES = {
    "explain": "Explain what the code does, part by part.",
    "debug": "Find the bug, explain the cause, then give a corrected version.",
    "generate": "Write working code that fulfils the request.",
    "review": "Review the code for correctness, clarity and risks.",
    "improve": "Suggest concrete improvements with rewritten snippets.",
}


class ToolService:
    def __init__(self, engine: ChatEngine, registry: ProviderRegistry, settings: Settings) -> None:
        self.engine = engine
        self.registry = registry
        self.settings = settings

    async def summarize(self, user: User, text: str, mode: str) -> str:
        instruction = SUMMARY_MODES.get(mode, SUMMARY_MODES["short"])
        return await self._run(user, "summarize", instruction, text)

    async def translate(self, user: User, text: str, target: str) -> str:
        if target == "auto":
            # Translate in the opposite direction of the input language.
            target = "en" if detect_language(text) == "fa" else "fa"
        lang_name = TARGET_LANGUAGES.get(target, TARGET_LANGUAGES["en"])
        return await self._run(
            user,
            "translate",
            f"Translate the text into {lang_name}. Preserve formatting. Return only the translation.",
            text,
        )

    async def write(self, user: User, text: str, mode: str) -> str:
        instruction = WRITE_MODES.get(mode, WRITE_MODES["improve"])
        return await self._run(user, "write", instruction, text)

    async def explain(self, user: User, text: str, mode: str) -> str:
        instruction = EXPLAIN_MODES.get(mode, EXPLAIN_MODES["simple"])
        return await self._run(user, "explain", instruction, text)

    async def coding(self, user: User, text: str, mode: str) -> str:
        instruction = CODING_MODES.get(mode, CODING_MODES["explain"])
        return await self._run(user, "coding", instruction, text)

    async def custom(self, user: User, text: str) -> str:
        return await self._run(
            user, "custom", "Follow the user's instruction precisely.", text
        )

    async def _run(self, user: User, action: str, instruction: str, text: str) -> str:
        language = "Persian" if user.language == "fa" else "English"
        system = (
            f"You are a precise text processing assistant. {instruction} "
            f"Respond in {language}. Do not add commentary, preamble or explanations."
        )
        response = await self.engine.run_tool(
            user, text, system=system, action=action
        )
        return response.text
