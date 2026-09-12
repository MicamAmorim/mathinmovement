from __future__ import annotations

from typing import Any

import numpy as np
from manim import (
    LEFT,
    PI,
    RIGHT,
    UP,
    Create,
    DashedLine,
    FadeOut,
    Line,
    MathTex,
    Polygon,
    Rectangle,
    Rotate,
    Text,
    VGroup,
)

CYAN = "#55D6CF"
GOLD = "#FFCC78"
WHITE = "#EEF2FF"
MUTED = "#9CAAC5"
GREEN = "#8DE2A7"
PINK = "#F28DB2"


def P(x: float, y: float):
    return np.array([x, y, 0.0])


def _math(tex: str, size: int = 30, color: str = WHITE):
    return MathTex(tex, font_size=size, color=color)


def build_visual(name: str, *, horizontal: bool = False):
    if name == "triangle_instrument":
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
            Text("Figura 1", font_size=20, color=MUTED).move_to(P(-2, 2.25)),
            instrument,
            Text("Figura 2", font_size=20, color=MUTED).move_to(P(2, 2.25)),
            tri,
            alt,
            _math(r"8\,\mathrm{cm}", 24, GOLD).next_to(alt, RIGHT, buff=0.12),
        )

    if name == "equilateral":
        width = 4.3 if horizontal else 4.0
        tri = Polygon(
            P(-width / 2, -1.3),
            P(width / 2, -1.3),
            P(0, 2.1),
            color=CYAN,
            fill_opacity=0.15,
        )
        alt = DashedLine(P(0, -1.3), P(0, 2.1), color=GOLD)
        return VGroup(
            tri,
            alt,
            _math(r"8\,\mathrm{cm}", 25, GOLD).next_to(alt, RIGHT),
            _math(r"\ell/2", 25).move_to(P(-1.0, -1.7)),
            _math(r"\ell/2", 25).move_to(P(1.0, -1.7)),
        )

    box = Rectangle(width=5.5, height=3.4, color=CYAN)
    label = Text(name or "visual", font_size=24, color=MUTED)
    return VGroup(box, label)


def run_demo_action(scene, state: dict[str, Any], step: dict[str, Any], *, horizontal: bool = False):
    visual = step.get("visual") or {}
    action = visual.get("action")

    if action == "create_triangle":
        tri = Polygon(
            P(-2.8, -0.9),
            P(2.2, -0.9),
            P(-0.8, 1.6),
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.22,
            stroke_width=3,
        )
        if horizontal:
            tri.scale(1.05)
        state["triangle"] = tri
        scene.play(Create(tri), run_time=1.5)
        return

    if action == "show_height":
        tri = state.get("triangle")
        if tri is None:
            return
        h = DashedLine(P(-0.8, -0.9), P(-0.8, 1.6), color=GOLD)
        labels = VGroup(
            _math("b", 34, CYAN).move_to(P(-0.3, -1.35)),
            _math("h", 34, GOLD).move_to(P(-1.18, 0.25)),
        )
        state["height"] = VGroup(h, labels)
        scene.play(Create(h), Create(labels), run_time=1.0)
        return

    if action == "complete_parallelogram":
        tri = state.get("triangle")
        if tri is None:
            return
        if "height" in state:
            scene.play(FadeOut(state["height"]), run_time=0.45)
        other = tri.copy().set_color(GOLD)
        state["other"] = other
        scene.add(other)
        scene.play(other.animate.shift(UP * 0.45), run_time=0.55)
        scene.play(Rotate(other, PI, about_point=other.get_center()), run_time=1.1)
        target_center = P(1.7, 0.35)
        scene.play(other.animate.shift(target_center - other.get_center()), run_time=1.0)
        group = VGroup(tri, other)
        if horizontal:
            scene.play(group.animate.shift(LEFT * 2.7), run_time=0.55)
        else:
            scene.play(group.animate.shift(LEFT * 0.7), run_time=0.55)
        state["parallelogram"] = group
        return

    if action == "hold":
        return
