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


def polygon_xy(points, color=CYAN, fill_opacity=0.22, stroke_width=3):
    return Polygon(
        *[P(x, y) for x, y in points],
        color=color,
        stroke_width=stroke_width,
        fill_color=color,
        fill_opacity=fill_opacity,
    )


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

    def render_demo(self):
        render = self.manifest.get("render") or {}
        renderer = str(render.get("native_renderer", ""))
        if renderer != "area_triangle_parallelogram_v1":
            raise RuntimeError(f"Renderer demo nativo ainda não portado: {renderer!r}")

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
