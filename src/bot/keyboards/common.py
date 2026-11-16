"""Inline keyboard builders. Callback data stays short (< 64 bytes)."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.ui import t
from database.models import AIProvider, Conversation, UserSettings

PRESETS = [
    "friendly",
    "professional",
    "funny",
    "creative",
    "supportive",
    "analytical",
    "teacher",
    "programmer",
    "sarcastic",
    "custom",
]
STYLES = ["short", "balanced", "detailed", "step_by_step", "technical", "beginner"]
TONES = ["casual", "formal", "warm", "direct", "humorous"]
CREATIVITY = ["low", "balanced", "high"]
TOOL_KINDS = ["summarize", "translate", "write", "explain", "custom"]


def btn(text: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=data)


def _grid(options: list[str], per_row: int, label, data_prefix: str, current: str | None = None):
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for option in options:
        text = label(option)
        if option == current:
            text = f"• {text}"
        row.append(btn(text, f"{data_prefix}{option}"))
        if len(row) == per_row:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return rows


def back_home(lang: str, back: str = "home") -> list[list[InlineKeyboardButton]]:
    return [[btn(t(lang, "common.back"), back), btn(t(lang, "common.home"), "home")]]


def back_home_kb(lang: str, back: str = "home") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=back_home(lang, back))


def main_menu(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "menu.chat"), "menu:chat"), btn(t(lang, "menu.persona"), "menu:persona")],
        [btn(t(lang, "menu.memory"), "menu:memory"), btn(t(lang, "menu.model"), "menu:model")],
        [btn(t(lang, "menu.tools"), "menu:tools"), btn(t(lang, "menu.convs"), "menu:convs")],
        [btn(t(lang, "menu.prompts"), "menu:prompts"),
         btn(t(lang, "menu.developer"), "menu:developer")],
        [btn(t(lang, "menu.settings"), "menu:settings"), btn(t(lang, "menu.about"), "menu:about")],
        [btn(t(lang, "menu.lang"), "menu:lang")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def language_kb(lang: str, back: str = "home") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn("🇮🇷 فارسی", "lang:fa"), btn("🇬🇧 English", "lang:en")],
            [btn(t(lang, "common.back"), back)],
        ]
    )


def persona_kb(lang: str, prefs: UserSettings) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "persona.presets"), "pv:presets"),
         btn(t(lang, "persona.style"), "pv:style")],
        [btn(t(lang, "persona.tone"), "pv:tone"),
         btn(t(lang, "persona.creativity"), "pv:cr")],
        [btn(t(lang, "persona.custom"), "pv:custom"),
         btn(t(lang, "cpersona.mine"), "cps:list")],
    ]
    rows += back_home(lang)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def presets_kb(lang: str, current: str) -> InlineKeyboardMarkup:
    rows = _grid(PRESETS, 2, lambda o: t(lang, f"presets.{o}"), "ps:", current)
    rows += back_home(lang, "menu:persona")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def styles_kb(lang: str, current: str) -> InlineKeyboardMarkup:
    rows = _grid(STYLES, 2, lambda o: t(lang, f"styles.{o}"), "st:", current)
    rows += back_home(lang, "menu:persona")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tones_kb(lang: str, current: str) -> InlineKeyboardMarkup:
    rows = _grid(TONES, 2, lambda o: t(lang, f"tones.{o}"), "tn:", current)
    rows += back_home(lang, "menu:persona")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def creativity_kb(lang: str, current: str) -> InlineKeyboardMarkup:
    rows = _grid(CREATIVITY, 3, lambda o: t(lang, f"creativity.{o}"), "cr:", current)
    rows += back_home(lang, "menu:persona")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def memory_kb(lang: str, enabled: bool) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "memory.toggle"), "mem:toggle")],
        [btn(t(lang, "memory.clear_conv"), "mem:clear")],
        [btn(t(lang, "memory.clear_all"), "mem:clearall")],
    ]
    rows += back_home(lang)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def model_kb(lang: str, models: list[tuple[str, str]], current: str | None) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for index, (provider, model) in enumerate(models):
        label = f"{model}"
        if model == current:
            label = f"• {label}"
        rows.append([btn(f"{label} — {provider}", f"mdl:{index}")])
    if not rows:
        rows.append([btn(t(lang, "model.empty"), "noop")])
    rows += back_home(lang)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tools_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "tools.summarize"), "tools:summarize"),
         btn(t(lang, "tools.translate"), "tools:translate")],
        [btn(t(lang, "tools.write"), "tools:write"),
         btn(t(lang, "tools.explain"), "tools:explain")],
        [btn(t(lang, "tools.coding"), "tools:coding"),
         btn(t(lang, "tools.custom"), "tools:custom")],
    ]
    rows += back_home(lang)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def summary_modes_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "tools.sum_short"), "ts:short")],
        [btn(t(lang, "tools.sum_detailed"), "ts:detailed")],
        [btn(t(lang, "tools.sum_bullets"), "ts:bullets")],
        [btn(t(lang, "tools.sum_takeaways"), "ts:takeaways")],
    ]
    rows += back_home(lang, "menu:tools")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def translate_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "tools.trans_fa"), "tt:fa"), btn(t(lang, "tools.trans_en"), "tt:en")],
        [btn(t(lang, "tools.trans_auto"), "tt:auto")],
    ]
    rows += back_home(lang, "menu:tools")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def write_modes_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "tools.write_improve"), "tw:improve"),
         btn(t(lang, "tools.write_rewrite"), "tw:rewrite")],
        [btn(t(lang, "tools.write_tone"), "tw:tone"),
         btn(t(lang, "tools.write_grammar"), "tw:grammar")],
        [btn(t(lang, "tools.write_ideas"), "tw:ideas"),
         btn(t(lang, "tools.write_email"), "tw:email")],
    ]
    rows += back_home(lang, "menu:tools")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def coding_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "coding.explain"), "tc:explain"), btn(t(lang, "coding.debug"), "tc:debug")],
        [btn(t(lang, "coding.generate"), "tc:generate"), btn(t(lang, "coding.review"), "tc:review")],
        [btn(t(lang, "coding.improve"), "tc:improve")],
    ]
    rows += back_home(lang, "menu:tools")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def explain_modes_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "tools.explain_simple"), "te:simple")],
        [btn(t(lang, "tools.explain_step"), "te:step")],
        [btn(t(lang, "tools.explain_technical"), "te:technical")],
    ]
    rows += back_home(lang, "menu:tools")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def conversations_kb(
    lang: str, conversations: list[Conversation], page: int, total_pages: int
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for conv in conversations:
        title = conv.title if len(conv.title) <= 28 else conv.title[:27] + "…"
        rows.append([btn(f"💬 {title}", f"conv:open:{conv.id}")])
        rows.append(
            [
                btn("✏️", f"conv:rn:{conv.id}"),
                btn("📌", f"conv:pin:{conv.id}"),
                btn("📦", f"conv:arch:{conv.id}"),
                btn("🗑", f"conv:del:{conv.id}"),
            ]
        )
    rows.append(
        [btn(t(lang, "convs.new"), "conv:new"), btn(t(lang, "convs.search"), "conv:search")]
    )
    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(btn("◀️", f"conv:list:{page - 1}"))
    if total_pages > 1:
        nav.append(btn(f"{page + 1}/{total_pages}", "noop"))
    if page + 1 < total_pages:
        nav.append(btn("▶️", f"conv:list:{page + 1}"))
    if nav:
        rows.append(nav)
    rows += back_home(lang)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_kb(lang: str, confirm_data: str, cancel_data: str = "home") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn(t(lang, "common.yes"), confirm_data), btn(t(lang, "common.no"), cancel_data)]
        ]
    )


def settings_kb(lang: str, prefs: UserSettings, memory_enabled: bool) -> InlineKeyboardMarkup:
    emoji_state = t(lang, "common.on") if prefs.emoji_enabled else t(lang, "common.off")
    mem_state = t(lang, "common.on") if memory_enabled else t(lang, "common.off")
    rows = [
        [btn(t(lang, "settings.language"), "menu:lang"),
         btn(t(lang, "settings.model"), "menu:model")],
        [btn(t(lang, "settings.personality"), "menu:persona"),
         btn(t(lang, "settings.memory"), f"set:mem")],
        [btn(f"{t(lang, 'settings.response_lang')}: {_rlang(lang, prefs.response_language)}", "set:rlang")],
        [btn(f"{t(lang, 'settings.routing')}: "
             f"{t(lang, 'common.on') if prefs.auto_routing else t(lang, 'common.off')}", "set:routing")],
        [btn(f"{t(lang, 'settings.emoji')}: {emoji_state}", "set:emoji")],
        [btn(t(lang, "settings.reset"), "set:reset")],
        [btn(t(lang, "settings.privacy"), "set:privacy")],
    ]
    rows += back_home(lang)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _rlang(lang: str, value: str) -> str:
    return {
        "auto": t(lang, "settings.auto"),
        "fa": t(lang, "settings.response_fa"),
        "en": t(lang, "settings.response_en"),
    }.get(value, t(lang, "settings.auto"))


def about_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "about.github"), "ab:dev")],
        [btn(t(lang, "about.about_bot"), "ab:bot")],
        [btn(t(lang, "about.support"), "ab:support")],
    ]
    rows += back_home(lang)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "admin.stats"), "adm:stats")],
        [btn(t(lang, "admin.broadcast"), "adm:broadcast")],
        [btn(t(lang, "admin.providers"), "adm:providers")],
        [btn(t(lang, "admin.health"), "adm:health")],
        [btn(t(lang, "admin.limits"), "adm:limits")],
    ]
    rows += back_home(lang)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def providers_kb(lang: str, providers: list[AIProvider]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for provider in providers:
        rows.append(
            [btn(f"{provider.name} — {provider.model}", "noop"), btn("🗑", f"adm:delprov:{provider.id}")]
        )
    rows.append([btn(t(lang, "admin.add_provider"), "adm:addprov")])
    rows += back_home(lang, "adm:home")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def chat_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn(t(lang, "chat.new_chat"), "conv:new"), btn(t(lang, "common.home"), "home")]
        ]
    )


def open_conversation_kb(lang: str, conversation_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn(t(lang, "convs.summary"), f"conv:sum:{conversation_id}"),
             btn(t(lang, "convs.export"), f"conv:exp:{conversation_id}")],
            [btn(t(lang, "chat.new_chat"), "conv:new"), btn(t(lang, "common.home"), "home")],
        ]
    )


def developer_kb(lang: str, profile_url: str) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "gh.repos"), "gh:repos:0"), btn(t(lang, "gh.popular"), "gh:popular")],
        [InlineKeyboardButton(text=t(lang, "gh.profile_btn"), url=profile_url)],
        [btn(t(lang, "gh.refresh"), "gh:refresh")],
    ]
    rows += back_home(lang)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def repos_kb(lang: str, repos: list[dict], page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for offset, repo in enumerate(repos):
        index = page * REPO_PAGE_SIZE + offset
        stars = f"⭐{repo['stars']}" if repo.get("stars") else ""
        rows.append([btn(f"📦 {repo['name']} {stars}".strip(), f"gh:repo:{index}")])
    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(btn("◀️", f"gh:repos:{page - 1}"))
    if total_pages > 1:
        nav.append(btn(f"{page + 1}/{total_pages}", "noop"))
    if page + 1 < total_pages:
        nav.append(btn("▶️", f"gh:repos:{page + 1}"))
    if nav:
        rows.append(nav)
    rows += back_home(lang, "menu:developer")
    return InlineKeyboardMarkup(inline_keyboard=rows)


REPO_PAGE_SIZE = 5


def repo_detail_kb(lang: str, html_url: str, page: int) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=t(lang, "gh.open"), url=html_url)]]
    rows += back_home(lang, f"gh:repos:{page}")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def custom_personas_kb(lang: str, personas) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for persona in personas:
        mark = "⭐ " if persona.is_default else ""
        rows.append([btn(f"{persona.emoji} {mark}{persona.name}", f"cps:{persona.id}")])
    rows.append([btn(t(lang, "cpersona.create"), "cps:new")])
    rows.append([btn(t(lang, "cpersona.import_btn"), "cps:import")])
    rows += back_home(lang, "menu:persona")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def custom_persona_detail_kb(lang: str, persona) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "cpersona.set_default"), f"cps:default:{persona.id}")],
        [btn(t(lang, "cpersona.assign"), f"cps:assign:{persona.id}")],
        [btn(t(lang, "cpersona.edit"), f"cps:edit:{persona.id}"),
         btn(t(lang, "cpersona.export"), f"cps:exp:{persona.id}")],
        [btn(t(lang, "cpersona.delete"), f"cps:del:{persona.id}")],
    ]
    rows += back_home(lang, "cps:list")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def prompts_kb(lang: str, prompts, page: int, total_pages: int, active_category: str | None = None) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for prompt in prompts:
        rows.append([btn(f"📝 {prompt.title}", f"pr:{prompt.id}")])
    rows.append([btn(t(lang, "prompts.create"), "pr:new")])
    if active_category:
        rows.append([btn(active_category, "noop"), btn(t(lang, "prompts.filter_all"), "pr:cats")])
    else:
        rows.append([btn(t(lang, "prompts.categories"), "pr:cats")])
    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(btn("◀️", f"pr:list:{page - 1}"))
    if total_pages > 1:
        nav.append(btn(f"{page + 1}/{total_pages}", "noop"))
    if page + 1 < total_pages:
        nav.append(btn("▶️", f"pr:list:{page + 1}"))
    if nav:
        rows.append(nav)
    rows += back_home(lang)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def prompt_detail_kb(lang: str, prompt) -> InlineKeyboardMarkup:
    rows = [
        [btn(t(lang, "prompts.run"), f"pr:run:{prompt.id}")],
        [btn(t(lang, "prompts.edit"), f"pr:edit:{prompt.id}"),
         btn(t(lang, "cpersona.export"), f"pr:exp:{prompt.id}")],
        [btn(t(lang, "prompts.delete"), f"pr:del:{prompt.id}")],
    ]
    rows += back_home(lang, "pr:list:0")
    return InlineKeyboardMarkup(inline_keyboard=rows)


def prompt_categories_kb(lang: str, categories: list[str]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for index, category in enumerate(categories):
        rows.append([btn(f"🏷 {category}", f"pr:cat:{index}")])
    rows.append([btn(t(lang, "prompts.filter_all"), "pr:list:0")])
    rows += back_home(lang, "pr:list:0")
    return InlineKeyboardMarkup(inline_keyboard=rows)
