from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class AreaTrianguloEquilatero(Base):
    def construct(self):
        self.header("05", "Área do triângulo equilátero", r"A=\frac{\sqrt3}{4}\ell^2", "ÁREAS")
        L = 4.4
        H = np.sqrt(3)*L/2
        a,b,c = P(-L/2,-1.45),P(L/2,-1.45),P(0,-1.45+H)
        tri = Polygon(a,b,c,color=CYAN,stroke_width=3,fill_color=CYAN,fill_opacity=0.22)
        self.caption("A altura também é mediana.")
        self.play(Create(tri),run_time=1.8)
        alt = DashedLine(c,P(0,-1.45),color=GOLD)
        ra = self.right_angle(P(0,-1.45),quadrant=UR)
        labels = VGroup(
            safe_mathtex(r"\ell",36,CYAN).move_to(P(0,-1.85)),
            safe_mathtex(r"\ell",36,CYAN).move_to(P(1.7,0.7)),
            safe_mathtex(r"\frac\ell2",34,GOLD).move_to(P(-1.28,-1.05)),
            safe_mathtex("h",34,GOLD).move_to(P(0.32,0.45)),
        )
        self.play(Create(alt),Create(ra),Write(labels),run_time=1.15)

        self.caption("Metade do equilátero é um triângulo retângulo.")
        half = Polygon(a,P(0,-1.45),c,color=GOLD,stroke_width=3,fill_color=GOLD,fill_opacity=0.16)
        self.hide_intro_formula()
        self.play(FadeIn(half),run_time=0.6)
        self.equation(r"h^2+\left(\frac\ell2\right)^2=\ell^2")
        self.caption("Pitágoras fornece a altura.")
        self.equation(r"h^2=\ell^2-\frac{\ell^2}{4}")
        self.equation(r"h^2=\frac34\ell^2")
        self.equation(r"h=\frac{\sqrt3}{2}\ell")
        self.caption("Substitua na fórmula da área do triângulo.")
        self.equation(r"A=\frac{\ell h}{2}=\frac{\sqrt3}{4}\ell^2")
        self.end()
