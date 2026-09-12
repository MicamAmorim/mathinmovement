from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class TeoremaPitagoras(Base):
    def construct(self):
        self.header("12", "Teorema de Pitágoras", r"a^2+b^2=c^2", "TRIÂNGULOS")
        a,b=2.0,3.0
        side=a+b
        # Quadrado externo com quatro triângulos e quadrado central c².
        outer=Square(side_length=side,color=WHITE).move_to(P(0,0.2))
        x0,y0=-side/2,-side/2+0.2
        t1=Polygon(P(x0,y0),P(x0+b,y0),P(x0,y0+a),color=CYAN,fill_color=CYAN,fill_opacity=0.25)
        t2=t1.copy().rotate(PI/2,about_point=P(0,0.2))
        t3=t1.copy().rotate(PI,about_point=P(0,0.2))
        t4=t1.copy().rotate(3*PI/2,about_point=P(0,0.2))
        tris=VGroup(t1,t2,t3,t4)
        self.caption("Quatro triângulos iguais cabem num quadrado de lado a+b.")
        self.play(Create(outer),LaggedStart(*[FadeIn(t) for t in tris],lag_ratio=0.12),run_time=1.7)
        self.hide_intro_formula()
        side_labels=VGroup(
            safe_mathtex("b",32,CYAN).next_to(Line(P(x0,y0),P(x0+b,y0)),DOWN),
            safe_mathtex("a",32,GOLD).next_to(Line(P(x0+b,y0),P(x0+side,y0)),DOWN))
        self.play(Write(side_labels))
        self.equation(r"(a+b)^2=4\left(\frac{ab}{2}\right)+c^2")
        self.caption("A área central é c².")
        center=Polygon(
            P(x0+b,y0),P(x0+side,y0+b),P(x0+a,y0+side),P(x0,y0+a),
            color=GOLD,fill_color=GOLD,fill_opacity=0.20,stroke_width=4
        )
        self.play(Create(center),run_time=0.9)
        self.caption("Cada lado central é uma hipotenusa c.")
        self.play(Write(safe_mathtex("c",32,GOLD).next_to(
            Line(P(x0+b,y0),P(x0+side,y0+b)),LEFT)))
        self.caption("Os ângulos agudos somam 90°: o centro é um quadrado.")
        self.equation(r"a^2+2ab+b^2=2ab+c^2")
        self.caption("Cancele 2ab dos dois lados.")
        self.equation(r"a^2+b^2=c^2")
        self.end()
