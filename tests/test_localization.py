from __future__ import annotations

from localization import Localization, loc


def test_both_languages_load() -> None:
    assert set(loc.languages) >= {"fa", "en"}


def test_catalogs_have_identical_keys() -> None:
    local = Localization()
    fa = local._catalogs["fa"]
    en = local._catalogs["en"]
    assert set(fa) == set(en), f"missing keys: {set(fa) ^ set(en)}"


def test_formatting_and_fallback() -> None:
    assert "Buffy" in loc.t("en", "start.welcome", name="Buffy")
    # Unknown key returns the key itself rather than raising.
    assert loc.t("en", "does.not.exist") == "does.not.exist"


def test_unknown_language_falls_back_to_default() -> None:
    text = loc.t("xx", "common.saved")
    assert text == loc.t(loc.default, "common.saved")
