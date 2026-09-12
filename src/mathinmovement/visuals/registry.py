from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    PI,
    RIGHT,
    UP,
    Circle,
    DashedLine,
    Line,
    MathTex,
    Polygon,
    Rectangle,
    Text,
    VGroup,
)

from ..fonts import ENEM_TEXT_FONT

CYAN = "#55D6CF"
GOLD = "#FFCC78"
WHITE = "#EEF2FF"
MUTED = "#9CAAC5"
GREEN = "#8DE2A7"
PINK = "#F28DB2"


def P(x: float, y: float):
    return np.array([x, y, 0.0])


def math_label(tex: str, size: int = 26, color: str = WHITE):
    return MathTex(tex, font_size=size, color=color)


def panel_title(text: str, x: float):
    return Text(
        text,
        font=ENEM_TEXT_FONT,
        font_size=17,
        color=MUTED,
    ).move_to(P(x, 2.7))


def source_figure(kind: str):
    """Reconstruction catalog for statement figures.

    The pilot implementation is intentionally byte-for-byte equivalent in
    geometry to the approved legacy renderer. More entries are ported here
    before their native renderer can be promoted to production.
    """
    if kind == "triangle_instrument":
        a = P(-3.3, -1.0)
        b = P(-0.7, -1.0)
        c = P(-2.0, 1.5)
        instrument = VGroup(
            Line(a, b, color=CYAN),
            Line(b, c, color=CYAN),
            Line(c, a + RIGHT * 0.35, color=CYAN),
            Line(a + RIGHT * 0.35, a + RIGHT * 0.7, color=GOLD),
        )
        a2 = P(0.7, -1.1)
        b2 = P(3.3, -1.1)
        c2 = P(2.0, 1.5)
        tri = Polygon(a2, b2, c2, color=CYAN, fill_opacity=0.08)
        alt = DashedLine(c2, P(2, -1.1), color=GOLD)
        return VGroup(
            panel_title("Figura 1", -2),
            instrument,
            panel_title("Figura 2", 2),
            tri,
            alt,
            math_label(r"8\,\mathrm{cm}", 24, GOLD).next_to(alt, RIGHT, buff=0.12),
        )

    return VGroup(
        Rectangle(width=5.5, height=3.5, color=CYAN),
        Text("Figura", font=ENEM_TEXT_FONT, font_size=22, color=MUTED),
    )


def concept_diagram(kind: str):
    if kind == "equilateral":
        tri = Polygon(
            P(-2, -1.3),
            P(2, -1.3),
            P(0, 2.1),
            color=CYAN,
            fill_opacity=0.15,
        )
        alt = DashedLine(P(0, -1.3), P(0, 2.1), color=GOLD)
        return VGroup(
            tri,
            alt,
            math_label(r"8\,cm", 25, GOLD).next_to(alt, RIGHT),
            math_label(r"\ell/2", 25).move_to(P(-1, -1.65)),
        )

    return VGroup(
        Rectangle(width=5, height=3, color=CYAN),
        Text(kind or "generic", font=ENEM_TEXT_FONT, font_size=20, color=MUTED),
    )


# Backwards-compatible public names for the v2 package API.
def build_visual(name: str, *, horizontal: bool = False):
    del horizontal
    if name == "equilateral":
        return concept_diagram(name)
    return source_figure(name)


def run_demo_action(scene, state, step, *, horizontal: bool = False):
    # The parity renderer now owns approved demo motion programs. This hook is
    # retained as an extension point for the generic DSL.
    del scene, state, step, horizontal
    return None
