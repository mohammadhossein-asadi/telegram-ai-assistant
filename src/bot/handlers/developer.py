from __future__ import annotations

import math

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards import common as kb
from bot.ui import safe_edit, t
from core.container import container
from core.logging import get_logger

log = get_logger(__name__)
router = Router(name="developer")
PAGE_SIZE = kb.REPO_PAGE_SIZE


def _profile_url() -> str:
    return container.config.developer_github


@router.callback_query(F.data.in_({"menu:developer", "menu:profile"}))
async def cb_profile(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    await _render_profile(call, lang)


@router.callback_query(F.data == "gh:refresh")
async def cb_refresh(call: CallbackQuery, lang: str) -> None:
    container.github.clear_cache()
    await call.answer(t(lang, "gh.refresh"))
    await _render_profile(call, lang, force=True)


async def _render_profile(call: CallbackQuery, lang: str, force: bool = False) -> None:
    cfg = container.config
    profile = await container.github.profile(force=force)

    if not profile:
        await safe_edit(call, t(lang, "gh.unavailable"), kb.developer_kb(lang, _profile_url()))
        return

    text = t(
        lang,
        "gh.title",
        name=profile.get("name") or cfg.developer_name,
        role=cfg.developer_role,
        followers=profile.get("followers", 0),
        following=profile.get("following", 0),
        repos=profile.get("public_repos", 0),
    )
    if profile.get("bio"):
        text += "\n\n" + t(lang, "gh.bio", bio=profile["bio"])
    if cfg.bot_branding_enabled:
        text += "\n\n" + t(lang, "start.dev_credit", developer=cfg.developer_name)

    keyboard = kb.developer_kb(lang, profile.get("html_url") or _profile_url())

    if profile.get("avatar_url"):
        try:
            await call.message.answer_photo(
                profile["avatar_url"], caption=text[:1000], reply_markup=keyboard
            )
            return
        except TelegramBadRequest as exc:
            log.debug("Avatar send failed, falling back to text: %s", exc)
    await safe_edit(call, text, keyboard)


@router.callback_query(F.data.startswith("gh:repos:"))
async def cb_repos(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    try:
        page = int(call.data.rsplit(":", 1)[1])
    except ValueError:
        page = 0

    repos = await container.github.repos()
    if not repos:
        await safe_edit(call, t(lang, "gh.empty"), kb.back_home_kb(lang, "menu:developer"))
        return

    total_pages = max(1, math.ceil(len(repos) / PAGE_SIZE))
    page = max(0, min(page, total_pages - 1))
    window = repos[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]

    lines = [f"<b>{t(lang, 'gh.repos')}</b>", ""]
    for repo in window:
        language = repo.get("language") or "—"
        description = repo.get("description") or t(lang, "gh.no_description")
        lines.append(
            t(lang, "gh.repo_line", name=repo["name"], stars=repo.get("stars", 0), language=language)
        )
        lines.append(f"   {description[:110]}")
        lines.append("")

    await safe_edit(
        call, "\n".join(lines).strip(), kb.repos_kb(lang, window, page, total_pages)
    )


@router.callback_query(F.data == "gh:popular")
async def cb_popular(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    popular = await container.github.popular(limit=10)
    if not popular:
        await safe_edit(call, t(lang, "gh.empty"), kb.back_home_kb(lang, "menu:developer"))
        return

    lines = [f"<b>{t(lang, 'gh.popular')}</b>", ""]
    buttons: list[list[InlineKeyboardButton]] = []
    for repo in popular:
        lines.append(
            t(lang, "gh.repo_line", name=repo["name"], stars=repo.get("stars", 0),
              language=repo.get("language") or "—")
        )
        if repo.get("description"):
            lines.append(f"   {repo['description'][:110]}")
        if repo.get("html_url"):
            buttons.append(
                [InlineKeyboardButton(text=f"🔗 {repo['name']}", url=repo["html_url"])]
            )
        lines.append("")

    buttons += kb.back_home(lang, "menu:developer")
    await safe_edit(
        call, "\n".join(lines).strip(), InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("gh:repo:"))
async def cb_repo_detail(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    try:
        index = int(call.data.rsplit(":", 1)[1])
    except ValueError:
        return
    repos = await container.github.repos()
    if not (0 <= index < len(repos)):
        return
    repo = repos[index]
    text = t(
        lang,
        "gh.repo_detail",
        name=repo["name"],
        description=repo.get("description") or t(lang, "gh.no_description"),
        stars=repo.get("stars", 0),
        forks=repo.get("forks", 0),
        language=repo.get("language") or "—",
        updated=repo.get("updated_at") or "—",
    )
    page = index // PAGE_SIZE
    await safe_edit(call, text, kb.repo_detail_kb(lang, repo.get("html_url", ""), page))
