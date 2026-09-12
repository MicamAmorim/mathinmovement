from __future__ import annotations

import os
import textwrap
from pathlib import Path

from manim import (
    DOWN,
    GREEN,
    LEFT,
    RIGHT,
    UP,
    Create,
    FadeIn,
    FadeOut,
    MathTex,
    Rectangle,
    RoundedRectangle,
    Scene,
    Text,
    VGroup,
    Write,
    config,
)

from ..config import PROJECT_ROOT
from ..registry import Registry
from ..visuals import build_visual, run_demo_action

BG = "#0B1020"
WHITE = "#EEF2FF"
CYAN = "#55D6CF"
GOLD = "#FFCC78"
MUTED = "#9CAAC5"
GREEN_C = "#8DE2A7"
PINK = "#F28DB2"

VIDEO_FORMAT = os.getenv("MIM_FORMAT", "vertical").strip().lower()
if VIDEO_FORMAT not in {"vertical", "horizontal"}:
    VIDEO_FORMAT = "vertical"
HORIZONTAL = VIDEO_FORMAT == "horizontal"
FAST = os.getenv("MIM_FAST_PREVIEW", "0").lower() in {"1", "true", "yes"}

config.frame_width = 16 if HORIZONTAL else 9
config.frame_height = 9 if HORIZONTAL else 16
config.background_color = BG


def _fit(mob, width: float, height: float | None = None):
    if mob.width > width:
        mob.scale_to_fit_width(width)
    if height is not None and mob.height > height:
        mob.scale_to_fit_height(height)
    return mob


def _txt(value: str, size: int = 28, color: str = WHITE, wrap: int | None = None, bold: bool = False):
    if wrap:
        value = "\n".join(textwrap.fill(p, wrap) for p in str(value).splitlines())
    mob = Text(value, font_size=size, color=color, weight="BOLD" if bold else "NORMAL", line_spacing=0.9)
    return mob


def _math(value: str, size: int = 44, color: str = WHITE):
    return MathTex(value, font_size=size, color=color)


class UnifiedContentScene(Scene):
    """Scene declarativa compartilhada por demos e questões ENEM."""

    def construct(self):
        content_id = os.getenv("MIM_CONTENT_ID")
        if not content_id:
            raise RuntimeError("MIM_CONTENT_ID não foi definido pelo renderer.")
        self.record = Registry().rebuild().get(content_id)
        self.manifest = self.record.manifest
        self.narration = {
            str(segment["key"]): segment
            for segment in (self.manifest.get("narration") or {}).get("segments", [])
            if isinstance(segment, dict) and segment.get("key")
        }
        if self.record.type == "qenem":
            self.render_qenem()
        elif self.record.type == "demo":
            self.render_demo()
        else:
            raise RuntimeError(f"Tipo não suportado: {self.record.type}")

    # ------------------------- timing/audio -------------------------

    def segment_duration(self, key: str, default: float = 2.5) -> float:
        segment = self.narration.get(key) or {}
        value = segment.get("duration", segment.get("estimated_seconds", default))
        try:
            duration = float(value)
        except (TypeError, ValueError):
            duration = default
        if FAST:
            duration *= 0.12
        return max(0.35, duration)

    def speak(self, key: str, animations=None, default: float = 2.5):
        duration = self.segment_duration(key, default)
        segment = self.narration.get(key) or {}
        audio = segment.get("audio")
        if audio and not FAST:
            path = (PROJECT_ROOT / str(audio)).resolve()
            if path.exists():
                self.add_sound(str(path))
        if animations:
            run_time = min(duration * 0.5, 3.2)
            run_time = max(0.3, run_time)
            self.play(*animations, run_time=run_time)
            if duration > run_time:
                self.wait(duration - run_time)
        else:
            self.wait(duration)

    def pause_for_step(self, words: int = 10):
        duration = max(0.8, min(3.0, words / 4.5))
        self.wait(0.35 if FAST else duration)

    # ------------------------- shared layout -------------------------

    def clear_screen(self, run_time: float = 0.45):
        if not self.mobjects:
            return
        self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=0.15 if FAST else run_time)

    def heading(self, text: str):
        y = 3.65 if HORIZONTAL else 6.75
        size = 28 if HORIZONTAL else 24
        mob = _txt(text, size=size, color=CYAN, bold=True).move_to([0, y, 0])
        return mob

    # ------------------------- demo -------------------------

    def render_demo(self):
        lesson = self.manifest["lesson"]
        result = self.manifest["result"]

        title_y = 3.2 if HORIZONTAL else 6.0
        formula_y = 2.1 if HORIZONTAL else 4.4
        title = _txt(self.manifest["title"], 42 if HORIZONTAL else 38, WHITE, bold=True).move_to([0, title_y, 0])
        final_math = result.get("math")
        intro_formula = _math(final_math, 46 if HORIZONTAL else 42, GOLD).move_to([0, formula_y, 0]) if final_math else None
        animations = [Write(title)]
        if intro_formula:
            animations.append(Write(intro_formula))
        self.play(*animations, run_time=1.2)
        self.wait(0.5 if FAST else 1.0)

        if intro_formula:
            self.play(FadeOut(intro_formula), run_time=0.4)
        self.play(title.animate.scale(0.65).to_edge(UP, buff=0.35), run_time=0.5)

        caption = None
        state = {}
        for step in lesson.get("steps", []):
            narration = str(step.get("narration", "")).strip()
            if caption is not None:
                self.play(FadeOut(caption), run_time=0.25)
            caption = _txt(
                narration,
                size=25 if HORIZONTAL else 24,
                color=WHITE,
                wrap=70 if HORIZONTAL else 42,
            )
            if HORIZONTAL:
                caption.move_to([4.6, 0.4, 0])
                _fit(caption, 6.0, 5.3)
            else:
                caption.move_to([0, -5.6, 0])
                _fit(caption, 7.2, 2.4)
            self.play(FadeIn(caption), run_time=0.35)

            run_demo_action(self, state, step, horizontal=HORIZONTAL)

            math = step.get("math")
            if math:
                equation = _math(str(math), 46 if HORIZONTAL else 42, GOLD)
                if HORIZONTAL:
                    equation.move_to([4.6, -2.15, 0])
                    _fit(equation, 6.0, 1.5)
                else:
                    equation.move_to([0, -3.9, 0])
                    _fit(equation, 7.2, 1.5)
                previous = state.get("equation")
                if previous is not None:
                    self.play(FadeOut(previous), run_time=0.25)
                self.play(Write(equation), run_time=0.7)
                state["equation"] = equation

            self.pause_for_step(max(8, len(narration.split())))

        if caption is not None:
            self.play(FadeOut(caption), run_time=0.3)

        final = _math(final_math, 54 if HORIZONTAL else 48, GREEN_C) if final_math else _txt(result.get("text", ""), 36, GREEN_C)
        if HORIZONTAL:
            final.move_to([4.6, 0.0, 0])
        else:
            final.move_to([0, -5.0, 0])
        _fit(final, 6.2 if HORIZONTAL else 7.2, 2.0)
        self.play(Write(final), run_time=0.9)
        self.wait(0.5 if FAST else 1.8)

    # ------------------------- qenem -------------------------

    def render_qenem(self):
        self.q_source()
        self.q_statement()
        visuals = self.manifest.get("visuals") or {}
        if visuals.get("statement"):
            self.q_figure()
        self.q_options()
        self.q_data()
        self.q_strategy()
        if visuals.get("concept"):
            self.q_concept()
        self.q_solution()
        self.q_answer()

    def q_source(self):
        exam = self.manifest["exam"]
        tag = _txt("QUESTÃO COMENTADA", 22, CYAN, bold=True)
        tag.move_to([0, 2.2 if HORIZONTAL else 5.8, 0])
        code = _txt(
            f'{exam["canonical_id"]} — Q{exam["question_number"]}',
            40 if HORIZONTAL else 34,
            WHITE,
            bold=True,
        )
        src = _txt(f'Fonte: {exam["name"]} {exam["year"]} · {exam.get("booklet", "")}', 22, MUTED)
        group = VGroup(code, src).arrange(DOWN, buff=0.35).move_to([0, 0.15, 0])
        self.speak("source", [FadeIn(tag), Write(code), FadeIn(src)], default=3.5)
        self.clear_screen()

    def q_statement(self):
        h = self.heading("ENUNCIADO")
        q = self.manifest["question"]
        body = _txt(
            q["stem"],
            25 if HORIZONTAL else 23,
            WHITE,
            wrap=96 if HORIZONTAL else 47,
        )
        card = RoundedRectangle(
            width=14.2 if HORIZONTAL else 7.7,
            height=5.4 if HORIZONTAL else 10.8,
            corner_radius=0.18,
            stroke_color="#283652",
            fill_color="#111A2F",
            fill_opacity=0.88,
        )
        card.move_to([0, -0.05 if HORIZONTAL else 0.0, 0])
        _fit(body, 13.4 if HORIZONTAL else 7.0, 4.6 if HORIZONTAL else 9.7)
        body.move_to(card.get_center())
        first = "statement_01"
        if first in self.narration:
            self.speak(first, [FadeIn(h), FadeIn(card), Write(body)], default=4.0)
            for key in sorted(k for k in self.narration if k.startswith("statement_") and k != first):
                self.speak(key, default=3.0)
        else:
            self.play(FadeIn(h), FadeIn(card), Write(body), run_time=1.5)
            self.pause_for_step(len(str(q["stem"]).split()))
        self.clear_screen()

    def q_figure(self):
        h = self.heading("FIGURA DO ENUNCIADO")
        spec = (self.manifest.get("visuals") or {}).get("statement") or {}
        visual = build_visual(str(spec.get("renderer", "")), horizontal=HORIZONTAL)
        note = _txt(str(spec.get("description", "")), 22, MUTED, wrap=58 if HORIZONTAL else 42)
        if HORIZONTAL:
            visual.scale_to_fit_height(5.1)
            visual.move_to([-3.8, -0.15, 0])
            _fit(note, 6.2, 4.0)
            note.move_to([4.4, -0.2, 0])
        else:
            _fit(visual, 7.1, 8.5)
            visual.move_to([0, 0.4, 0])
            _fit(note, 7.1, 2.0)
            note.move_to([0, -5.25, 0])
        self.speak("figure", [FadeIn(h), Create(visual), FadeIn(note)], default=4.0)
        self.clear_screen()

    def q_options(self):
        h = self.heading("ALTERNATIVAS")
        options = self.manifest["question"]["options"]
        text = "\n\n".join(f"{letter}) {options[letter]}" for letter in "ABCDE")
        body = _txt(text, 30 if HORIZONTAL else 27, WHITE, wrap=75 if HORIZONTAL else 42)
        card = RoundedRectangle(
            width=13.0 if HORIZONTAL else 7.7,
            height=5.0 if HORIZONTAL else 10.0,
            corner_radius=0.18,
            stroke_color="#283652",
            fill_color="#111A2F",
            fill_opacity=0.88,
        )
        card.move_to([0, -0.15, 0])
        _fit(body, 12.1 if HORIZONTAL else 7.0, 4.2 if HORIZONTAL else 9.1)
        body.move_to(card.get_center())
        self.speak("options", [FadeIn(h), FadeIn(card), Write(body)], default=4.0)
        self.clear_screen()

    def q_data(self):
        h = self.heading("DADOS-CHAVE")
        items = self.manifest["solution"].get("data") or []
        rows = VGroup()
        for item in items:
            bullet = _txt("• " + str(item), 27 if HORIZONTAL else 25, WHITE, wrap=42 if HORIZONTAL else 38)
            rows.add(bullet)
        if HORIZONTAL:
            rows.arrange_in_grid(rows=2, cols=max(1, (len(rows) + 1) // 2), buff=(0.8, 0.8), aligned_edge=LEFT)
            _fit(rows, 13.5, 4.6)
            rows.move_to([0, -0.15, 0])
        else:
            rows.arrange(DOWN, buff=0.55, aligned_edge=LEFT)
            _fit(rows, 7.2, 9.0)
            rows.move_to([0, 0, 0])
        self.speak("data", [FadeIn(h), FadeIn(rows)], default=4.0)
        self.clear_screen()

    def q_strategy(self):
        h = self.heading("ESTRATÉGIA")
        sol = self.manifest["solution"]
        goal = _txt("Objetivo: " + sol["goal"], 28 if HORIZONTAL else 26, GOLD, wrap=50 if HORIZONTAL else 40, bold=True)
        hook = _txt(str(sol.get("hook", "")), 24, MUTED, wrap=52 if HORIZONTAL else 40)
        plans = VGroup(*[
            _txt(f"{i}. {item}", 25 if HORIZONTAL else 23, WHITE, wrap=42 if HORIZONTAL else 39)
            for i, item in enumerate(sol.get("strategy") or [], 1)
        ])
        plans.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        if HORIZONTAL:
            goal.move_to([-3.7, 1.2, 0]); _fit(goal, 6.3, 1.4)
            hook.move_to([-3.7, -0.4, 0]); _fit(hook, 6.3, 2.1)
            plans.move_to([4.0, -0.2, 0]); _fit(plans, 6.5, 4.8)
        else:
            goal.move_to([0, 4.4, 0]); _fit(goal, 7.2, 1.8)
            hook.move_to([0, 2.5, 0]); _fit(hook, 7.1, 2.0)
            plans.move_to([0, -0.9, 0]); _fit(plans, 7.2, 5.8)
        self.speak("strategy", [FadeIn(h), FadeIn(goal), FadeIn(hook), FadeIn(plans)], default=4.0)
        self.clear_screen()

    def q_concept(self):
        h = self.heading("MODELO VISUAL")
        spec = (self.manifest.get("visuals") or {}).get("concept") or {}
        visual = build_visual(str(spec.get("renderer", "")), horizontal=HORIZONTAL)
        note = _txt(str(spec.get("note", "")), 23, MUTED, wrap=55 if HORIZONTAL else 42)
        if HORIZONTAL:
            _fit(visual, 6.4, 5.1); visual.move_to([-3.9, -0.25, 0])
            _fit(note, 6.0, 3.8); note.move_to([4.3, -0.1, 0])
        else:
            _fit(visual, 7.0, 7.5); visual.move_to([0, 0.7, 0])
            _fit(note, 7.0, 2.2); note.move_to([0, -5.1, 0])
        self.speak("visual", [FadeIn(h), Create(visual), FadeIn(note)], default=4.0)
        self.clear_screen()

    def q_solution(self):
        steps = self.manifest["solution"]["steps"]
        h = self.heading("RESOLUÇÃO")
        self.play(FadeIn(h), run_time=0.3)
        previous = None
        previous_label = None
        concept_spec = (self.manifest.get("visuals") or {}).get("concept") or {}
        side_visual = None
        if HORIZONTAL and concept_spec:
            side_visual = build_visual(str(concept_spec.get("renderer", "")), horizontal=True)
            _fit(side_visual, 5.2, 4.8)
            side_visual.move_to([-4.3, -0.4, 0])
            self.play(FadeIn(side_visual), run_time=0.4)

        for i, step in enumerate(steps, 1):
            label = _txt(str(step.get("label", "")), 25 if HORIZONTAL else 23, GOLD, wrap=42 if HORIZONTAL else 38, bold=True)
            eq = _math(str(step.get("math", "")), 42 if HORIZONTAL else 40, WHITE)
            if HORIZONTAL:
                label.move_to([3.8, 1.15, 0]); _fit(label, 6.6, 1.5)
                eq.move_to([3.8, -0.6, 0]); _fit(eq, 6.6, 2.2)
            else:
                label.move_to([0, 4.6, 0]); _fit(label, 7.0, 1.6)
                eq.move_to([0, 0.1, 0]); _fit(eq, 7.1, 3.0)

            animations = []
            if previous is not None:
                animations.extend([FadeOut(previous), FadeOut(previous_label)])
            animations.extend([FadeIn(label), Write(eq)])
            self.speak(f"step_{i:02d}", animations, default=3.0)
            previous = eq
            previous_label = label

        self.clear_screen()

    def q_answer(self):
        h = self.heading("RESPOSTA")
        q = self.manifest["question"]
        letter = self.manifest["solution"]["final_answer"]
        answer = _txt(
            f"Alternativa {letter}\n{q['options'][letter]}",
            42 if HORIZONTAL else 36,
            GREEN_C,
            wrap=40,
            bold=True,
        )
        answer.move_to([0, 0, 0])
        _fit(answer, 10.5 if HORIZONTAL else 7.0, 4.0)
        self.speak("answer", [FadeIn(h), Write(answer)], default=3.0)
