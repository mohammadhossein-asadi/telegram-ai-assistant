"""Lightweight task classification."""

import re

SUMMARY_RE = re.compile(r"\b(summarize|summar|tl;?dr|خلاصه|bullet points|key takeaways)\b", re.IGNORECASE)

def classify_task(text: str) -> str:
    text = text or ""
    if SUMMARY_RE.search(text):
        return "summarization"
    return "general"