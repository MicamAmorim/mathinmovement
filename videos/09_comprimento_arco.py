from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class ComprimentoArco(Base):
    def construct(self):
        self.header("09", "Comprimento de arco", r"L=\frac{\theta}{360^\circ}\,2\pi r", "CÍRCULO")
        r=2.3; theta=120*DEGREES
        circle=Circle(r,color=MUTED,stroke_width=2)
        arc=Arc(radius=r,start_angle=0,angle=theta,color=CYAN,stroke_width=7)
        radii=VGroup(Line(P(0,0),P(r,0),color=GOLD),Line(P(0,0),P(r*np.cos(theta),r*np.sin(theta)),color=GOLD))
        angle=Arc(radius=0.65,start_angle=0,angle=theta,color=GOLD,stroke_width=4)
        self.caption("O arco ocupa a mesma fração angular da circunferência.")
        self.play(Create(circle),Create(radii),Create(arc),Create(angle),run_time=1.8)
        self.play(Write(safe_mathtex(r"\theta",34,GOLD).move_to(P(0.55,0.48))),run_time=0.45)
        self.hide_intro_formula()
        self.caption("Aqui são 120°: três arcos iguais completam a volta.")
        copies=VGroup(*[arc.copy().rotate(i*theta,about_point=ORIGIN).set_color(GOLD)
                       for i in (1,2)])
        self.play(LaggedStart(*[Create(s) for s in copies],lag_ratio=.5),run_time=2)
        self.equation(r"3L=2\pi r\quad\Rightarrow\quad L=\frac13\,2\pi r")
        self.play(FadeOut(copies))
        self.caption("Para qualquer ângulo, usamos a mesma proporção.")
        self.equation(r"\frac{L}{2\pi r}=\frac{\theta}{360^\circ}")
        self.caption("Multiplique a circunferência total pela fração do ângulo.")
        self.equation(r"L=\frac{\theta}{360^\circ}\,2\pi r")
        self.caption("Em radianos, a relação fica ainda mais simples.")
        self.equation(r"L=r\theta\quad(\theta\ \text{em radianos})")
        self.end()
