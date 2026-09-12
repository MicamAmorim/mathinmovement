from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    PI,
    RIGHT,
    UP,
    Arc,
    Arrow,
    Axes,
    Circle,
    DashedLine,
    Dot,
    DoubleArrow,
    Ellipse,
    Line,
    MathTex,
    Polygon,
    Rectangle,
    RegularPolygon,
    Square,
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

    if kind == "cup_frustum":
        trap = Polygon(
            P(-1.8, -1.6),
            P(1.8, -1.6),
            P(2.4, 1.6),
            P(-2.4, 1.6),
            color=CYAN,
            fill_opacity=0.12,
        )
        handle = Arc(
            radius=1.25,
            start_angle=-PI / 2,
            angle=PI,
            color=GOLD,
        ).shift(RIGHT * 2.1)
        height = DoubleArrow(
            P(-2.8, -1.6),
            P(-2.8, 1.6),
            buff=0,
            color=GOLD,
            tip_length=0.12,
        )
        return VGroup(
            trap,
            handle,
            height,
            math_label("12", 22, GOLD).next_to(height, LEFT),
            math_label(r"D=10", 22).move_to(P(0, 2.0)),
            math_label(r"d=8", 22).move_to(P(0, -2.0)),
        )

    if kind == "castle_scale":
        castle = VGroup(
            Rectangle(
                width=3.4,
                height=2.1,
                color=CYAN,
                fill_opacity=0.08,
            ).shift(UP * 0.25),
            Polygon(
                P(-1.7, 1.3),
                P(-1.05, 2.0),
                P(-0.4, 1.3),
                color=CYAN,
            ),
            Polygon(
                P(0.4, 1.3),
                P(1.05, 2.0),
                P(1.7, 1.3),
                color=CYAN,
            ),
        )
        bridge = Line(
            P(-3, -1.8),
            P(3, -1.8),
            color=GOLD,
            stroke_width=7,
        )
        return VGroup(
            castle,
            bridge,
            math_label(
                r"38{,}4\,m\to160\,cm",
                24,
                GOLD,
            ).next_to(bridge, DOWN),
            math_label(
                r"1{,}68\,m\to7\,cm",
                24,
            ).move_to(P(0, -2.8)),
        )

    if kind == "roads":
        axes = Axes(
            x_range=[0, 55, 10],
            y_range=[0, 45, 10],
            x_length=6.5,
            y_length=5.2,
            tips=False,
            axis_config={"color": MUTED, "stroke_width": 2},
        )
        point_a = axes.c2p(20, 40)
        point_b = axes.c2p(50, 20)
        dots = VGroup(Dot(point_a, color=CYAN), Dot(point_b, color=CYAN))
        labels = VGroup(
            math_label("A", 22, CYAN).next_to(dots[0], UP),
            math_label("B", 22, CYAN).next_to(dots[1], UP),
        )
        xs = [20, 30, 35, 40, 50]
        romans = ["I", "II", "III", "IV", "V"]
        candidates = VGroup()
        for x, roman in zip(xs, romans):
            dot = Dot(axes.c2p(x, 0), radius=0.06, color=GOLD)
            label = math_label(roman, 18, GOLD).next_to(
                dot, DOWN, buff=0.08
            )
            candidates.add(VGroup(dot, label))
        point_x = axes.c2p(40, 0)
        roads = VGroup(
            Line(point_a, point_x, color=GREEN),
            Line(point_b, point_x, color=GREEN),
        )
        return VGroup(axes, roads, dots, labels, candidates)

    if kind == "cone_dims":
        base = Ellipse(width=4.4, height=1.0, color=CYAN)
        apex = P(0, 3.0)
        sides = VGroup(
            Line(base.get_left(), apex, color=CYAN),
            Line(base.get_right(), apex, color=CYAN),
        )
        altitude = DashedLine(P(0, 0), apex, color=GOLD)
        return VGroup(
            base,
            sides,
            altitude,
            math_label(r"8\,cm", 24).move_to(P(0, -0.75)),
            math_label(r"10\,cm", 24, GOLD).next_to(
                altitude, RIGHT
            ),
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

    if kind in ("cone_frustum", "trapezoid_spin"):
        trap = Polygon(
            P(-2, -1.5),
            P(2, -1.5),
            P(1, 1.7),
            P(-1, 1.7),
            color=CYAN,
            fill_opacity=0.18,
        )
        axis = DashedLine(P(0, -2.1), P(0, 2.3), color=GOLD)
        return VGroup(
            trap,
            axis,
            math_label("R", 25, GOLD).move_to(P(1, -1.85)),
            math_label("r", 25).move_to(P(0.5, 2.05)),
        )

    if kind == "shape_areas":
        return VGroup(
            RegularPolygon(3, radius=0.9, color=CYAN),
            Square(1.5, color=GOLD),
            Circle(0.85, color=GREEN),
        ).arrange(RIGHT, buff=0.7)

    if kind in ("box", "pool", "stairs"):
        rect = Rectangle(
            width=5.5,
            height=3.3,
            color=CYAN,
            fill_opacity=0.12,
        )
        lines = VGroup(
            *[
                Line(
                    P(-2.75 + i * 1.1, -1.65),
                    P(-2.75 + i * 1.1, 1.65),
                    color=MUTED,
                )
                for i in range(1, 5)
            ]
        )
        return VGroup(
            rect,
            lines,
            math_label("A_b", 28, GOLD).move_to(P(0, -2)),
            math_label("h", 28, GOLD).move_to(P(3.2, 0)),
        )

    if kind in (
        "cylinder",
        "cylinder_compare",
        "cylinder_sphere",
        "cylinders_sheet",
    ):
        top = Ellipse(width=4, height=1, color=CYAN).shift(UP * 1.5)
        bottom = top.copy().shift(DOWN * 3)
        sides = VGroup(
            Line(P(-2, 1.5), P(-2, -1.5), color=CYAN),
            Line(P(2, 1.5), P(2, -1.5), color=CYAN),
        )
        radius = Line(ORIGIN, P(2, 0), color=GOLD)
        return VGroup(
            top,
            bottom,
            sides,
            radius,
            math_label("r", 25, GOLD).next_to(radius, UP),
            math_label("h", 25, GOLD).move_to(P(2.4, 0)),
        )

    if kind == "scale":
        small = Square(1.4, color=GOLD).shift(LEFT * 2)
        large = Square(3, color=CYAN).shift(RIGHT * 1.2)
        return VGroup(
            small,
            large,
            Arrow(small.get_right(), large.get_left(), color=WHITE),
            math_label("k", 30, GREEN),
        )

    if kind == "reflection":
        axes = Axes(
            x_range=[0, 55, 10],
            y_range=[-25, 45, 10],
            x_length=6.2,
            y_length=6.0,
            tips=False,
            axis_config={"color": MUTED},
        )
        point_a = axes.c2p(20, 40)
        point_b = axes.c2p(50, 20)
        reflected_b = axes.c2p(50, -20)
        point_x = axes.c2p(40, 0)
        dot_x = Dot(point_x, color=PINK)
        return VGroup(
            axes,
            Dot(point_a, color=CYAN),
            Dot(point_b, color=CYAN),
            Dot(reflected_b, color=GOLD),
            DashedLine(point_b, reflected_b, color=GOLD),
            Line(point_a, reflected_b, color=GREEN),
            dot_x,
            math_label("IV", 20, PINK).next_to(dot_x, DOWN),
        )

    if kind == "sphere_scale":
        return VGroup(
            Circle(0.8, color=GOLD),
            Circle(1.6, color=CYAN),
        ).arrange(RIGHT, buff=1)

    if kind == "cone":
        return source_figure("cone_dims")

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
