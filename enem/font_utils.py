from __future__ import annotations

import os


def choose_text_font() -> str:
    """Choose a Pango font that actually exists on the current machine.

    ENEM_FONT can be used to force a preferred family.  We otherwise prefer
    DejaVu Sans on Linux and Segoe UI on Windows, then fall back to common
    sans-serif families.
    """
    requested = os.getenv("ENEM_FONT", "").strip()
    candidates = [
        requested,
        "DejaVu Sans",
        "Segoe UI",
        "Aptos",
        "Arial",
        "Liberation Sans",
        "Noto Sans",
        "Sans",
    ]

    try:
        import manimpango  # type: ignore

        available = {str(name).casefold(): str(name) for name in manimpango.list_fonts()}
        for candidate in candidates:
            if candidate and candidate.casefold() in available:
                return available[candidate.casefold()]
    except Exception:
        pass

    # Generic Pango family; safe fallback even when font enumeration fails.
    return requested or "Sans"


TEXT_FONT = choose_text_font()
