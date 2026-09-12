from manim import *
import numpy as np
import os
import textwrap
import manimpango

# ------------------------------------------------------------
# MATEMÁTICA EM MOVIMENTO — identidade visual comum
# ------------------------------------------------------------
config.frame_width = 9
config.frame_height = 16
config.background_color = "#0B1020"
FONT = next((f for f in (os.getenv('MANIM_FONT', ''), 'DejaVu Sans', 'Arial', 'Liberation Sans')
             if f in manimpango.list_fonts()), 'sans-serif')

BG = "#0B1020"
CYAN = "#55D6CF"
GOLD = "#FFCC78"
WHITE = "#EEF2FF"
MUTED = "#9CAAC5"
PINK = "#F28DB2"
GREEN = "#8DE2A7"
RED = "#FF7D7D"
BLUE = "#79A7FF"


def P(x, y):
    return np.array([x, y, 0.0])

def rigid_motion(mob, angle, shift):
    """Rotate and translate together, retaining lengths and area at every frame."""
    original = mob.copy()
    return UpdateFromAlphaFunc(mob, lambda m, t: m.become(
        original.copy().rotate(angle*t, about_point=ORIGIN).shift(t*shift)))


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
        center + radius * np.array([np.cos(start_angle - k * TAU / n), np.sin(start_angle - k * TAU / n), 0])
        for k in range(n)
    ]


def safe_mathtex(tex, font_size=50, color=WHITE, max_width=7.4):
    obj = MathTex(tex, font_size=font_size, color=color)
    if obj.width > max_width:
        obj.scale_to_fit_width(max_width)
    return obj


class MotionMathScene(Scene):
    """Base para os 30 vídeos verticais.

    Zonas reservadas:
      topo: marca + número + título + fórmula inicial
      centro: prova visual
      inferior: legenda curta + dedução
      rodapé: assinatura
    """

    category = "GEOMETRIA"

    def play(self, *animations, **kwargs):
        kwargs['run_time'] = kwargs.get('run_time', 1) * float(os.getenv('MANIM_PACE', '1.15'))
        return super().play(*animations, **kwargs)

    def wait(self, duration=1, **kwargs):
        kwargs.setdefault('frozen_frame', True)
        return super().wait(duration, **kwargs)

    def text(self, s, size=28, color=WHITE, max_width=7.4, weight=NORMAL):
        t = Text(s, font=FONT, font_size=size, color=color, weight=weight)
        if t.width > max_width:
            t.scale_to_fit_width(max_width)
        return t

    def header(self, number, title, formula=None, category=None):
        category = category or self.category
        self.brand = self.text("MATEMÁTICA EM MOVIMENTO", 17, MUTED).move_to(P(0, 6.75))
        self.counter = self.text(f"{number}  /  {category}", 19, CYAN).move_to(P(0, 5.95))
        self.title_mob = self.text(title, 38, WHITE, weight=BOLD).move_to(P(0, 5.02))
        self.add(self.brand)
        self.play(FadeIn(self.counter, shift=UP * 0.12), run_time=0.55)
        self.play(Write(self.title_mob), run_time=1.0)
        self.intro_formula = VGroup()
        if formula:
            self.intro_formula = safe_mathtex(formula, 54).move_to(P(0, 3.55))
            self.play(Write(self.intro_formula), run_time=1.25)
        self.caption_mob = VGroup()
        self.work_formula = VGroup()
        self.signature = self.text("MIQUÉIAS AMORIM", 15, MUTED).move_to(P(0, -6.78))
        self.add(self.signature)
        self.wait(0.55)

    def hide_intro_formula(self):
        if len(self.intro_formula) > 0:
            self.play(FadeOut(self.intro_formula), run_time=0.45)
            self.intro_formula = VGroup()

    def caption(self, s, color=WHITE, size=25, y=-3.28):
        new = self.text(textwrap.fill(s, width=47), size, color).move_to(P(0, y))
        if len(self.caption_mob) > 0:
            self.play(FadeOut(self.caption_mob), FadeIn(new, shift=UP * 0.10), run_time=0.42)
        else:
            self.play(FadeIn(new, shift=UP * 0.10), run_time=0.42)
        self.caption_mob = new
        self.wait(max(1.4, len(s.split()) / 3.0))
        return new

    def equation(self, tex, color=WHITE, size=50, y=-4.75, transform=True):
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

    def end(self, pause=2.4):
        if len(self.work_formula) > 0:
            self.play(Indicate(self.work_formula, color=CYAN, scale_factor=1.04), run_time=1.0)
        self.wait(pause)

    def base_height(self, x1, x2, y_base, y_top, base_label="b", height_label="h"):
        b = BraceBetweenPoints(P(x1, y_base - 0.12), P(x2, y_base - 0.12), DOWN, color=CYAN)
        h = BraceBetweenPoints(P(x2 + 0.15, y_base), P(x2 + 0.15, y_top), RIGHT, color=GOLD)
        group = VGroup(
            b,
            safe_mathtex(base_label, 36, CYAN).next_to(b, DOWN, buff=0.08),
            h,
            safe_mathtex(height_label, 36, GOLD).next_to(h, RIGHT, buff=0.08),
        )
        self.play(FadeIn(group), run_time=0.75)
        return group

    def right_angle(self, at, size=0.20, color=GOLD, quadrant=UR):
        x, y, _ = at
        sx = 1 if quadrant[0] >= 0 else -1
        sy = 1 if quadrant[1] >= 0 else -1
        return Polygon(
            P(x, y), P(x + sx * size, y), P(x + sx * size, y + sy * size), P(x, y + sy * size),
            color=color, stroke_width=2, fill_opacity=0
        )

    def measure_line(self, start, end, label, color=CYAN, direction=DOWN, buff=0.12, label_size=34):
        line = Line(start, end, color=color, stroke_width=3)
        lab = safe_mathtex(label, label_size, color).next_to(line, direction, buff=buff)
        return VGroup(line, lab)

    def remove_center(self, *mobjects, run_time=0.45):
        if mobjects:
            self.play(*[FadeOut(m) for m in mobjects], run_time=run_time)

    def pulse(self, mob, color=GOLD, scale_factor=1.03):
        self.play(Indicate(mob, color=color, scale_factor=scale_factor), run_time=0.9)

    def dashed_height(self, start, end, label="h", label_side=RIGHT):
        d = DashedLine(start, end, color=GOLD, stroke_width=3)
        lab = safe_mathtex(label, 34, GOLD).next_to(d, label_side, buff=0.10)
        return VGroup(d, lab)

    def copy_note(self, s="Mesmas peças. Mesma área."):
        return self.caption(s, color=MUTED, size=23)


# Alias curto para os arquivos de cenas.
Base = MotionMathScene
