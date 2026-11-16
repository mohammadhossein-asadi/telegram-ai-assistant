from __future__ import annotations

import re
import html

MAX_TELEGRAM_LENGTH = 4000


def split_message(text: str, limit: int = MAX_TELEGRAM_LENGTH) -> list[str]:
    """Split text into chunks that respect paragraph/line/word boundaries."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break
        window = remaining[:limit]
        split_at = window.rfind("\n\n")
        if split_at < limit // 2:
            split_at = window.rfind("\n")
        if split_at < limit // 2:
            split_at = window.rfind(" ")
        if split_at <= 0:
            split_at = limit
        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
    return chunks


def escape_html(text: str) -> str:
    return html.escape(text, quote=False)


_CODE_BLOCK = re.compile(r"```(?:\w+)?\n?(.*?)```", re.DOTALL)
_INLINE_CODE = re.compile(r"`([^`\n]+)`")
_BOLD = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_ITALIC = re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])")
_STRIKE = re.compile(r"~~(.+?)~~", re.DOTALL)
_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")


def markdown_to_telegram_html(text: str) -> str:
    """Convert a safe subset of Markdown to Telegram HTML.

    All raw HTML is escaped first, so model output cannot inject tags.
    """
    text = escape_html(text or "")

    def _code_block(match: re.Match[str]) -> str:
        return f"<pre>{match.group(1)}</pre>"

    def _inline_code(match: re.Match[str]) -> str:
        return f"<code>{match.group(1)}</code>"

    def _bold(match: re.Match[str]) -> str:
        return f"<b>{match.group(1)}</b>"

    def _italic(match: re.Match[str]) -> str:
        return f"<i>{match.group(1)}</i>"

    def _strike(match: re.Match[str]) -> str:
        return f"<s>{match.group(1)}</s>"

    def _link(match: re.Match[str]) -> str:
        label, url = match.group(1), match.group(2)
        return f'<a href="{url}">{label}</a>'

    text = _CODE_BLOCK.sub(_code_block, text)
    text = _LINK.sub(_link, text)
    text = _BOLD.sub(_bold, text)
    text = _ITALIC.sub(_italic, text)
    text = _STRIKE.sub(_strike, text)
    text = _INLINE_CODE.sub(_inline_code, text)
    return text


_PERSIAN_RE = re.compile(r"[\u0600-\u06FF]")


def detect_language(text: str) -> str:
    """Return 'fa' when the text is predominantly Persian, otherwise 'en'."""
    if not text:
        return "en"
    persian = len(_PERSIAN_RE.findall(text))
    letters = len(re.findall(r"[A-Za-z\u0600-\u06FF]", text)) or 1
    return "fa" if persian / letters >= 0.3 else "en"


def truncate(text: str, limit: int = 60) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def derive_title(text: str, limit: int = 50) -> str:
    title = truncate(text, limit)
    return title or "New chat"
