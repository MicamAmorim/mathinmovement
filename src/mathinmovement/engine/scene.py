from __future__ import annotations

import os
import textwrap
from pathlib import Path

import numpy as np
from manim import *

from ..config import PROJECT_ROOT
from ..fonts import DEMO_FONT, ENEM_TEXT_FONT
from ..registry import Registry
from ..visuals import build_visual
from ..visuals.registry import concept_diagram, source_figure

BG = "#0B1020"
WHITE = "#EEF2FF"
CYAN = "#55D6CF"
GOLD = "#FFCC78"
MUTED = "#9CAAC5"
PINK = "#F28DB2"
GREEN = "#8DE2A7"
RED = "#FF7D7D"
BLUE = "#79A7FF"

VIDEO_FORMAT = os.getenv("MIM_FORMAT", "vertical").strip().lower()
if VIDEO_FORMAT not in {"vertical", "horizontal"}:
    VIDEO_FORMAT = "vertical"
IS_HORIZONTAL = VIDEO_FORMAT == "horizontal"
FAST_PREVIEW = os.getenv("MIM_FAST_PREVIEW", "0").lower() in {"1", "true", "yes"}

config.frame_width = 16 if IS_HORIZONTAL else 9
config.frame_height = 9 if IS_HORIZONTAL else 16
config.background_color = BG


def P(x, y):
    return np.array([x, y, 0.0])


def _lv(vertical, horizontal):
    return horizontal if IS_HORIZONTAL else vertical


def fit(mob, w=None, h=None):
    if w is None:
        w = _lv(7.5, 13.5)
    if mob.width > w:
        mob.scale_to_fit_width(w)
    if h and mob.height > h:
        mob.scale_to_fit_height(h)
    return mob


def mt(tex, size=45, color=WHITE):
    return fit(MathTex(tex, font_size=size, color=color), _lv(7.5, 13.2))


def enem_txt(s, size=26, color=WHITE, width=46, weight=NORMAL):
    wrapped = "\n".join(textwrap.fill(p, width) for p in str(s).splitlines())
    return fit(
        Text(
            wrapped,
            font=ENEM_TEXT_FONT,
            font_size=size,
            color=color,
            weight=weight,
            line_spacing=0.9,
        ),
        _lv(7.5, 13.5),
    )


def rigid_motion(mob, angle, shift):
    """Rigid rotation + translation preserving lengths and area."""
    original = mob.copy()
    return UpdateFromAlphaFunc(
        mob,
        lambda m, t: m.become(
            original.copy().rotate(angle * t, about_point=ORIGIN).shift(t * shift)
        ),
    )


def polygon_xy(points, color=CYAN, fill_opacity=0.22, stroke_width=3):
    return Polygon(
        *[P(x, y) for x, y in points],
        color=color,
        stroke_width=stroke_width,
        fill_color=color,
        fill_opacity=fill_opacity,
    )


def regular_polygon_points(n, radius=2.5, center=P(0, 0), start_angle=PI / 2):
    return [
        center
        + radius
        * np.array(
            [
                np.cos(start_angle - k * TAU / n),
                np.sin(start_angle - k * TAU / n),
                0,
            ]
        )
        for k in range(n)
    ]


def safe_mathtex(tex, font_size=50, color=WHITE, max_width=7.4):
    obj = MathTex(tex, font_size=font_size, color=color)
    if obj.width > max_width:
        obj.scale_to_fit_width(max_width)
    return obj


class UnifiedContentScene(Scene):
    """Native v2 scene engine.

    It reads only v2 manifests/registry. Visual behavior is ported from the
    approved renderers without importing legacy scene or data modules at runtime.
    """

    def wait(self, duration=1, **kwargs):
        kwargs.setdefault("frozen_frame", True)
        return super().wait(duration, **kwargs)

    def play(self, *animations, **kwargs):
        if getattr(self, "_profile", "") == "motion_math_v1":
            kwargs["run_time"] = kwargs.get("run_time", 1) * float(
                os.getenv("MANIM_PACE", "1.15")
            )
        return super().play(*animations, **kwargs)

    def construct(self):
        content_id = os.getenv("MIM_CONTENT_ID")
        if not content_id:
            raise RuntimeError("MIM_CONTENT_ID não foi definido pelo renderer.")

        self.record = Registry().rebuild().get(content_id)
        self.manifest = self.record.manifest
        narration = self.manifest.get("narration") or {}
        self.narr = {
            str(segment["key"]): segment
            for segment in narration.get("segments", [])
            if isinstance(segment, dict) and segment.get("key")
        }

        if self.record.type == "demo":
            self._profile = "motion_math_v1"
            self.render_demo()
            return
        if self.record.type == "qenem":
            self._profile = "qenem_v1"
            self.render_qenem()
            return
        raise RuntimeError(f"Tipo não suportado: {self.record.type}")

    # ------------------------------------------------------------------
    # Demo profile: port of MotionMathScene identity and timing
    # ------------------------------------------------------------------

    def demo_text(self, s, size=28, color=WHITE, max_width=7.4, weight=NORMAL):
        t = Text(s, font=DEMO_FONT, font_size=size, color=color, weight=weight)
        if t.width > max_width:
            t.scale_to_fit_width(max_width)
        return t

    def demo_header(self, number, title, formula=None, category=None):
        category = category or "GEOMETRIA"
        self.brand = self.demo_text("MATEMÁTICA EM MOVIMENTO", 17, MUTED).move_to(P(0, 6.75))
        self.counter = self.demo_text(f"{number}  /  {category}", 19, CYAN).move_to(P(0, 5.95))
        self.title_mob = self.demo_text(title, 38, WHITE, weight=BOLD).move_to(P(0, 5.02))
        self.add(self.brand)
        self.play(FadeIn(self.counter, shift=UP * 0.12), run_time=0.55)
        self.play(Write(self.title_mob), run_time=1.0)
        self.intro_formula = VGroup()
        if formula:
            self.intro_formula = safe_mathtex(formula, 54).move_to(P(0, 3.55))
            self.play(Write(self.intro_formula), run_time=1.25)
        self.caption_mob = VGroup()
        self.work_formula = VGroup()
        signature = (self.manifest.get("presentation") or {}).get("signature", "MIQUÉIAS AMORIM")
        self.signature = self.demo_text(signature, 15, MUTED).move_to(P(0, -6.78))
        self.add(self.signature)
        self.wait(0.55)

    def demo_hide_intro_formula(self):
        if len(self.intro_formula) > 0:
            self.play(FadeOut(self.intro_formula), run_time=0.45)
            self.intro_formula = VGroup()

    def demo_caption(self, s, color=WHITE, size=25, y=-3.28):
        new = self.demo_text(textwrap.fill(s, width=47), size, color).move_to(P(0, y))
        if len(self.caption_mob) > 0:
            self.play(
                FadeOut(self.caption_mob),
                FadeIn(new, shift=UP * 0.10),
                run_time=0.42,
            )
        else:
            self.play(FadeIn(new, shift=UP * 0.10), run_time=0.42)
        self.caption_mob = new
        self.wait(max(1.4, len(s.split()) / 3.0))
        return new

    def demo_equation(self, tex, color=WHITE, size=50, y=-4.75, transform=True):
        new = safe_mathtex(tex, size, color).move_to(P(0, y))
        if len(self.work_formula) > 0 and transform:
            self.play(ReplacementTransform(self.work_formula, new), run_time=1.05)
        else:
            if len(self.work_formula) > 0:
                self.play(FadeOut(self.work_formula), run_time=0.25)
            self.play(Write(new), run_time=0.95)
        self.work_formula = new
        self.wait(2.0)
        return new

    def demo_end(self, pause=2.4):
        if len(self.work_formula) > 0:
            self.play(
                Indicate(self.work_formula, color=CYAN, scale_factor=1.04),
                run_time=1.0,
            )
        self.wait(pause)

    def right_angle(self, at, size=0.20, color=GOLD, quadrant=UR):
        x, y, _ = at
        sx = 1 if quadrant[0] >= 0 else -1
        sy = 1 if quadrant[1] >= 0 else -1
        return Polygon(
            P(x, y),
            P(x + sx * size, y),
            P(x + sx * size, y + sy * size),
            P(x, y + sy * size),
            color=color,
            stroke_width=2,
            fill_opacity=0,
        )

    def base_height(self, x1, x2, y_base, y_top, base_label="b", height_label="h"):
        b = BraceBetweenPoints(
            P(x1, y_base - 0.12),
            P(x2, y_base - 0.12),
            DOWN,
            color=CYAN,
        )
        h = BraceBetweenPoints(
            P(x2 + 0.15, y_base),
            P(x2 + 0.15, y_top),
            RIGHT,
            color=GOLD,
        )
        group = VGroup(
            b,
            safe_mathtex(base_label, 36, CYAN).next_to(b, DOWN, buff=0.08),
            h,
            safe_mathtex(height_label, 36, GOLD).next_to(h, RIGHT, buff=0.08),
        )
        self.play(FadeIn(group), run_time=0.75)
        return group

    def dashed_height(self, start, end, label="h", label_side=RIGHT):
        d = DashedLine(start, end, color=GOLD, stroke_width=3)
        lab = safe_mathtex(label, 34, GOLD).next_to(d, label_side, buff=0.10)
        return VGroup(d, lab)

    def pulse(self, mob, color=GOLD, scale_factor=1.03):
        self.play(
            Indicate(mob, color=color, scale_factor=scale_factor),
            run_time=0.9,
        )

    def demo_steps(self):
        return list((self.manifest.get("lesson") or {}).get("steps") or [])

    def demo_header_from_manifest(self):
        presentation = self.manifest.get("presentation") or {}
        self.demo_header(
            str(presentation.get("number", "")),
            self.manifest["title"],
            str(
                presentation.get(
                    "formula",
                    self.manifest.get("result", {}).get("math", ""),
                )
            ),
            str(presentation.get("category", "GEOMETRIA")),
        )

    def render_demo(self):
        render = self.manifest.get("render") or {}
        renderer = str(render.get("native_renderer", ""))

        dispatch = {
            "area_triangle_parallelogram_v1": self.render_demo_area_triangle,
            "area_parallelogram_cut_v1": self.render_demo_area_parallelogram,
            "area_trapezoid_double_v1": self.render_demo_area_trapezoid,
            "area_rhombus_rearrange_v1": self.render_demo_area_rhombus,
            "area_equilateral_height_v1": self.render_demo_area_equilateral,
            "regular_polygon_apothem_v1": self.render_demo_regular_polygon,
            "circumference_roll_pi_v1": self.render_demo_circumference_pi,
            "circle_sector_rearrange_v1": self.render_demo_circle_area,
            "arc_fraction_v1": self.render_demo_arc_length,
            "sector_fraction_v1": self.render_demo_sector_area,
            "annulus_subtraction_v1": self.render_demo_annulus_area,
            "pythagoras_four_triangles_v1": self.render_demo_pythagoras,
            "right_triangle_metric_relations_v1": self.render_demo_metric_relations,
            "trig_similarity_ratios_v1": self.render_demo_trig_similarity,
            "law_of_sines_altitudes_v1": self.render_demo_law_of_sines,
            "law_of_cosines_projection_v1": self.render_demo_law_of_cosines,
            "triangle_area_sine_v1": self.render_demo_triangle_area_sine,
            "scale_dimension_exponents_v1": self.render_demo_scale_dimensions,
            "euler_polyhedra_reduction_v1": self.render_demo_euler_polyhedra,
            "cuboid_space_diagonal_v1": self.render_demo_cuboid_diagonal,
            "prism_net_area_v1": self.render_demo_prism_area_net,
            "prism_volume_layers_v1": self.render_demo_prism_volume,
            "cylinder_lateral_unwrap_v1": self.render_demo_cylinder_area,
            "cylinder_volume_layers_v1": self.render_demo_cylinder_volume,
            "regular_pyramid_net_area_v1": self.render_demo_pyramid_area,
            "pyramid_volume_partition_cavalieri_v1": self.render_demo_pyramid_volume,
            "cone_sector_area_v1": self.render_demo_cone_area,
            "cone_volume_polygon_limit_v1": self.render_demo_cone_volume,
            "sphere_volume_cavalieri_v1": self.render_demo_sphere_volume,
            "sphere_area_bands_v1": self.render_demo_sphere_area,
        }
        handler = dispatch.get(renderer)
        if handler is None:
            raise RuntimeError(f"Renderer demo nativo ainda não portado: {renderer!r}")
        handler()

    def render_demo_area_triangle(self):
        if IS_HORIZONTAL:
            self.render_demo_horizontal()
            return

        presentation = self.manifest.get("presentation") or {}
        captions = presentation.get("captions") or {}
        self.demo_header(
            str(presentation.get("number", "01")),
            self.manifest["title"],
            str(presentation.get("formula", self.manifest.get("result", {}).get("math", ""))),
            str(presentation.get("category", "ÁREAS")),
        )

        tri = polygon_xy([(-2.8, -0.9), (2.2, -0.9), (-0.8, 1.6)])
        self.demo_caption(captions["base_height"])
        self.play(Create(tri), run_time=1.8)

        h = DashedLine(P(-0.8, -0.9), P(-0.8, 1.6), color=GOLD)
        ra = self.right_angle(P(-0.8, -0.9), quadrant=UR)
        labels = VGroup(
            safe_mathtex("b", 36, CYAN).move_to(P(-0.3, -1.35)),
            safe_mathtex("h", 36, GOLD).move_to(P(-1.15, 0.25)),
        )
        self.play(Create(h), Create(ra), Write(labels), run_time=1.2)
        self.wait(1.2)

        self.demo_caption(captions["duplicate"])
        self.demo_hide_intro_formula()
        other = tri.copy().set_color(GOLD)
        self.play(
            FadeOut(h),
            FadeOut(ra),
            FadeOut(labels),
            other.animate.shift(UP * 0.45),
            run_time=0.8,
        )
        self.play(Rotate(other, PI, about_point=other.get_center()), run_time=1.35)
        target = polygon_xy([(-0.8, 1.6), (4.2, 1.6), (2.2, -0.9)], GOLD)
        self.play(
            other.animate.shift(target.get_center() - other.get_center()),
            run_time=1.35,
        )
        group = VGroup(tri, other)
        self.play(group.animate.shift(LEFT * 0.7), run_time=0.65)
        self.wait(0.9)
        self.demo_equation(r"2A=bh")
        self.demo_caption(captions["half"])
        self.demo_equation(r"A=\frac{bh}{2}")
        self.demo_end()

    def render_demo_area_parallelogram(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_paralelogramo nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        whole = polygon_xy([(-3, -1), (1.5, -1), (3, 1.5), (-1.5, 1.5)])
        self.demo_caption(steps[0]["narration"])
        self.play(Create(whole), run_time=1.8)
        cut = DashedLine(P(1.5, -1), P(1.5, 1.5), color=GOLD)
        self.play(Create(cut), run_time=0.9)
        self.wait(0.8)

        self.demo_caption(steps[1]["narration"])
        left = polygon_xy([(-3, -1), (-1.5, -1), (-1.5, 1.5)])
        mid = polygon_xy([(-1.5, -1), (1.5, -1), (1.5, 1.5), (-1.5, 1.5)])
        moving = polygon_xy([(1.5, -1), (3, 1.5), (1.5, 1.5)], GOLD)
        self.remove(whole)
        self.add(left, mid, moving)
        self.play(FadeOut(cut), run_time=0.35)

        self.demo_caption(steps[2]["narration"])
        self.demo_hide_intro_formula()
        self.play(moving.animate.shift(UP * 0.55), run_time=0.55)
        self.play(moving.animate.shift(LEFT * 4.5), run_time=2.2)
        self.play(moving.animate.shift(DOWN * 0.55), run_time=0.55)
        outline = Rectangle(width=4.5, height=2.5, color=WHITE).move_to(P(-0.75, 0.25))
        self.play(Create(outline), run_time=0.8)
        self.base_height(-3, 1.5, -1, 1.5)

        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))
        self.demo_end()

    def render_demo_area_trapezoid(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_trapezio nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        trap = polygon_xy([(-3, -1), (1, -1), (0, 1.3), (-2, 1.3)])
        self.demo_caption(steps[0]["narration"])
        self.play(Create(trap), run_time=1.8)
        labs = VGroup(
            safe_mathtex("B", 36, CYAN).move_to(P(-1, -1.4)),
            safe_mathtex("b", 36, GOLD).move_to(P(-1, 1.68)),
        )
        self.play(Write(labs), run_time=0.8)

        self.demo_caption(steps[1]["narration"])
        self.demo_hide_intro_formula()
        copy = trap.copy().set_color(GOLD)
        self.play(FadeOut(labs), copy.animate.shift(UP * 0.5), run_time=0.75)
        self.play(Rotate(copy, PI, about_point=copy.get_center()), run_time=1.25)
        target = polygon_xy([(4, 1.3), (0, 1.3), (1, -1), (3, -1)], GOLD)
        self.play(copy.animate.shift(target.get_center() - copy.get_center()), run_time=1.35)
        self.play(VGroup(trap, copy).animate.shift(LEFT * 0.5), run_time=0.55)

        brace = BraceBetweenPoints(P(-3.5, -1.15), P(2.5, -1.15), DOWN, color=CYAN)
        blab = safe_mathtex("B+b", 36, CYAN).next_to(brace, DOWN, buff=0.08)
        height = self.dashed_height(P(2.5, -1), P(2.5, 1.3), "h")
        self.play(FadeIn(brace), Write(blab), FadeIn(height), run_time=0.8)

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]))
        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))
        self.demo_end()

    def render_demo_area_rhombus(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_losango nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        pts = [(0, 1.8), (3, 0), (0, -1.8), (-3, 0)]
        whole = polygon_xy(pts)
        self.demo_caption(steps[0]["narration"])
        self.play(Create(whole), run_time=1.8)
        dh = Line(P(-3, 0), P(3, 0), color=CYAN, stroke_width=4)
        dv = Line(P(0, -1.8), P(0, 1.8), color=GOLD, stroke_width=4)
        labs = VGroup(
            safe_mathtex("D", 36, CYAN).move_to(P(0, -0.42)),
            safe_mathtex("d", 36, GOLD).move_to(P(0.38, 0.22)),
        )
        self.play(Create(dh), Create(dv), Write(labs), run_time=1.1)

        self.demo_caption(steps[1]["narration"])
        tris = VGroup(
            polygon_xy([(0, 0), (3, 0), (0, 1.8)], GOLD),
            polygon_xy([(0, 0), (0, 1.8), (-3, 0)], CYAN),
            polygon_xy([(0, 0), (-3, 0), (0, -1.8)], GOLD),
            polygon_xy([(0, 0), (0, -1.8), (3, 0)], CYAN),
        )
        self.remove(whole)
        self.add(*tris, dh, dv, labs)
        self.wait(0.8)

        self.demo_caption(steps[2]["narration"])
        self.demo_hide_intro_formula()
        self.play(FadeOut(dh), FadeOut(dv), FadeOut(labs), run_time=0.4)
        for i, angle, shift in (
            (0, 0, P(-3, -0.9)),
            (2, 0, P(0, 0.9)),
            (1, PI, P(0, 0.9)),
            (3, PI, P(3, -0.9)),
        ):
            self.play(rigid_motion(tris[i], angle, shift), run_time=1.6)

        outline = Rectangle(width=6, height=1.8, color=WHITE)
        b = BraceBetweenPoints(P(-3, -1.05), P(3, -1.05), DOWN, color=CYAN)
        h = BraceBetweenPoints(P(3.15, -0.9), P(3.15, 0.9), RIGHT, color=GOLD)
        dims = VGroup(
            b,
            safe_mathtex("D", 34, CYAN).next_to(b, DOWN, buff=0.08),
            h,
            safe_mathtex(r"\frac d2", 34, GOLD).next_to(h, RIGHT, buff=0.08),
        )
        self.play(Create(outline), FadeIn(dims), run_time=0.85)
        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))
        self.demo_equation(str(steps[4]["math"]))
        self.demo_end()

    def render_demo_area_equilateral(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_triangulo_equilatero nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        length = 4.4
        height_value = np.sqrt(3) * length / 2
        a = P(-length / 2, -1.45)
        b = P(length / 2, -1.45)
        c = P(0, -1.45 + height_value)
        tri = Polygon(
            a,
            b,
            c,
            color=CYAN,
            stroke_width=3,
            fill_color=CYAN,
            fill_opacity=0.22,
        )
        self.demo_caption(steps[0]["narration"])
        self.play(Create(tri), run_time=1.8)
        alt = DashedLine(c, P(0, -1.45), color=GOLD)
        ra = self.right_angle(P(0, -1.45), quadrant=UR)
        labels = VGroup(
            safe_mathtex(r"\ell", 36, CYAN).move_to(P(0, -1.85)),
            safe_mathtex(r"\ell", 36, CYAN).move_to(P(1.7, 0.7)),
            safe_mathtex(r"\frac\ell2", 34, GOLD).move_to(P(-1.28, -1.05)),
            safe_mathtex("h", 34, GOLD).move_to(P(0.32, 0.45)),
        )
        self.play(Create(alt), Create(ra), Write(labels), run_time=1.15)

        self.demo_caption(steps[1]["narration"])
        half = Polygon(
            a,
            P(0, -1.45),
            c,
            color=GOLD,
            stroke_width=3,
            fill_color=GOLD,
            fill_opacity=0.16,
        )
        self.demo_hide_intro_formula()
        self.play(FadeIn(half), run_time=0.6)
        self.demo_equation(str(steps[1]["math"]))

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]))
        self.demo_equation(str(steps[3]["math"]))
        self.demo_equation(str(steps[4]["math"]))

        self.demo_caption(steps[5]["narration"])
        self.demo_equation(str(steps[5]["math"]))
        self.demo_end()

    def render_demo_regular_polygon(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_poligonos_regulares nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        pts = regular_polygon_points(6, 2.3, start_angle=PI / 6)
        sectors = VGroup(
            *[
                Polygon(
                    ORIGIN,
                    pts[i],
                    pts[(i + 1) % 6],
                    color=CYAN if i % 2 else GOLD,
                    fill_opacity=0.22,
                )
                for i in range(6)
            ]
        )
        self.demo_caption(steps[0]["narration"])
        self.play(
            LaggedStart(*[Create(s) for s in sectors], lag_ratio=0.2),
            run_time=3,
        )
        mid = (pts[0] + pts[1]) / 2
        apo = Line(ORIGIN, mid, color=GOLD)
        self.play(
            Create(apo),
            Write(safe_mathtex("a", 34, GOLD).next_to(apo, LEFT)),
            Write(
                safe_mathtex(r"\ell", 34).next_to(
                    Line(pts[0], pts[1]),
                    UP,
                )
            ),
        )
        self.demo_hide_intro_formula()

        self.demo_caption(steps[1]["narration"])
        self.pulse(sectors[0])
        self.demo_equation(str(steps[1]["math"]))

        self.demo_caption(steps[2]["narration"])
        for i, sector in enumerate(sectors):
            self.pulse(sector)
            self.demo_equation(
                str(i + 1) + r"\cdot\frac{\ell a}{2}",
                size=44,
            )

        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))
        self.play(
            LaggedStart(
                *[
                    Create(
                        Line(
                            pts[i],
                            pts[(i + 1) % 6],
                            color=GREEN,
                            stroke_width=6,
                        )
                    )
                    for i in range(6)
                ],
                lag_ratio=0.2,
            ),
            run_time=2,
        )
        self.demo_caption(steps[4]["narration"])
        self.demo_equation(str(steps[4]["math"]))
        self.demo_end()

    def render_demo_circumference_pi(self):
        if IS_HORIZONTAL:
            raise RuntimeError(
                "comprimento_circunferencia_pi nativo ainda é somente vertical."
            )

        steps = self.demo_steps()
        self.demo_header_from_manifest()
        self.demo_hide_intro_formula()

        start = P(-PI, -1)
        wheel = Circle(radius=1, color=CYAN).move_to(start + UP)
        spoke = Line(start + UP, start, color=GOLD, stroke_width=5)
        floor = Line(
            start + LEFT * 0.2,
            start + RIGHT * (TAU + 0.2),
            color=MUTED,
        )
        self.demo_caption(steps[0]["narration"])
        self.play(Create(wheel), Create(spoke), Create(floor), run_time=2)

        diameter = Line(start + P(-1, 1), start + P(1, 1), color=GOLD)
        dlabel = safe_mathtex("d=2r", 30, GOLD).next_to(diameter, UP)
        self.play(Create(diameter), Write(dlabel))
        self.wait(2)
        self.play(FadeOut(diameter), FadeOut(dlabel))

        tracker = ValueTracker(0)
        wheel.add_updater(
            lambda m: m.move_to(start + P(tracker.get_value(), 1))
        )
        spoke.add_updater(
            lambda m: m.put_start_and_end_on(
                start + P(tracker.get_value(), 1),
                start
                + P(
                    tracker.get_value() - np.sin(tracker.get_value()),
                    1 - np.cos(tracker.get_value()),
                ),
            )
        )
        trail = always_redraw(
            lambda: Line(
                start,
                start + RIGHT * max(0.001, tracker.get_value()),
                color=CYAN,
                stroke_width=6,
            )
        )
        self.add(trail)
        self.play(
            tracker.animate.set_value(TAU),
            run_time=7,
            rate_func=linear,
        )
        for mob in (wheel, spoke, trail):
            mob.clear_updaters()

        self.demo_caption(steps[1]["narration"])
        self.play(FadeOut(wheel), FadeOut(spoke))

        self.demo_caption(steps[2]["narration"])
        for i in range(3):
            unit = Line(
                start + P(2 * i, 0.7),
                start + P(2 * i + 2, 0.7),
                color=GOLD,
                stroke_width=6,
            )
            self.play(
                Create(unit),
                Write(safe_mathtex("d", 32, GOLD).next_to(unit, UP)),
                run_time=1,
            )
        self.play(
            Create(
                Line(
                    start + P(6, 0.7),
                    start + P(TAU, 0.7),
                    color=PINK,
                    stroke_width=6,
                )
            )
        )
        self.demo_equation(str(steps[2]["math"]))

        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))
        self.demo_caption(steps[4]["narration"])
        self.demo_equation(str(steps[4]["math"]))
        self.demo_end()

    def render_demo_circle_area(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_circulo nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()
        self.demo_hide_intro_formula()

        radius = 1.65
        sectors = None
        for n in (8, 16, 32):
            if sectors is not None:
                self.play(FadeOut(sectors))
            alpha = TAU / n
            sectors = VGroup(
                *[
                    Sector(
                        radius=radius,
                        angle=alpha,
                        start_angle=i * alpha,
                        color=CYAN if i % 2 == 0 else GOLD,
                        fill_opacity=0.35,
                        stroke_width=1,
                    )
                    for i in range(n)
                ]
            )
            self.demo_caption(f"Divida o círculo em {n} setores iguais.")
            self.play(
                LaggedStart(
                    *[Create(s) for s in sectors],
                    lag_ratio=0.04,
                ),
                run_time=2,
            )
            self.demo_caption(steps[0]["narration"])
            chord = 2 * radius * np.sin(alpha / 2)
            self.play(
                *[
                    rigid_motion(
                        sector,
                        (
                            PI / 2 - alpha / 2
                            if i % 2 == 0
                            else -PI / 2 - alpha / 2
                        )
                        - i * alpha,
                        P(
                            (i // 2) * chord
                            + (chord / 2 if i % 2 else 0)
                            - ((n / 2 - 0.5) * chord) / 2,
                            -0.8 + (radius * np.cos(alpha / 2) if i % 2 else 0),
                        ),
                    )
                    for i, sector in enumerate(sectors)
                ],
                run_time=5,
            )
            self.demo_caption(steps[1]["narration"])

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]), size=44)
        self.demo_equation(str(steps[3]["math"]))
        self.demo_end()

    def render_demo_arc_length(self):
        if IS_HORIZONTAL:
            raise RuntimeError("comprimento_arco nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        radius = 2.3
        theta = 120 * DEGREES
        circle = Circle(radius, color=MUTED, stroke_width=2)
        arc = Arc(
            radius=radius,
            start_angle=0,
            angle=theta,
            color=CYAN,
            stroke_width=7,
        )
        radii = VGroup(
            Line(P(0, 0), P(radius, 0), color=GOLD),
            Line(
                P(0, 0),
                P(radius * np.cos(theta), radius * np.sin(theta)),
                color=GOLD,
            ),
        )
        angle = Arc(
            radius=0.65,
            start_angle=0,
            angle=theta,
            color=GOLD,
            stroke_width=4,
        )
        self.demo_caption(steps[0]["narration"])
        self.play(
            Create(circle),
            Create(radii),
            Create(arc),
            Create(angle),
            run_time=1.8,
        )
        self.play(
            Write(
                safe_mathtex(r"\theta", 34, GOLD).move_to(P(0.55, 0.48))
            ),
            run_time=0.45,
        )
        self.demo_hide_intro_formula()

        self.demo_caption(steps[1]["narration"])
        copies = VGroup(
            *[
                arc.copy()
                .rotate(i * theta, about_point=ORIGIN)
                .set_color(GOLD)
                for i in (1, 2)
            ]
        )
        self.play(
            LaggedStart(*[Create(s) for s in copies], lag_ratio=0.5),
            run_time=2,
        )
        self.demo_equation(str(steps[1]["math"]))
        self.play(FadeOut(copies))

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]))
        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))
        self.demo_caption(steps[4]["narration"])
        self.demo_equation(str(steps[4]["math"]))
        self.demo_end()

    def render_demo_sector_area(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_setor_circular nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        radius = 2.4
        theta = 120 * DEGREES
        circle = Circle(radius, color=MUTED, stroke_width=2)
        sector = Sector(
            radius=radius,
            angle=theta,
            start_angle=0,
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.32,
            stroke_width=4,
        )
        angle = Arc(
            radius=0.7,
            start_angle=0,
            angle=theta,
            color=GOLD,
            stroke_width=4,
        )
        self.demo_caption(steps[0]["narration"])
        self.play(
            Create(circle),
            FadeIn(sector),
            Create(angle),
            run_time=1.7,
        )
        self.play(
            Write(
                safe_mathtex(r"\theta", 34, GOLD).move_to(P(0.6, 0.5))
            ),
            run_time=0.45,
        )
        self.demo_hide_intro_formula()

        self.demo_caption(steps[1]["narration"])
        copies = VGroup(
            *[
                sector.copy()
                .rotate(i * theta, about_point=ORIGIN)
                .set_color(GOLD)
                for i in (1, 2)
            ]
        )
        self.play(
            LaggedStart(*[FadeIn(s) for s in copies], lag_ratio=0.5),
            run_time=2,
        )
        self.demo_equation(str(steps[1]["math"]))
        self.play(FadeOut(copies))

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]))
        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))
        self.demo_caption(steps[4]["narration"])
        self.demo_equation(str(steps[4]["math"]), size=40)
        self.demo_end()

    def render_demo_annulus_area(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_coroa_circular nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        outer = Circle(
            2.55,
            color=CYAN,
            stroke_width=4,
            fill_color=CYAN,
            fill_opacity=0.20,
        )
        inner = Circle(
            1.35,
            color=GOLD,
            stroke_width=4,
            fill_color=BG,
            fill_opacity=1,
        )
        self.demo_caption(steps[0]["narration"])
        self.play(Create(outer), run_time=1.0)
        self.play(Create(inner), run_time=0.9)

        r_outer = Line(P(0, 0), P(2.55, 0), color=CYAN, stroke_width=3)
        r_inner = Line(
            P(0, 0),
            P(
                1.35 * np.cos(140 * DEGREES),
                1.35 * np.sin(140 * DEGREES),
            ),
            color=GOLD,
            stroke_width=3,
        )
        labs = VGroup(
            safe_mathtex("R", 34, CYAN).next_to(r_outer, DOWN, buff=0.08),
            safe_mathtex("r", 34, GOLD).next_to(r_inner, LEFT, buff=0.08),
        )
        self.play(
            Create(r_outer),
            Create(r_inner),
            Write(labs),
            run_time=0.8,
        )
        self.demo_hide_intro_formula()

        self.demo_caption(steps[1]["narration"])
        self.demo_equation(str(steps[1]["math"]))
        self.play(Indicate(inner, color=RED), run_time=0.8)
        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]))
        self.demo_end()

    def render_demo_pythagoras(self):
        if IS_HORIZONTAL:
            raise RuntimeError("teorema_pitagoras nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        a, b = 2.0, 3.0
        side = a + b
        outer = Square(side_length=side, color=WHITE).move_to(P(0, 0.2))
        x0, y0 = -side / 2, -side / 2 + 0.2

        t1 = Polygon(
            P(x0, y0),
            P(x0 + b, y0),
            P(x0, y0 + a),
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.25,
        )
        center_point = P(0, 0.2)
        t2 = t1.copy().rotate(PI / 2, about_point=center_point)
        t3 = t1.copy().rotate(PI, about_point=center_point)
        t4 = t1.copy().rotate(3 * PI / 2, about_point=center_point)
        tris = VGroup(t1, t2, t3, t4)

        self.demo_caption(steps[0]["narration"])
        self.play(
            Create(outer),
            LaggedStart(*[FadeIn(t) for t in tris], lag_ratio=0.12),
            run_time=1.7,
        )
        self.demo_hide_intro_formula()
        side_labels = VGroup(
            safe_mathtex("b", 32, CYAN).next_to(
                Line(P(x0, y0), P(x0 + b, y0)),
                DOWN,
            ),
            safe_mathtex("a", 32, GOLD).next_to(
                Line(P(x0 + b, y0), P(x0 + side, y0)),
                DOWN,
            ),
        )
        self.play(Write(side_labels))
        self.demo_equation(str(steps[0]["math"]))

        self.demo_caption(steps[1]["narration"])
        center = Polygon(
            P(x0 + b, y0),
            P(x0 + side, y0 + b),
            P(x0 + a, y0 + side),
            P(x0, y0 + a),
            color=GOLD,
            fill_color=GOLD,
            fill_opacity=0.20,
            stroke_width=4,
        )
        self.play(Create(center), run_time=0.9)

        self.demo_caption(steps[2]["narration"])
        self.play(
            Write(
                safe_mathtex("c", 32, GOLD).next_to(
                    Line(P(x0 + b, y0), P(x0 + side, y0 + b)),
                    LEFT,
                )
            )
        )

        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))
        self.demo_caption(steps[4]["narration"])
        self.demo_equation(str(steps[4]["math"]))
        self.demo_end()

    def render_demo_metric_relations(self):
        if IS_HORIZONTAL:
            raise RuntimeError(
                "relacoes_metricas_triangulo_retangulo nativo ainda é somente vertical."
            )

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        A = P(-3, -1.0)
        B = P(3, -1.0)
        C = P(-0.6, -1 + np.sqrt(2.4 * 3.6))
        H = P(-0.6, -1.0)
        tri = Polygon(
            A,
            B,
            C,
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.12,
            stroke_width=3,
        )
        alt = DashedLine(C, H, color=GOLD, stroke_width=3)

        self.demo_caption(steps[0]["narration"])
        self.play(Create(tri), Create(alt), run_time=1.6)

        labels = VGroup(
            safe_mathtex("h", 32, GOLD).next_to(alt, RIGHT, buff=0.08),
            safe_mathtex("m", 32, CYAN).move_to(P(-1.8, -1.42)),
            safe_mathtex("n", 32, CYAN).move_to(P(1.2, -1.42)),
            safe_mathtex("c", 32, WHITE).move_to(P(0, -1.72)),
            safe_mathtex("a", 32, GREEN).move_to((B + C) / 2 + P(0.3, 0.15)),
            safe_mathtex("b", 32, GOLD).move_to((A + C) / 2 + P(-0.3, 0.15)),
        )
        self.play(Write(labels), run_time=0.8)
        self.demo_hide_intro_formula()

        left = Polygon(
            A,
            H,
            C,
            color=GOLD,
            fill_color=GOLD,
            fill_opacity=0.16,
            stroke_width=3,
        )
        right = Polygon(
            H,
            B,
            C,
            color=GREEN,
            fill_color=GREEN,
            fill_opacity=0.13,
            stroke_width=3,
        )
        self.play(FadeIn(left), FadeIn(right), run_time=0.7)
        angles = VGroup(
            Angle(Line(A, H), Line(A, C), radius=0.45, color=PINK),
            Angle(Line(C, H), Line(C, B), radius=0.45, color=PINK),
        )
        self.play(Create(angles), Create(self.right_angle(H, quadrant=UR)))

        self.demo_caption(steps[1]["narration"])
        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]))
        self.demo_equation(str(steps[3]["math"]))

        self.demo_caption(steps[4]["narration"])
        self.pulse(right)
        self.demo_equation(str(steps[4]["math"]))
        self.demo_equation(str(steps[5]["math"]))
        self.pulse(left)
        self.demo_equation(str(steps[6]["math"]))
        self.demo_equation(str(steps[7]["math"]))
        self.demo_equation(str(steps[8]["math"]))
        self.demo_end()

    def render_demo_trig_similarity(self):
        if IS_HORIZONTAL:
            raise RuntimeError(
                "razoes_trigonometricas_semelhanca nativo ainda é somente vertical."
            )

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        theta = 32 * DEGREES
        A = P(-3, -1.5)
        B = P(-0.4, -1.5)
        C = P(-0.4, -1.5 + 2.6 * np.tan(theta))
        A2 = P(-3, -1.5)
        B2 = P(2.5, -1.5)
        C2 = P(2.5, -1.5 + 5.5 * np.tan(theta))
        small = Polygon(
            A,
            B,
            C,
            color=GOLD,
            fill_color=GOLD,
            fill_opacity=0.16,
            stroke_width=3,
        )
        large = Polygon(
            A2,
            B2,
            C2,
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.10,
            stroke_width=3,
        )

        self.demo_caption(steps[0]["narration"])
        self.play(Create(small), run_time=1.0)
        self.play(TransformFromCopy(small, large), run_time=1.2)
        arc = Arc(
            radius=0.65,
            start_angle=0,
            angle=theta,
            arc_center=A,
            color=WHITE,
            stroke_width=3,
        )
        self.play(
            Create(arc),
            Write(
                safe_mathtex(r"\theta", 30, WHITE).next_to(
                    arc,
                    RIGHT,
                    buff=0.05,
                )
            ),
            run_time=0.6,
        )
        self.demo_hide_intro_formula()

        sides = VGroup(
            safe_mathtex("op", 30, CYAN).next_to(Line(B2, C2), RIGHT),
            safe_mathtex("adj", 30, CYAN).next_to(Line(A2, B2), DOWN),
            safe_mathtex("hip", 30, GOLD).next_to(Line(A2, C2), UP),
        )
        self.play(Write(sides))

        self.demo_caption(steps[1]["narration"])
        self.demo_equation(str(steps[1]["math"]))
        self.demo_equation(str(steps[2]["math"]))

        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))
        self.demo_equation(str(steps[4]["math"]))
        self.demo_end()

    def render_demo_law_of_sines(self):
        if IS_HORIZONTAL:
            raise RuntimeError("lei_senos nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        A = P(-3, -1.2)
        B = P(3, -1.2)
        C = P(0.8, 2.0)
        H = P(0.8, -1.2)
        tri = Polygon(
            A,
            B,
            C,
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.12,
            stroke_width=3,
        )
        alt = DashedLine(C, H, color=GOLD, stroke_width=3)

        self.demo_caption(steps[0]["narration"])
        self.play(Create(tri), Create(alt), run_time=1.6)
        labs = VGroup(
            safe_mathtex("A", 30, WHITE).next_to(A, LEFT, buff=0.08),
            safe_mathtex("B", 30, WHITE).next_to(B, RIGHT, buff=0.08),
            safe_mathtex("C", 30, WHITE).next_to(C, UP, buff=0.08),
            safe_mathtex("c", 32, CYAN).move_to(P(0, -1.65)),
            safe_mathtex("a", 32, CYAN).move_to((B + C) / 2 + P(0.25, 0.15)),
            safe_mathtex("b", 32, CYAN).move_to((A + C) / 2 + P(-0.25, 0.15)),
            safe_mathtex("h", 32, GOLD).next_to(alt, RIGHT, buff=0.08),
        )
        self.play(Write(labs), run_time=0.8)
        self.demo_hide_intro_formula()

        self.demo_caption(steps[1]["narration"])
        self.demo_equation(str(steps[1]["math"]))
        self.demo_equation(str(steps[2]["math"]))

        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))
        self.demo_equation(str(steps[4]["math"]))

        self.demo_caption(steps[5]["narration"])
        K = A + np.dot(B - A, C - A) / np.dot(C - A, C - A) * (C - A)
        second = DashedLine(B, K, color=GREEN)
        self.play(FadeOut(alt), FadeOut(labs[-1]), Create(second))
        self.demo_equation(str(steps[5]["math"]))
        self.demo_equation(str(steps[6]["math"]))
        self.demo_equation(str(steps[7]["math"]))
        self.demo_end()

    def render_demo_law_of_cosines(self):
        if IS_HORIZONTAL:
            raise RuntimeError("lei_cossenos nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        A = P(-3, -1.2)
        B = P(3, -1.2)
        C = P(0.8, 2.0)
        H = P(0.8, -1.2)
        tri = Polygon(
            A, B, C,
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.12,
            stroke_width=3,
        )
        alt = DashedLine(C, H, color=GOLD, stroke_width=3)

        self.demo_caption(steps[0]["narration"])
        self.play(Create(tri), Create(alt), run_time=1.5)
        labs = VGroup(
            safe_mathtex("a", 32, CYAN).move_to((B + C) / 2 + P(0.25, 0.18)),
            safe_mathtex("b", 32, CYAN).move_to((A + C) / 2 + P(-0.25, 0.18)),
            safe_mathtex("c", 32, CYAN).move_to(P(0, -2.15)),
            safe_mathtex("A", 30, WHITE).next_to(A, UP + RIGHT, buff=0.12),
        )
        self.play(Write(labs), run_time=0.8)
        self.demo_hide_intro_formula()

        self.demo_caption(steps[1]["narration"])
        proj = Line(A, H, color=GOLD, stroke_width=5)
        self.play(
            Create(proj),
            Write(
                safe_mathtex(r"b\cos A", 30, GOLD).next_to(
                    proj, DOWN, buff=0.08
                )
            ),
            run_time=0.8,
        )
        self.play(
            Write(
                safe_mathtex(r"b\sin A", 28, GOLD).next_to(alt, RIGHT)
            )
        )

        self.demo_caption(steps[2]["narration"])
        self.pulse(Line(H, B, color=GREEN))
        self.demo_equation(str(steps[2]["math"]), size=42)

        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))

        self.demo_caption(steps[4]["narration"])
        self.demo_equation(str(steps[4]["math"]))
        self.demo_equation(str(steps[5]["math"]))
        self.demo_end()

    def render_demo_triangle_area_sine(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_triangulo_seno nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        A = P(-3, -1.2)
        B = P(3, -1.2)
        C = P(0.7, 2.0)
        H = P(0.7, -1.2)
        tri = Polygon(
            A, B, C,
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.15,
            stroke_width=3,
        )
        alt = DashedLine(C, H, color=GOLD, stroke_width=3)

        self.demo_caption(steps[0]["narration"])
        self.play(Create(tri), Create(alt), run_time=1.5)
        labs = VGroup(
            safe_mathtex("b", 32, CYAN).move_to((A + C) / 2 + P(-0.25, 0.2)),
            safe_mathtex("c", 32, CYAN).move_to(P(0, -1.55)),
            safe_mathtex("h", 32, GOLD).next_to(alt, RIGHT, buff=0.08),
            safe_mathtex("A", 30, WHITE).next_to(A, UP + RIGHT, buff=0.1),
        )
        self.play(Write(labs), run_time=0.8)
        self.demo_hide_intro_formula()
        self.demo_equation(str(steps[0]["math"]))

        self.demo_caption(steps[1]["narration"])
        half = Polygon(
            A, H, C,
            color=GOLD,
            fill_opacity=0.18,
        )
        self.play(FadeIn(half))
        self.demo_equation(str(steps[1]["math"]))

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]))
        self.demo_equation(str(steps[3]["math"]))
        self.demo_end()

    def render_demo_scale_dimensions(self):
        if IS_HORIZONTAL:
            raise RuntimeError(
                "escalas_comprimentos_areas_volumes nativo ainda é somente vertical."
            )

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        s1 = Square(
            1.5,
            color=GOLD,
            fill_color=GOLD,
            fill_opacity=0.18,
        ).move_to(P(-2.2, 0.5))
        s2 = Square(
            3.0,
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.14,
        ).move_to(P(1.4, 0.5))

        self.demo_caption(steps[0]["narration"])
        self.play(Create(s1), run_time=0.8)
        self.play(TransformFromCopy(s1, s2), run_time=1.1)
        labels = VGroup(
            safe_mathtex("L", 30, GOLD).next_to(s1, DOWN),
            safe_mathtex("2L", 30, CYAN).next_to(s2, DOWN),
        )
        self.play(Write(labels), run_time=0.6)
        self.demo_hide_intro_formula()

        self.demo_caption(steps[1]["narration"])
        grid = VGroup(
            Line(P(1.4, -1.0), P(1.4, 2.0), color=MUTED, stroke_width=1.5),
            Line(P(-0.1, 0.5), P(2.9, 0.5), color=MUTED, stroke_width=1.5),
        )
        self.play(Create(grid), run_time=0.7)
        self.demo_equation(str(steps[1]["math"]))

        self.demo_caption(steps[2]["narration"])
        front = Square(1.5, color=GOLD).move_to(P(-1.8, 0.2))
        back = front.copy().shift(P(0.55, 0.55))
        edges = VGroup(
            *[
                Line(front.get_vertices()[i], back.get_vertices()[i], color=GOLD)
                for i in range(4)
            ]
        )
        cube = VGroup(front, back, edges).scale(0.85).move_to(P(0, 0.15))
        self.play(
            FadeOut(s1),
            FadeOut(s2),
            FadeOut(grid),
            FadeIn(cube),
            run_time=0.8,
        )
        self.play(FadeOut(labels), FadeOut(cube))

        self.demo_caption(steps[3]["narration"])
        cubes = VGroup()
        for z in (1, 0):
            for y in (0, 1):
                for x in (0, 1):
                    f = Square(
                        0.9,
                        color=GOLD,
                        fill_opacity=0.12,
                    ).move_to(
                        P(
                            x * 0.9 - 0.8 + z * 0.35,
                            y * 0.9 - 0.5 + z * 0.35,
                        )
                    )
                    back_face = f.copy().shift(P(0.35, 0.35))
                    e = VGroup(
                        *[
                            Line(
                                f.get_vertices()[i],
                                back_face.get_vertices()[i],
                                color=GOLD,
                            )
                            for i in range(4)
                        ]
                    )
                    cubes.add(VGroup(f, back_face, e))
        self.play(
            LaggedStart(*[Create(c) for c in cubes], lag_ratio=0.25),
            run_time=4,
        )
        self.demo_equation(str(steps[3]["math"]))
        self.demo_equation(str(steps[4]["math"]))

        self.demo_caption(steps[5]["narration"])
        self.demo_equation(str(steps[5]["math"]))
        self.demo_end()

    def render_demo_euler_polyhedra(self):
        if IS_HORIZONTAL:
            raise RuntimeError("relacao_euler_poliedros nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()
        self.demo_hide_intro_formula()

        self.demo_caption(steps[0]["narration"])
        verts = [
            P(-2.5, -2),
            P(2.5, -2),
            P(2.5, 2),
            P(-2.5, 2),
            P(-1, -0.8),
            P(1, -0.8),
            P(1, 0.8),
            P(-1, 0.8),
        ]
        pairs = (
            [(i, (i + 1) % 4) for i in range(4)]
            + [(i + 4, (i + 1) % 4 + 4) for i in range(4)]
            + [(i, i + 4) for i in range(4)]
        )
        lines = [Line(verts[a], verts[b], color=CYAN) for a, b in pairs]
        dots = VGroup(*[Dot(p, color=GOLD) for p in verts])
        self.play(
            LaggedStart(*[Create(line) for line in lines], lag_ratio=0.1),
            FadeIn(dots),
            run_time=3,
        )
        self.demo_equation(str(steps[0]["math"]), size=40)

        self.demo_caption(steps[1]["narration"])
        for idx, remaining in zip((4, 5, 6, 7, 0), (4, 3, 2, 1, 0)):
            self.play(FadeOut(lines[idx]), run_time=1)
            self.demo_equation(rf"8-{7 + remaining}+{remaining}=1")

        self.demo_caption(steps[2]["narration"])
        for vertex, edge in (
            (4, 8),
            (7, 11),
            (0, 3),
            (3, 2),
            (6, 10),
            (2, 1),
            (5, 9),
        ):
            self.play(
                FadeOut(dots[vertex]),
                FadeOut(lines[edge]),
                run_time=0.8,
            )
        self.demo_equation(str(steps[2]["math"]))

        self.demo_caption(steps[3]["narration"])
        self.demo_caption(steps[4]["narration"])
        self.demo_caption(steps[5]["narration"])
        self.demo_equation(str(steps[5]["math"]))
        self.demo_end()

    def render_demo_cuboid_diagonal(self):
        if IS_HORIZONTAL:
            raise RuntimeError(
                "diagonal_paralelepipedo nativo ainda é somente vertical."
            )

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        A = P(-2.6, -1.5)
        B = P(1.8, -1.5)
        C = P(1.8, 0.9)
        D = P(-2.6, 0.9)
        shift = P(1.1, 0.9)
        A2, B2, C2, D2 = A + shift, B + shift, C + shift, D + shift

        front = Polygon(A, B, C, D, color=CYAN, fill_opacity=0)
        back = Polygon(A2, B2, C2, D2, color=GOLD, fill_opacity=0)
        edges = VGroup(
            Line(A, A2),
            Line(B, B2),
            Line(C, C2),
            Line(D, D2),
        ).set_color(WHITE)

        self.demo_caption(steps[0]["narration"])
        self.play(Create(front), Create(back), Create(edges), run_time=1.5)
        db = Line(A, B2, color=GREEN, stroke_width=5)
        self.play(Create(db), run_time=0.7)
        ground = Polygon(A, B, B2, color=GREEN, fill_opacity=0.15)
        self.play(FadeIn(ground))
        self.play(
            Write(
                VGroup(
                    safe_mathtex("a", 30, CYAN).next_to(Line(A, B), DOWN),
                    safe_mathtex("b", 30, CYAN).next_to(Line(B, B2), RIGHT),
                    safe_mathtex("c", 30, GOLD).next_to(Line(B2, C2), RIGHT),
                )
            )
        )
        self.demo_hide_intro_formula()
        self.demo_equation(str(steps[0]["math"]))

        self.demo_caption(steps[1]["narration"])
        space = Line(A, C2, color=GOLD, stroke_width=6)
        self.play(Create(space), run_time=0.9)
        upright = Polygon(A, B2, C2, color=GOLD, fill_opacity=0.18)
        self.play(FadeOut(ground), FadeIn(upright))
        self.demo_equation(str(steps[1]["math"]))

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]))
        self.demo_equation(str(steps[3]["math"]))
        self.demo_end()

    def render_demo_prism_area_net(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_prismas_planificacao nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()
        self.demo_hide_intro_formula()

        side = 0.9
        height = 1.5
        self.demo_caption(steps[0]["narration"])

        p3 = [
            np.array(
                [
                    side * np.cos(i * TAU / 6),
                    side * np.sin(i * TAU / 6),
                    0,
                ]
            )
            for i in range(6)
        ]

        def project(point):
            return P(
                1.4 * point[0] + 0.5 * point[1],
                0.3 * point[1] + point[2] - 0.7,
            )

        faces = VGroup(
            *[
                Polygon(
                    project(p3[i]),
                    project(p3[(i + 1) % 6]),
                    project(p3[(i + 1) % 6] + [0, 0, height]),
                    project(p3[i] + [0, 0, height]),
                    color=CYAN if i % 2 else GOLD,
                    fill_opacity=0.18,
                )
                for i in range(6)
            ]
        )
        self.play(
            LaggedStart(*[Create(face) for face in faces], lag_ratio=0.15),
            run_time=3,
        )

        self.demo_caption(steps[1]["narration"])
        targets = [
            Rectangle(
                width=side,
                height=height,
                color=CYAN if i % 2 else GOLD,
                fill_opacity=0.18,
            ).move_to(P(-2.7 + side * (i + 0.5), 0))
            for i in range(6)
        ]
        for face, target in zip(faces, targets):
            self.play(Transform(face, target), run_time=0.8)

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]), size=40)
        self.base_height(
            -2.7,
            2.7,
            -height / 2,
            height / 2,
            "P_b",
            "h",
        )

        self.demo_caption(steps[3]["narration"])
        bases = VGroup(
            *[
                Polygon(
                    *regular_polygon_points(6, side, center=P(x, 2)),
                    color=GOLD,
                    fill_opacity=0.25,
                )
                for x in (-1.5, 1.5)
            ]
        )
        self.play(
            LaggedStart(*[Create(base) for base in bases], lag_ratio=0.5),
            run_time=2,
        )
        self.demo_equation(str(steps[3]["math"]))
        self.demo_equation(str(steps[4]["math"]))
        self.demo_end()

    def render_demo_prism_volume(self):
        if IS_HORIZONTAL:
            raise RuntimeError("volume_prismas nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        base = Polygon(
            *regular_polygon_points(
                6,
                1.8,
                center=P(0, -1.4),
                start_angle=PI / 6,
            ),
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.18,
        )
        base.stretch(0.3, 1, about_point=P(0, -1.4))

        self.demo_caption(steps[0]["narration"])
        self.play(Create(base), run_time=1.0)

        layers = VGroup(base)
        for i in range(1, 8):
            layer = (
                base.copy()
                .shift(UP * 0.42 * i)
                .set_opacity(0.18 + 0.04 * i)
            )
            layers.add(layer)
        self.play(
            LaggedStart(
                *[
                    TransformFromCopy(base, layers[i])
                    for i in range(1, 8)
                ],
                lag_ratio=0.08,
            ),
            run_time=1.5,
        )
        self.demo_hide_intro_formula()

        self.demo_caption(steps[1]["narration"])
        self.demo_equation(str(steps[1]["math"]))

        hbrace = BraceBetweenPoints(
            P(2.2, -1.4),
            P(2.2, 1.54),
            RIGHT,
            color=GOLD,
        )
        self.play(
            FadeIn(hbrace),
            Write(
                safe_mathtex("h", 34, GOLD).next_to(
                    hbrace, RIGHT, buff=0.08
                )
            ),
            run_time=0.7,
        )

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]), size=42)
        self.demo_equation(str(steps[3]["math"]))
        self.demo_end()

    def render_demo_cylinder_area(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_cilindro nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()
        self.demo_hide_intro_formula()

        radius = 0.9
        height = 1.8
        n = 32

        def point(theta, z):
            return P(
                radius * np.cos(theta),
                0.3 * radius * np.sin(theta) + z,
            )

        strips = VGroup(
            *[
                Polygon(
                    point(i * TAU / n, -height / 2),
                    point((i + 1) * TAU / n, -height / 2),
                    point((i + 1) * TAU / n, height / 2),
                    point(i * TAU / n, height / 2),
                    color=CYAN,
                    fill_opacity=0.15,
                    stroke_width=1,
                )
                for i in range(n)
            ]
        )

        self.demo_caption(steps[0]["narration"])
        self.play(Create(strips), run_time=2)

        self.demo_caption(steps[1]["narration"])
        targets = [
            Rectangle(
                width=TAU * radius / n,
                height=height,
                color=CYAN,
                fill_opacity=0.15,
                stroke_width=1,
            ).move_to(
                P(
                    -PI * radius + (i + 0.5) * TAU * radius / n,
                    0,
                )
            )
            for i in range(n)
        ]
        self.play(
            *[
                Transform(strip, target)
                for strip, target in zip(strips, targets)
            ],
            run_time=4,
        )

        self.demo_caption(steps[2]["narration"])
        self.base_height(
            -PI * radius,
            PI * radius,
            -height / 2,
            height / 2,
            r"2\pi r",
            "h",
        )
        self.demo_equation(str(steps[2]["math"]))

        self.demo_caption(steps[3]["narration"])
        caps = VGroup(
            *[
                Circle(
                    radius=radius,
                    color=GOLD,
                    fill_opacity=0.2,
                ).move_to(P(x, 2.1))
                for x in (-1.6, 1.6)
            ]
        )
        self.play(
            LaggedStart(*[Create(cap) for cap in caps], lag_ratio=0.5),
            run_time=2,
        )
        self.demo_equation(str(steps[3]["math"]))
        self.demo_equation(str(steps[4]["math"]))
        self.demo_end()

    def render_demo_cylinder_volume(self):
        if IS_HORIZONTAL:
            raise RuntimeError("volume_cilindro nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        base = Ellipse(
            width=4.6,
            height=1.25,
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.16,
        ).move_to(P(0, -1.45))

        self.demo_caption(steps[0]["narration"])
        self.play(Create(base), run_time=0.9)

        disks = VGroup(base)
        for i in range(1, 9):
            disk = base.copy().shift(UP * 0.36 * i)
            disks.add(disk)
        self.play(
            LaggedStart(
                *[
                    TransformFromCopy(base, disks[i])
                    for i in range(1, 9)
                ],
                lag_ratio=0.07,
            ),
            run_time=1.5,
        )

        side_left = Line(
            P(-2.3, -1.45),
            P(-2.3, 1.43),
            color=WHITE,
            stroke_width=2,
        )
        side_right = Line(
            P(2.3, -1.45),
            P(2.3, 1.43),
            color=WHITE,
            stroke_width=2,
        )
        self.play(
            Create(side_left),
            Create(side_right),
            run_time=0.55,
        )
        self.demo_hide_intro_formula()

        self.demo_caption(steps[1]["narration"])
        self.demo_equation(str(steps[1]["math"]))

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]), size=42)
        self.demo_equation(str(steps[3]["math"]))
        self.demo_equation(str(steps[4]["math"]))
        self.demo_end()

    def render_demo_pyramid_area(self):
        if IS_HORIZONTAL:
            raise RuntimeError(
                "area_piramides_regulares nativo ainda é somente vertical."
            )

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        base = Polygon(
            P(-2.3, -1.3),
            P(1.8, -1.3),
            P(2.6, -0.45),
            P(-1.5, -0.45),
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.13,
        )
        apex = P(0.3, 2.15)
        edges = VGroup(
            *[
                Line(apex, vertex, color=GOLD, stroke_width=3)
                for vertex in base.get_vertices()
            ]
        )

        self.demo_caption(steps[0]["narration"])
        self.play(Create(base), Create(edges), run_time=1.5)
        self.demo_hide_intro_formula()

        self.demo_caption(steps[1]["narration"])
        n = 4
        side = 1.35
        y = -0.75
        geratrix = 2.0
        faces = VGroup()
        for i in range(n):
            x = -2.9 + i * side
            color = GOLD if i % 2 == 0 else CYAN
            faces.add(
                Polygon(
                    P(x, y),
                    P(x + side, y),
                    P(x + side / 2, y + geratrix),
                    color=color,
                    fill_color=color,
                    fill_opacity=0.16,
                    stroke_width=2,
                )
            )
        self.play(
            FadeOut(VGroup(base, edges)),
            LaggedStart(*[FadeIn(face) for face in faces], lag_ratio=0.08),
            run_time=1.2,
        )

        baseline = Line(
            P(-2.9, y),
            P(-2.9 + n * side, y),
            color=CYAN,
            stroke_width=4,
        )
        height_line = DashedLine(
            P(-2.9 + side / 2, y),
            P(-2.9 + side / 2, y + geratrix),
            color=GOLD,
        )
        self.play(Create(baseline), Create(height_line), run_time=0.7)
        self.play(
            Write(
                safe_mathtex("g", 30, GOLD).next_to(
                    height_line, RIGHT
                )
            ),
            Write(
                safe_mathtex(r"P_b=n\ell", 30, CYAN).next_to(
                    baseline, DOWN
                )
            ),
        )

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]))
        self.demo_equation(str(steps[3]["math"]))

        self.demo_caption(steps[4]["narration"])
        self.demo_equation(str(steps[4]["math"]))
        self.demo_end()

    def render_demo_pyramid_volume(self):
        if IS_HORIZONTAL:
            raise RuntimeError("volume_piramide nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        front = Square(3.3, color=WHITE).move_to(P(-0.55, -0.35))
        back = front.copy().shift(P(1.0, 0.8))
        connectors = VGroup(
            *[
                Line(
                    front.get_vertices()[i],
                    back.get_vertices()[i],
                    color=WHITE,
                    stroke_width=2,
                )
                for i in range(4)
            ]
        )

        self.demo_caption(steps[0]["narration"])
        self.play(
            Create(front),
            Create(back),
            Create(connectors),
            run_time=1.4,
        )

        origin = front.get_vertices()[0]
        p1 = Polygon(
            back.get_vertices()[0],
            back.get_vertices()[1],
            back.get_vertices()[2],
            back.get_vertices()[3],
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.15,
        )
        p2 = Polygon(
            front.get_vertices()[1],
            front.get_vertices()[2],
            back.get_vertices()[2],
            back.get_vertices()[1],
            color=GOLD,
            fill_color=GOLD,
            fill_opacity=0.14,
        )
        p3 = Polygon(
            front.get_vertices()[3],
            front.get_vertices()[2],
            back.get_vertices()[2],
            back.get_vertices()[3],
            color=GREEN,
            fill_color=GREEN,
            fill_opacity=0.13,
        )
        self.play(FadeIn(p1), FadeIn(p2), FadeIn(p3), run_time=0.8)

        rays = VGroup(
            *[
                Line(origin, vertex, color=GOLD, stroke_width=2)
                for vertex in (
                    front.get_vertices()[2],
                    back.get_vertices()[1],
                    back.get_vertices()[2],
                    back.get_vertices()[3],
                )
            ]
        )
        self.play(Create(rays), FadeIn(Dot(origin, color=RED)), run_time=2)

        self.demo_caption(steps[1]["narration"])
        for face in (p1, p2, p3):
            self.pulse(face)

        self.demo_hide_intro_formula()
        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]))
        self.demo_equation(str(steps[3]["math"]))

        self.demo_caption(steps[4]["narration"])
        self.demo_equation(str(steps[4]["math"]))

        self.demo_caption(steps[5]["narration"])
        self.demo_caption(steps[6]["narration"])
        self.demo_caption(steps[7]["narration"])
        self.demo_equation(str(steps[7]["math"]))
        self.demo_caption(steps[8]["narration"])
        self.demo_equation(str(steps[8]["math"]))
        self.demo_caption(steps[9]["narration"])
        self.demo_equation(str(steps[9]["math"]))
        self.demo_end()

    def render_demo_cone_area(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_cone nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        radius_value = 1.7
        geratrix = 2.55
        base = Ellipse(
            width=2 * radius_value,
            height=0.8,
            color=CYAN,
        ).move_to(P(0, -1.2))
        apex = P(
            0,
            -1.2 + np.sqrt(geratrix * geratrix - radius_value * radius_value),
        )
        sides = VGroup(
            Line(apex, P(-radius_value, -1.2), color=CYAN),
            Line(apex, P(radius_value, -1.2), color=CYAN),
        )

        self.demo_caption(steps[0]["narration"])
        self.play(Create(base), Create(sides), run_time=1.4)
        self.demo_hide_intro_formula()

        sector = Sector(
            radius=2.55,
            angle=240 * DEGREES,
            start_angle=-30 * DEGREES,
            color=CYAN,
            fill_color=CYAN,
            fill_opacity=0.18,
            stroke_width=3,
        ).shift(UP * 0.15)
        self.play(
            FadeOut(VGroup(base, sides)),
            FadeIn(sector),
            run_time=0.9,
        )

        radius_line = Line(
            P(0, 0.15),
            P(
                2.55 * np.cos(-PI / 6),
                0.15 + 2.55 * np.sin(-PI / 6),
            ),
            color=GOLD,
            stroke_width=3,
        )
        self.play(
            Create(radius_line),
            Write(
                safe_mathtex("g", 34, GOLD).next_to(
                    radius_line, UP, buff=0.08
                )
            ),
            run_time=0.65,
        )

        self.demo_caption(steps[1]["narration"])
        self.demo_equation(str(steps[1]["math"]))
        arc = Arc(
            radius=2.55,
            start_angle=-PI / 6,
            angle=4 * PI / 3,
            arc_center=P(0, 0.15),
            color=GOLD,
            stroke_width=6,
        )
        self.play(Create(arc))
        self.demo_equation(str(steps[2]["math"]), size=42)

        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))

        self.demo_caption(steps[4]["narration"])
        self.demo_equation(str(steps[4]["math"]))
        self.demo_end()

    def render_demo_cone_volume(self):
        if IS_HORIZONTAL:
            raise RuntimeError("volume_cone nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()

        self.demo_caption(steps[0]["narration"])
        shapes = VGroup()
        centers = [P(-2.5, -0.6), P(0, -0.6), P(2.5, -0.6)]
        sides_counts = [4, 6, 14]

        for center, sides_count in zip(centers, sides_counts):
            points = regular_polygon_points(
                sides_count,
                0.95,
                center=center,
                start_angle=PI / 2,
            )
            points = [
                center + (vertex - center) * np.array([1, 0.3, 1])
                for vertex in points
            ]
            base = Polygon(
                *points,
                color=CYAN,
                fill_color=CYAN,
                fill_opacity=0.12,
                stroke_width=2,
            )
            apex = center + UP * 2.25
            edges = VGroup(
                *[
                    Line(apex, vertex, color=GOLD, stroke_width=1.7)
                    for vertex in points
                ]
            )
            shapes.add(VGroup(base, edges))

        self.play(
            LaggedStart(*[FadeIn(shape) for shape in shapes], lag_ratio=0.18),
            run_time=1.6,
        )
        self.demo_hide_intro_formula()

        self.demo_caption(steps[1]["narration"])
        self.demo_equation(str(steps[1]["math"]))

        self.demo_caption(steps[2]["narration"])
        circle = Ellipse(
            width=1.9,
            height=0.57,
            color=GREEN,
            stroke_width=4,
        ).move_to(centers[-1])
        self.play(Create(circle), run_time=0.7)
        self.demo_equation(str(steps[2]["math"]))

        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]))
        self.demo_end()

    def render_demo_sphere_volume(self):
        if IS_HORIZONTAL:
            raise RuntimeError("volume_esfera nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()
        self.demo_hide_intro_formula()

        radius_value = 1.4
        left = P(-2, -0.8)
        right = P(2, -0.8)

        hemisphere = VGroup(
            Arc(
                radius=radius_value,
                start_angle=0,
                angle=PI,
                arc_center=left,
                color=CYAN,
            ),
            Line(
                left + LEFT * radius_value,
                left + RIGHT * radius_value,
                color=CYAN,
            ),
        )
        cylinder = Rectangle(
            width=2 * radius_value,
            height=radius_value,
            color=GOLD,
        ).move_to(right + UP * radius_value / 2)
        cone = Polygon(
            right,
            right + P(-radius_value, radius_value),
            right + P(radius_value, radius_value),
            color=RED,
            fill_opacity=0.18,
        )

        self.demo_caption(steps[0]["narration"])
        self.play(
            Create(hemisphere),
            Create(cylinder),
            Create(cone),
            run_time=2,
        )

        self.demo_caption(steps[1]["narration"])
        tracker = ValueTracker(0.55)
        section = always_redraw(
            lambda: VGroup(
                Line(
                    left
                    + P(
                        -np.sqrt(
                            radius_value * radius_value
                            - tracker.get_value() ** 2
                        ),
                        tracker.get_value(),
                    ),
                    left
                    + P(
                        np.sqrt(
                            radius_value * radius_value
                            - tracker.get_value() ** 2
                        ),
                        tracker.get_value(),
                    ),
                    color=CYAN,
                    stroke_width=7,
                ),
                Line(
                    right + P(-radius_value, tracker.get_value()),
                    right + P(-tracker.get_value(), tracker.get_value()),
                    color=CYAN,
                    stroke_width=7,
                ),
                Line(
                    right + P(tracker.get_value(), tracker.get_value()),
                    right + P(radius_value, tracker.get_value()),
                    color=CYAN,
                    stroke_width=7,
                ),
            )
        )
        self.add(section)
        self.demo_equation(str(steps[1]["math"]))

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]))
        self.demo_equation(str(steps[3]["math"]))
        self.play(tracker.animate.set_value(1.25), run_time=3)
        self.play(tracker.animate.set_value(0.2), run_time=3)
        section.clear_updaters()

        self.demo_caption(steps[4]["narration"])
        self.demo_equation(str(steps[4]["math"]), size=40)
        self.demo_equation(str(steps[5]["math"]))

        self.demo_caption(steps[6]["narration"])
        self.demo_equation(str(steps[6]["math"]))
        self.demo_end()

    def render_demo_sphere_area(self):
        if IS_HORIZONTAL:
            raise RuntimeError("area_esfera nativo ainda é somente vertical.")

        steps = self.demo_steps()
        self.demo_header_from_manifest()
        self.demo_hide_intro_formula()

        radius_value = 2
        circle = Circle(radius=radius_value, color=CYAN)
        self.demo_caption(steps[0]["narration"])
        self.play(Create(circle), run_time=2)

        theta = PI / 6
        point_q = P(
            radius_value * np.cos(theta),
            radius_value * np.sin(theta),
        )
        radius_line = Line(ORIGIN, point_q, color=GOLD)
        rho_line = Line(P(0, point_q[1]), point_q, color=GREEN)
        point_a = point_q + P(
            0.45 * np.sin(theta),
            -0.45 * np.cos(theta),
        )
        point_b = point_q + P(
            -0.45 * np.sin(theta),
            0.45 * np.cos(theta),
        )
        tangent = Line(
            point_a,
            point_b,
            color=PINK,
            stroke_width=6,
        )
        labels = VGroup(
            safe_mathtex("R", 30, GOLD).next_to(radius_line, DOWN),
            safe_mathtex(r"\rho", 30, GREEN).next_to(rho_line, UP),
            safe_mathtex(r"\Delta s", 30, PINK).next_to(tangent, RIGHT),
        )
        self.play(
            Create(radius_line),
            Create(rho_line),
            Create(tangent),
            Write(labels),
        )
        self.demo_equation(str(steps[0]["math"]))

        self.demo_caption(steps[1]["narration"])
        point_c = P(point_a[0], point_b[1])
        aux = VGroup(
            DashedLine(point_a, point_c, color=WHITE),
            DashedLine(point_c, point_b, color=WHITE),
        )
        dh_label = safe_mathtex(
            r"\Delta h", 25, WHITE
        ).next_to(Line(point_a, point_c), RIGHT, buff=0.5)
        self.play(Create(aux))
        self.play(Write(dh_label))

        self.demo_caption(steps[2]["narration"])
        self.demo_equation(str(steps[2]["math"]))

        self.demo_caption(steps[3]["narration"])
        self.demo_equation(str(steps[3]["math"]), size=40)

        self.demo_caption(steps[4]["narration"])
        self.play(
            FadeOut(
                VGroup(
                    radius_line,
                    rho_line,
                    tangent,
                    labels,
                    aux,
                    dh_label,
                )
            )
        )
        bands = VGroup(
            *[
                Line(P(-2, y), P(2, y), color=GOLD, stroke_width=2)
                for y in np.linspace(-2, 2, 17)
            ]
        )
        self.play(Create(bands), run_time=2)

        self.demo_caption(steps[5]["narration"])
        self.demo_equation(str(steps[5]["math"]))
        self.demo_equation(str(steps[6]["math"]))
        self.demo_end()

    def render_demo_horizontal(self):
        """16:9 adaptation of the approved motion-math visual language.

        This is a new layout, not a legacy-parity target: the visual proof and
        timing language are preserved while the composition uses two columns.
        """
        presentation = self.manifest.get("presentation") or {}
        captions = presentation.get("captions") or {}
        formula = str(
            presentation.get(
                "formula",
                self.manifest.get("result", {}).get("math", ""),
            )
        )
        signature = str(presentation.get("signature", "MIQUÉIAS AMORIM"))

        brand = self.demo_text(
            "MATEMÁTICA EM MOVIMENTO", 16, MUTED, max_width=5.5
        ).move_to(P(-5.35, 3.95))
        counter = self.demo_text(
            f'{presentation.get("number", "01")}  /  {presentation.get("category", "ÁREAS")}',
            18,
            CYAN,
            max_width=5.0,
        ).move_to(P(5.35, 3.95))
        title = self.demo_text(
            self.manifest["title"], 36, WHITE, max_width=9.5, weight=BOLD
        ).move_to(P(0, 3.22))
        intro_formula = safe_mathtex(
            formula, 44, WHITE, max_width=5.0
        ).move_to(P(0, 2.35))
        signature_mob = self.demo_text(
            signature, 14, MUTED, max_width=4.0
        ).move_to(P(5.65, -4.05))
        divider = Line(
            P(0.35, -3.25),
            P(0.35, 1.85),
            color="#24324E",
            stroke_width=2,
        )

        self.add(brand)
        self.play(FadeIn(counter, shift=UP * 0.12), run_time=0.55)
        self.play(Write(title), run_time=1.0)
        self.play(Write(intro_formula), run_time=1.25)
        self.add(signature_mob)
        self.wait(0.55)

        caption_mob = VGroup()
        equation_mob = VGroup()

        def show_caption(text):
            nonlocal caption_mob
            new = self.demo_text(
                textwrap.fill(str(text), width=48),
                25,
                WHITE,
                max_width=6.2,
            ).move_to(P(4.15, 0.95))
            if len(caption_mob) > 0:
                self.play(
                    FadeOut(caption_mob),
                    FadeIn(new, shift=UP * 0.10),
                    run_time=0.42,
                )
            else:
                self.play(FadeIn(new, shift=UP * 0.10), run_time=0.42)
            caption_mob = new
            self.wait(max(1.4, len(str(text).split()) / 3.0))

        def show_equation(tex):
            nonlocal equation_mob
            new = safe_mathtex(
                tex, 50, WHITE, max_width=5.8
            ).move_to(P(4.15, -1.0))
            if len(equation_mob) > 0:
                self.play(
                    ReplacementTransform(equation_mob, new),
                    run_time=1.05,
                )
            else:
                self.play(Write(new), run_time=0.95)
            equation_mob = new
            self.wait(2.0)

        shift = LEFT * 3.4
        tri = polygon_xy(
            [(-2.8, -0.9), (2.2, -0.9), (-0.8, 1.6)]
        ).shift(shift)

        show_caption(captions["base_height"])
        self.play(FadeIn(divider), FadeOut(intro_formula), run_time=0.45)
        self.play(Create(tri), run_time=1.8)

        h = DashedLine(
            P(-0.8, -0.9) + shift,
            P(-0.8, 1.6) + shift,
            color=GOLD,
        )
        ra = self.right_angle(P(-0.8, -0.9) + shift, quadrant=UR)
        labels = VGroup(
            safe_mathtex("b", 36, CYAN).move_to(P(-0.3, -1.35) + shift),
            safe_mathtex("h", 36, GOLD).move_to(P(-1.15, 0.25) + shift),
        )
        self.play(Create(h), Create(ra), Write(labels), run_time=1.2)
        self.wait(1.2)

        show_caption(captions["duplicate"])
        other = tri.copy().set_color(GOLD)
        self.play(
            FadeOut(h),
            FadeOut(ra),
            FadeOut(labels),
            other.animate.shift(UP * 0.45),
            run_time=0.8,
        )
        self.play(Rotate(other, PI, about_point=other.get_center()), run_time=1.35)
        target = polygon_xy(
            [(-0.8, 1.6), (4.2, 1.6), (2.2, -0.9)],
            GOLD,
        ).shift(shift)
        self.play(
            other.animate.shift(target.get_center() - other.get_center()),
            run_time=1.35,
        )
        group = VGroup(tri, other)
        self.play(group.animate.shift(LEFT * 0.7), run_time=0.65)
        self.wait(0.9)

        show_equation(r"2A=bh")
        show_caption(captions["half"])
        show_equation(r"A=\frac{bh}{2}")
        self.play(
            Indicate(equation_mob, color=CYAN, scale_factor=1.04),
            run_time=1.0,
        )
        self.wait(2.4)

    # ------------------------------------------------------------------
    # ENEM profile: port of ENEMSolutionScene, driven only by manifest
    # ------------------------------------------------------------------

    def segment_duration(self, key, default=2.5):
        rec = self.narr.get(key, {})
        raw = rec.get("duration", rec.get("estimated_seconds", default))
        try:
            d = float(raw)
        except (TypeError, ValueError):
            d = float(default)
        return max(0.35, d * (0.16 if FAST_PREVIEW else 1.0))

    def audio_path(self, key):
        rec = self.narr.get(key, {})
        rel = rec.get("audio")
        if not rel:
            return None
        path = (PROJECT_ROOT / str(rel)).resolve()
        return path if path.exists() else None

    def speak(self, key, animations=None, run_time=None):
        duration = self.segment_duration(key)
        audio = self.audio_path(key)
        if audio and not FAST_PREVIEW:
            self.add_sound(str(audio))
        if animations:
            rt = min(duration * 0.52, 3.8) if run_time is None else min(float(run_time), duration)
            rt = max(0.25, rt)
            self.play(*animations, run_time=rt)
            if duration > rt:
                self.wait(duration - rt)
        else:
            self.wait(duration)
        return duration

    def render_qenem(self):
        self.q = self.manifest["question"]
        self.exam = self.manifest["exam"]
        self.solution = self.manifest["solution"]
        self.visuals = self.manifest.get("visuals") or {}

        self.source_screen()
        self.statement_screen()
        if self.visuals.get("statement"):
            self.figure_screen()
        self.options_screen()
        self.data_screen()
        self.goal_screen()
        self.visual_screen()
        self.solution_screen()

    def source_screen(self):
        tag = enem_txt("QUESTÃO COMENTADA", 20, CYAN, weight=BOLD).move_to(
            P(0, _lv(5.8, 2.9))
        )
        code = enem_txt(
            f'{self.exam["canonical_id"]} — Q{self.exam["question_number"]}',
            _lv(34, 38),
            WHITE,
            weight=BOLD,
        )
        src = enem_txt(
            f'Fonte: {self.exam["name"]} {self.exam["year"]} · {self.exam.get("booklet", "")}',
            21,
            MUTED,
        )
        group = VGroup(code, src).arrange(DOWN, buff=0.35).move_to(P(0, _lv(0.3, 0)))
        self.speak(
            "source",
            [FadeIn(tag, shift=DOWN * 0.15), Write(code), FadeIn(src)],
        )
        self.play(FadeOut(VGroup(tag, group)), run_time=0.45)

    def statement_screen(self):
        heading = enem_txt("1 · LEIA O PROBLEMA", 20, CYAN, weight=BOLD).move_to(
            P(0, _lv(6.7, 3.65))
        )
        self.add(heading)
        segs = [v for k, v in sorted(self.narr.items()) if k.startswith("statement_")]
        for i, seg in enumerate(segs, 1):
            card = RoundedRectangle(
                width=_lv(7.7, 14.2),
                height=_lv(10.7, 5.6),
                corner_radius=0.18,
                color="#24324E",
                fill_color="#111A30",
                fill_opacity=1,
            )
            body = enem_txt(
                seg["text"],
                _lv(24, 23),
                WHITE,
                width=_lv(51, 92),
            )
            fit(body, _lv(7.1, 13.2), _lv(9.4, 4.45))
            body.move_to(card)
            page_no = enem_txt(f"{i}/{len(segs)}", 16, MUTED).move_to(
                P(0, _lv(-5.25, -2.55))
            )
            group = VGroup(card, body, page_no)
            self.speak(seg["key"], [FadeIn(group, shift=UP * 0.12)])
            self.play(FadeOut(group), run_time=0.35)
        self.play(FadeOut(heading), run_time=0.25)

    def figure_screen(self):
        h = enem_txt("2 · FIGURA DA QUESTÃO", 20, CYAN, weight=BOLD).move_to(
            P(0, _lv(6.7, 3.65))
        )
        sub = enem_txt("reconstrução vetorial esquemática", 16, MUTED).next_to(
            h, DOWN, buff=0.12
        )
        spec = self.visuals["statement"]
        fig = source_figure(str(spec["renderer"]))
        note = enem_txt(
            str(spec.get("description", "")),
            _lv(18, 19),
            MUTED,
            width=_lv(52, 46),
        )
        if IS_HORIZONTAL:
            fit(fig, 8.0, 5.25)
            fig.move_to(P(-3.25, -0.15))
            fit(note, 5.15, 4.5)
            note.move_to(P(4.35, -0.1))
        else:
            fit(fig, 7.2, 9.0)
            fig.move_to(P(0, 0.3))
            fit(note, 7.2, 2.2)
            note.move_to(P(0, -5.1))
        children = list(fig) if len(fig) > 0 else [fig]
        anim = [
            FadeIn(VGroup(h, sub)),
            LaggedStart(
                *[
                    Create(x) if isinstance(x, VMobject) else FadeIn(x)
                    for x in children
                ],
                lag_ratio=0.09,
            ),
            FadeIn(note),
        ]
        self.speak("figure", anim)
        self.play(FadeOut(VGroup(h, sub, fig, note)), run_time=0.4)

    def options_screen(self):
        h = enem_txt("3 · ALTERNATIVAS", 20, CYAN, weight=BOLD).move_to(
            P(0, _lv(6.7, 3.65))
        )
        self.add(h)
        option_lines = [
            f"{letter}) {value}" for letter, value in self.q.get("options", {}).items()
        ]
        body = enem_txt(
            "\n".join(option_lines),
            _lv(22, 21),
            WHITE,
            width=_lv(51, 90),
        )
        fit(body, _lv(7.1, 13.1), _lv(10.2, 4.75))
        body.move_to(P(0, 0))
        box = RoundedRectangle(
            width=_lv(7.7, 14.2),
            height=_lv(10.9, 5.6),
            corner_radius=0.18,
            color="#24324E",
            fill_color="#111A30",
            fill_opacity=1,
        )
        self.speak("options", [FadeIn(box), FadeIn(body, shift=UP * 0.1)])
        self.play(FadeOut(VGroup(h, box, body)), run_time=0.35)

    def data_screen(self):
        h = enem_txt("4 · SEPARE OS DADOS", 20, CYAN, weight=BOLD).move_to(
            P(0, _lv(6.7, 3.65))
        )
        self.add(h)
        items = []
        for datum in self.solution.get("data", []):
            if IS_HORIZONTAL:
                t = enem_txt(datum, 22, WHITE, width=44)
                fit(t, 6.05, 1.6)
                box = RoundedRectangle(
                    width=6.55,
                    height=max(0.8, t.height + 0.35),
                    corner_radius=0.13,
                    color="#334568",
                    fill_color="#111A30",
                    fill_opacity=1,
                )
            else:
                t = enem_txt(datum, 24, WHITE, width=38)
                box = RoundedRectangle(
                    width=7.5,
                    height=max(0.8, t.height + 0.35),
                    corner_radius=0.13,
                    color="#334568",
                    fill_color="#111A30",
                    fill_opacity=1,
                )
            t.move_to(box)
            items.append(VGroup(box, t))
        if IS_HORIZONTAL:
            rows = VGroup()
            for i in range(0, len(items), 2):
                rows.add(VGroup(*items[i : i + 2]).arrange(RIGHT, buff=0.32))
            cards = rows.arrange(DOWN, buff=0.25).move_to(P(0, -0.05))
            fit(cards, 13.7, 5.35)
        else:
            cards = VGroup(*items).arrange(DOWN, buff=0.2).move_to(P(0, 0.4))
            fit(cards, 7.6, 10.8)
        self.speak(
            "data",
            [
                LaggedStart(
                    *[FadeIn(c, shift=RIGHT * 0.2) for c in items],
                    lag_ratio=0.22,
                )
            ],
        )
        self.play(FadeOut(VGroup(h, cards)), run_time=0.35)

    def goal_screen(self):
        h = enem_txt("5 · ESTRATÉGIA", 20, CYAN, weight=BOLD).move_to(
            P(0, _lv(6.7, 3.65))
        )
        self.add(h)
        goal_text = str(self.solution.get("goal", ""))
        hook_text = str(self.solution.get("hook", ""))
        plan = self.solution.get("strategy") or []

        if IS_HORIZONTAL:
            goal = enem_txt(goal_text, 27, GOLD, width=40, weight=BOLD)
            fit(goal, 6.25, 1.55)
            hook = enem_txt(hook_text, 20, MUTED, width=42)
            fit(hook, 6.25, 1.8)
            left = VGroup(goal, hook).arrange(
                DOWN, aligned_edge=LEFT, buff=0.55
            ).move_to(P(-3.65, 0.2))
            chain = VGroup(
                *[
                    enem_txt(f"{i}. {item}", 21, WHITE, width=43)
                    for i, item in enumerate(plan, 1)
                ]
            )
            chain.arrange(DOWN, aligned_edge=LEFT, buff=0.38).move_to(P(3.55, -0.05))
            fit(chain, 6.35, 5.25)
            divider = Line(
                P(0, -2.7), P(0, 2.55), color="#24324E", stroke_width=2
            )
            self.speak(
                "strategy",
                [
                    Write(goal),
                    FadeIn(hook),
                    Create(divider),
                    LaggedStart(
                        *[FadeIn(x, shift=UP * 0.12) for x in chain],
                        lag_ratio=0.3,
                    ),
                ],
            )
            self.play(FadeOut(VGroup(h, left, chain, divider)), run_time=0.4)
        else:
            goal = enem_txt(goal_text, 29, GOLD, width=42, weight=BOLD).move_to(
                P(0, 4.5)
            )
            hook = enem_txt(hook_text, 22, MUTED, width=47).move_to(P(0, 2.7))
            chain = VGroup(
                *[
                    enem_txt(f"{i}. {item}", 23, WHITE, width=43)
                    for i, item in enumerate(plan, 1)
                ]
            )
            chain.arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to(P(0, -0.5))
            fit(chain, 7.4, 6.8)
            self.speak(
                "strategy",
                [
                    Write(goal),
                    FadeIn(hook),
                    LaggedStart(
                        *[FadeIn(x, shift=UP * 0.12) for x in chain],
                        lag_ratio=0.3,
                    ),
                ],
            )
            self.play(FadeOut(VGroup(h, goal, hook, chain)), run_time=0.4)

    def visual_screen(self):
        h = enem_txt("6 · MODELE VISUALMENTE", 20, CYAN, weight=BOLD).move_to(
            P(0, _lv(6.7, 3.65))
        )
        self.add(h)
        spec = self.visuals.get("concept") or {}
        diagram = concept_diagram(str(spec.get("renderer", "generic")))
        note = enem_txt(
            str(spec.get("note", "")),
            _lv(22, 20),
            MUTED,
            width=_lv(46, 45),
        )
        if IS_HORIZONTAL:
            diagram.move_to(P(-3.3, -0.05))
            fit(diagram, 8.0, 5.25)
            fit(note, 5.2, 4.6)
            note.move_to(P(4.3, -0.05))
        else:
            diagram.move_to(P(0, 0.5))
            fit(diagram, 7.2, 9.2)
            note.move_to(P(0, -5.15))
        children = list(diagram) if len(diagram) > 0 else [diagram]
        self.speak(
            "visual",
            [
                LaggedStart(
                    *[
                        Create(x) if isinstance(x, VMobject) else FadeIn(x)
                        for x in children
                    ],
                    lag_ratio=0.10,
                ),
                FadeIn(note),
            ],
        )
        if not FAST_PREVIEW and len(diagram) > 0:
            self.play(
                Indicate(diagram[0], color=GOLD, scale_factor=1.04),
                run_time=0.65,
            )
        self.play(FadeOut(VGroup(h, diagram, note)), run_time=0.35)

    def solution_screen(self):
        h = enem_txt("7 · RESOLVA PASSO A PASSO", 20, CYAN, weight=BOLD).move_to(
            P(0, _lv(6.7, 3.65))
        )
        self.add(h)
        current = None
        for i, step in enumerate(self.solution.get("steps", []), 1):
            label = enem_txt(
                str(step.get("label", "")),
                _lv(22, 21),
                GOLD,
                width=_lv(44, 72),
            ).move_to(P(0, _lv(4.9, 2.55)))
            size = step.get("font_size")
            equation = mt(
                str(step.get("math", "")),
                int(size) if size else _lv(45, 43),
            ).move_to(P(0, _lv(0.2, 0.1)))
            if current is None:
                anim = [FadeIn(label), Write(equation)]
            else:
                anim = [
                    FadeOut(current[0]),
                    FadeIn(label),
                    ReplacementTransform(current[1], equation),
                ]
            self.speak(f"step_{i:02d}", anim)
            current = (label, equation)

        answer_letter = str(
            self.solution.get("final_answer", self.q.get("answer", ""))
        )
        option = self.q.get("options", {}).get(answer_letter, "")
        answer = enem_txt(
            f"Alternativa {answer_letter}: {option}",
            _lv(30, 27),
            GREEN,
            width=_lv(42, 76),
            weight=BOLD,
        ).move_to(P(0, _lv(-4.5, -2.55)))
        check = SurroundingRectangle(answer, color=GREEN, buff=0.22)
        self.speak("answer", [FadeIn(answer), Create(check)])
