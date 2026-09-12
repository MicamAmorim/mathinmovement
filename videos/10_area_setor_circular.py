from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class AreaSetorCircular(Base):
    def construct(self):
        self.header("10", "Área do setor circular", r"A_s=\frac{\theta}{360^\circ}\pi r^2", "CÍRCULO")
        r=2.4; theta=120*DEGREES
        circle=Circle(r,color=MUTED,stroke_width=2)
        sector=Sector(radius=r,angle=theta,start_angle=0,color=CYAN,fill_color=CYAN,fill_opacity=0.32,stroke_width=4)
        angle=Arc(radius=0.7,start_angle=0,angle=theta,color=GOLD,stroke_width=4)
        self.caption("O setor é uma fração angular do círculo inteiro.")
        self.play(Create(circle),FadeIn(sector),Create(angle),run_time=1.7)
        self.play(Write(safe_mathtex(r"\theta",34,GOLD).move_to(P(0.6,0.5))),run_time=0.45)
        self.hide_intro_formula()
        self.caption("Três setores de 120° completam 360°.")
        copies=VGroup(*[sector.copy().rotate(i*theta,about_point=ORIGIN).set_color(GOLD)
                       for i in (1,2)])
        self.play(LaggedStart(*[FadeIn(s) for s in copies],lag_ratio=.5),run_time=2)
        self.equation(r"3A_s=\pi r^2\quad\Rightarrow\quad A_s=\frac13\pi r^2")
        self.play(FadeOut(copies))
        self.caption("Para um ângulo qualquer, usamos a fração da volta.")
        self.equation(r"\frac{A_s}{\pi r^2}=\frac{\theta}{360^\circ}")
        self.caption("A mesma proporção vale para as áreas.")
        self.equation(r"A_s=\frac{\theta}{360^\circ}\pi r^2")
        self.caption("Em radianos: metade de r² vezes o ângulo.")
        self.equation(r"A_s=\frac12r^2\theta\quad(\theta\ \mathrm{em\ radianos})",size=40)
        self.end()
