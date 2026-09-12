from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class AreaTrapezio(Base):
    def construct(self):
        self.header("03", "Área do trapézio", r"A=\frac{(B+b)h}{2}", "ÁREAS")
        trap = polygon_xy([(-3,-1),(1,-1),(0,1.3),(-2,1.3)])
        self.caption("Duas bases paralelas: B e b.")
        self.play(Create(trap), run_time=1.8)
        labs = VGroup(
            safe_mathtex("B",36,CYAN).move_to(P(-1,-1.4)),
            safe_mathtex("b",36,GOLD).move_to(P(-1,1.68)),
        )
        self.play(Write(labs), run_time=0.8)

        self.caption("Gire uma cópia e encaixe ao lado.")
        self.hide_intro_formula()
        copy = trap.copy().set_color(GOLD)
        self.play(FadeOut(labs), copy.animate.shift(UP*0.5), run_time=0.75)
        self.play(Rotate(copy, PI, about_point=copy.get_center()), run_time=1.25)
        target = polygon_xy([(4,1.3),(0,1.3),(1,-1),(3,-1)], GOLD)
        self.play(copy.animate.shift(target.get_center()-copy.get_center()), run_time=1.35)
        self.play(VGroup(trap,copy).animate.shift(LEFT*0.5), run_time=0.55)

        brace = BraceBetweenPoints(P(-3.5,-1.15), P(2.5,-1.15), DOWN, color=CYAN)
        blab = safe_mathtex("B+b",36,CYAN).next_to(brace, DOWN, buff=0.08)
        height = self.dashed_height(P(2.5,-1), P(2.5,1.3), "h")
        self.play(FadeIn(brace), Write(blab), FadeIn(height), run_time=0.8)
        self.caption("As duas peças formam um paralelogramo.")
        self.equation(r"2A=(B+b)h")
        self.caption("Um trapézio é metade dessa área.")
        self.equation(r"A=\frac{(B+b)h}{2}")
        self.end()
