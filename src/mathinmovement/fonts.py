from __future__ import annotations

import os


def _available_fonts() -> dict[str, str]:
    try:
        import manimpango  # type: ignore
        return {str(name).casefold(): str(name) for name in manimpango.list_fonts()}
    except Exception:
        return {}


def _choose(candidates: list[str], fallback: str = "Sans") -> str:
    available = _available_fonts()
    for candidate in candidates:
        if candidate and candidate.casefold() in available:
            return available[candidate.casefold()]
    return next((x for x in candidates if x), fallback)


def choose_demo_font() -> str:
    # Ordem idêntica à identidade visual legada das demonstrações.
    return _choose([
        os.getenv("MANIM_FONT", "").strip(),
        "DejaVu Sans",
        "Arial",
        "Liberation Sans",
    ])


def choose_enem_font() -> str:
    # Ordem idêntica ao font_utils.py legado do ENEM.
    requested = os.getenv("ENEM_FONT", "").strip()
    return _choose([
        requested,
        "DejaVu Sans",
        "Segoe UI",
        "Aptos",
        "Arial",
        "Liberation Sans",
        "Noto Sans",
        "Sans",
    ], requested or "Sans")


DEMO_FONT = choose_demo_font()
ENEM_TEXT_FONT = choose_enem_font()
