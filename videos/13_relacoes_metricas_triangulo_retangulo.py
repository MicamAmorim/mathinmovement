from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class RelacoesMetricasTrianguloRetangulo(Base):
    def construct(self):
        self.header("13", "Relações métricas no triângulo retângulo", r"h^2=mn", "TRIÂNGULOS")
        A=P(-3,-1.0); B=P(3,-1.0); C=P(-0.6,-1+np.sqrt(2.4*3.6)); H=P(-0.6,-1.0)
        tri=Polygon(A,B,C,color=CYAN,fill_color=CYAN,fill_opacity=0.12,stroke_width=3)
        alt=DashedLine(C,H,color=GOLD,stroke_width=3)
        self.caption("A altura à hipotenusa cria dois triângulos semelhantes.")
        self.play(Create(tri),Create(alt),run_time=1.6)
        labels=VGroup(
            safe_mathtex("h",32,GOLD).next_to(alt,RIGHT,buff=0.08),
            safe_mathtex("m",32,CYAN).move_to(P(-1.8,-1.42)),
            safe_mathtex("n",32,CYAN).move_to(P(1.2,-1.42)),
            safe_mathtex("c",32,WHITE).move_to(P(0,-1.72)),
            safe_mathtex("a",32,GREEN).move_to((B+C)/2+P(.3,.15)),
            safe_mathtex("b",32,GOLD).move_to((A+C)/2+P(-.3,.15)),
        )
        self.play(Write(labels),run_time=0.8)
        self.hide_intro_formula()
        left=Polygon(A,H,C,color=GOLD,fill_color=GOLD,fill_opacity=0.16,stroke_width=3)
        right=Polygon(H,B,C,color=GREEN,fill_color=GREEN,fill_opacity=0.13,stroke_width=3)
        self.play(FadeIn(left),FadeIn(right),run_time=0.7)
        angles=VGroup(
            Angle(Line(A,H),Line(A,C),radius=.45,color=PINK),
            Angle(Line(C,H),Line(C,B),radius=.45,color=PINK))
        self.play(Create(angles),Create(self.right_angle(H,quadrant=UR)))
        self.caption("Os ângulos em rosa são iguais: o outro par é complementar.")
        self.caption("Da semelhança: h/m = n/h.")
        self.equation(r"\frac{h}{m}=\frac{n}{h}")
        self.equation(r"h^2=mn")
        self.caption("As projeções também relacionam os catetos à hipotenusa.")
        self.pulse(right)
        self.equation(r"\frac{n}{a}=\frac{a}{c}")
        self.equation(r"a^2=cn")
        self.pulse(left)
        self.equation(r"\frac{m}{b}=\frac{b}{c}")
        self.equation(r"b^2=cm")
        self.equation(r"a^2=cn\qquad b^2=cm")
        self.end()
