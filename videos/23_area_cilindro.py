from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

class AreaCilindro(Base):
    def construct(self):
        self.header("23","Área do cilindro",r"A_T=2\pi r^2+2\pi rh","CILINDRO")
        self.hide_intro_formula()
        r=.9; h=1.8; n=32
        def point(theta,z):
            return P(r*np.cos(theta),.3*r*np.sin(theta)+z)
        strips=VGroup(*[Polygon(point(i*TAU/n,-h/2),point((i+1)*TAU/n,-h/2),
            point((i+1)*TAU/n,h/2),point(i*TAU/n,h/2),
            color=CYAN,fill_opacity=.15,stroke_width=1) for i in range(n)])
        self.caption("Corte uma geratriz vertical e abra a lateral.")
        self.play(Create(strips),run_time=2)
        self.caption("As linhas verticais mantêm a altura h.")
        targets=[Rectangle(width=TAU*r/n,height=h,color=CYAN,fill_opacity=.15,stroke_width=1)
                 .move_to(P(-PI*r+(i+.5)*TAU*r/n,0)) for i in range(n)]
        self.play(*[Transform(a,b) for a,b in zip(strips,targets)],run_time=4)
        self.caption("Uma volta na base se torna a largura do retângulo.")
        self.base_height(-PI*r,PI*r,-h/2,h/2,r"2\pi r","h")
        self.equation(r"A_L=(2\pi r)h")
        self.caption("A projeção virou planificação. Acrescente as duas tampas.")
        caps=VGroup(*[Circle(radius=r,color=GOLD,fill_opacity=.2).move_to(P(x,2.1)) for x in (-1.6,1.6)])
        self.play(LaggedStart(*[Create(c) for c in caps],lag_ratio=.5),run_time=2)
        self.equation(r"A_T=A_L+\pi r^2+\pi r^2")
        self.equation(r"A_T=2\pi rh+2\pi r^2")
        self.end()

