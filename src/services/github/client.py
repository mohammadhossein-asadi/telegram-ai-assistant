"""Async GitHub REST client with in-memory TTL caching and graceful failure.

Only public data is requested. An optional token raises the rate limit; the bot
still works without one. Every method returns ``None``/``[]`` on failure so the
UI can show a fallback instead of an exception.
"""

from __future__ import annotations

import time
from typing import Any

import httpx

from core.logging import get_logger

log = get_logger(__name__)

API_ROOT = "https://api.github.com"


class GitHubClient:
    def __init__(
        self,
        username: str = "mohammadhossein-asadi",
        token: str = "",
        ttl: int = 900,
        timeout: float = 15.0,
    ) -> None:
        self.username = username
        self.token = token
        self.ttl = ttl
        self.timeout = timeout
        self._cache: dict[str, tuple[float, Any]] = {}

    # ── cache ────────────────────────────────────────────────────────────
    def _cached(self, key: str) -> Any | None:
        entry = self._cache.get(key)
        if not entry:
            return None
        stamp, value = entry
        if time.monotonic() - stamp > self.ttl:
            self._cache.pop(key, None)
            return None
        return value

    def _store(self, key: str, value: Any) -> Any:
        self._cache[key] = (time.monotonic(), value)
        return value

    def clear_cache(self) -> None:
        self._cache.clear()

    # ── http ─────────────────────────────────────────────────────────────
    @property
    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "mohammadhossein-ai-bot"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any | None:
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self._headers) as client:
                response = await client.get(f"{API_ROOT}{path}", params=params)
        except httpx.HTTPError as exc:
            log.warning("GitHub request failed (%s): %s", path, exc)
            return None

        if response.status_code == 404:
            log.info("GitHub resource not found: %s", path)
            return None
        if response.status_code in (403, 429):
            remaining = response.headers.get("X-RateLimit-Remaining")
            log.warning("GitHub rate limited (%s), remaining=%s", path, remaining)
            return None
        if response.status_code >= 400:
            log.warning("GitHub error %s for %s", response.status_code, path)
            return None
        try:
            return response.json()
        except ValueError:
            return None

    # ── public API ───────────────────────────────────────────────────────
    async def profile(self, *, force: bool = False) -> dict[str, Any] | None:
        key = f"profile:{self.username}"
        if not force:
            cached = self._cached(key)
            if cached is not None:
                return cached
        data = await self._get(f"/users/{self.username}")
        if not isinstance(data, dict):
            return None
        normalized = {
            "login": data.get("login", self.username),
            "name": data.get("name") or data.get("login") or self.username,
            "avatar_url": data.get("avatar_url"),
            "html_url": data.get("html_url") or f"https://github.com/{self.username}",
            "bio": data.get("bio"),
            "location": data.get("location"),
            "public_repos": data.get("public_repos"),
            "followers": data.get("followers"),
            "following": data.get("following"),
        }
        return self._store(key, normalized)

    async def repos(self, *, force: bool = False) -> list[dict[str, Any]]:
        key = f"repos:{self.username}"
        if not force:
            cached = self._cached(key)
            if cached is not None:
                return cached
        data = await self._get(
            f"/users/{self.username}/repos",
            params={"sort": "updated", "per_page": 100, "type": "owner"},
        )
        if not isinstance(data, list):
            return []
        normalized = [
            {
                "name": repo.get("name", "?"),
                "full_name": repo.get("full_name", ""),
                "html_url": repo.get("html_url", ""),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "updated_at": (repo.get("updated_at") or "")[:10],
                "archived": bool(repo.get("archived")),
                "fork": bool(repo.get("fork")),
            }
            for repo in data
        ]
        normalized.sort(key=lambda r: r["updated_at"], reverse=True)
        return self._store(key, normalized)

    async def popular(self, limit: int = 10) -> list[dict[str, Any]]:
        all_repos = await self.repos()
        ranked = sorted(all_repos, key=lambda r: r["stars"], reverse=True)
        return [r for r in ranked[:limit] if not r.get("fork")]

    async def find_repo(self, name: str) -> dict[str, Any] | None:
        for repo in await self.repos():
            if repo["name"].lower() == name.lower():
                return repo
        return None
