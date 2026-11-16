from __future__ import annotations

from utils.text import (
    derive_title,
    detect_language,
    markdown_to_telegram_html,
    split_message,
)


def test_split_respects_limit() -> None:
    text = "word " * 2000
    chunks = split_message(text, limit=100)
    assert len(chunks) > 1
    assert all(len(chunk) <= 100 for chunk in chunks)
    assert " ".join(chunks).split() == text.split()


def test_short_text_is_single_chunk() -> None:
    assert split_message("hello") == ["hello"]
    assert split_message("") == []


def test_markdown_is_escaped_and_converted() -> None:
    result = markdown_to_telegram_html("**bold** and <script>alert(1)</script>")
    assert "<b>bold</b>" in result
    assert "<script>" not in result
    assert "&lt;script&gt;" in result


def test_inline_code_and_links() -> None:
    result = markdown_to_telegram_html("`code` [site](https://example.com)")
    assert "<code>code</code>" in result
    assert '<a href="https://example.com">site</a>' in result


def test_detect_language() -> None:
    assert detect_language("سلام حال شما چطور است") == "fa"
    assert detect_language("hello, how are you today?") == "en"


def test_derive_title() -> None:
    assert derive_title("") == "New chat"
    assert len(derive_title("x" * 100, limit=20)) <= 20
