from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class DiagonalParalelepipedo(Base):
    def construct(self):
        self.header("20", "Diagonal do paralelepípedo", r"D=\sqrt{a^2+b^2+c^2}", "POLIEDROS")
        # Caixa em projeção oblíqua.
        A=P(-2.6,-1.5); B=P(1.8,-1.5); C=P(1.8,0.9); D=P(-2.6,0.9)
        shift=P(1.1,0.9)
        A2,B2,C2,D2=A+shift,B+shift,C+shift,D+shift
        front=Polygon(A,B,C,D,color=CYAN,fill_opacity=0)
        back=Polygon(A2,B2,C2,D2,color=GOLD,fill_opacity=0)
        edges=VGroup(Line(A,A2),Line(B,B2),Line(C,C2),Line(D,D2)).set_color(WHITE)
        self.caption("Primeiro encontre a diagonal da base.")
        self.play(Create(front),Create(back),Create(edges),run_time=1.5)
        db=Line(A,B2,color=GREEN,stroke_width=5)
        self.play(Create(db),run_time=0.7)
        ground=Polygon(A,B,B2,color=GREEN,fill_opacity=.15)
        self.play(FadeIn(ground))
        self.play(Write(VGroup(
            safe_mathtex("a",30,CYAN).next_to(Line(A,B),DOWN),
            safe_mathtex("b",30,CYAN).next_to(Line(B,B2),RIGHT),
            safe_mathtex("c",30,GOLD).next_to(Line(B2,C2),RIGHT))))
        self.hide_intro_formula()
        self.equation(r"d_b^2=a^2+b^2")
        self.caption("Agora use outro triângulo retângulo com a altura c.")
        space=Line(A,C2,color=GOLD,stroke_width=6)
        self.play(Create(space),run_time=0.9)
        upright=Polygon(A,B2,C2,color=GOLD,fill_opacity=.18)
        self.play(FadeOut(ground),FadeIn(upright))
        self.equation(r"D^2=d_b^2+c^2")
        self.caption("Substitua a diagonal da base.")
        self.equation(r"D^2=a^2+b^2+c^2")
        self.equation(r"D=\sqrt{a^2+b^2+c^2}")
        self.end()
