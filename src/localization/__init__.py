from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.logging import get_logger

log = get_logger(__name__)

LOCALIZATION_DIR = Path(__file__).resolve().parent


class Localization:
    """Loads JSON language files and resolves dotted keys with formatting."""

    def __init__(self, directory: Path | None = None, default: str = "fa") -> None:
        self.directory = directory or LOCALIZATION_DIR
        self.default = default
        self._catalogs: dict[str, dict[str, str]] = {}
        self._load()

    def _load(self) -> None:
        for path in sorted(self.directory.glob("*.json")):
            lang = path.stem
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:  # pragma: no cover - dev guard
                raise ValueError(f"Invalid localization file {path}: {exc}") from exc
            self._catalogs[lang] = _flatten(raw)
        if not self._catalogs:
            raise RuntimeError(f"No localization files found in {self.directory}")
        if self.default not in self._catalogs:
            self.default = next(iter(self._catalogs))

    @property
    def languages(self) -> list[str]:
        return sorted(self._catalogs)

    def has_language(self, lang: str) -> bool:
        return lang in self._catalogs

    def t(self, lang: str, key: str, /, **kwargs: Any) -> str:
        catalog = self._catalogs.get(lang) or self._catalogs[self.default]
        template = catalog.get(key)
        if template is None:
            template = self._catalogs[self.default].get(key, key)
        if not kwargs:
            return template
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError, ValueError):  # pragma: no cover - bad placeholder
            log.warning("Localization placeholder mismatch for %s/%s", lang, key)
            return template


def _flatten(data: dict[str, Any], prefix: str = "") -> dict[str, str]:
    flat: dict[str, str] = {}
    for key, value in data.items():
        full = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(_flatten(value, full))
        else:
            flat[full] = str(value)
    return flat


# Shared singleton used across handlers.
loc = Localization()
