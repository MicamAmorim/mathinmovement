from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class AreaTriangulo(Base):
    def construct(self):
        self.header("01", "Área do triângulo", r"A=\frac{bh}{2}", "ÁREAS")
        tri = polygon_xy([(-2.8,-0.9),(2.2,-0.9),(-0.8,1.6)])
        self.caption("Uma base. Uma altura perpendicular.")
        self.play(Create(tri), run_time=1.8)
        h = DashedLine(P(-0.8,-0.9), P(-0.8,1.6), color=GOLD)
        ra = self.right_angle(P(-0.8,-0.9), quadrant=UR)
        labels = VGroup(
            safe_mathtex("b",36,CYAN).move_to(P(-0.3,-1.35)),
            safe_mathtex("h",36,GOLD).move_to(P(-1.15,0.25)),
        )
        self.play(Create(h), Create(ra), Write(labels), run_time=1.2)
        self.wait(1.2)

        self.caption("Duas cópias iguais completam um paralelogramo.")
        self.hide_intro_formula()
        other = tri.copy().set_color(GOLD)
        self.play(FadeOut(h), FadeOut(ra), FadeOut(labels), other.animate.shift(UP*0.45), run_time=0.8)
        self.play(Rotate(other, PI, about_point=other.get_center()), run_time=1.35)
        target = polygon_xy([(-0.8,1.6),(4.2,1.6),(2.2,-0.9)], GOLD)
        self.play(other.animate.shift(target.get_center()-other.get_center()), run_time=1.35)
        group = VGroup(tri, other)
        self.play(group.animate.shift(LEFT*0.7), run_time=0.65)
        self.wait(0.9)
        self.equation(r"2A=bh")
        self.caption("Cada triângulo ocupa metade da área.")
        self.equation(r"A=\frac{bh}{2}")
        self.end()
