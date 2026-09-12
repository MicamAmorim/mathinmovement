from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class AreaCone(Base):
    def construct(self):
        self.header("27", "Área do cone", r"A_T=\pi rg+\pi r^2", "CONE")
        r,g=1.7,2.55
        base=Ellipse(width=2*r,height=.8,color=CYAN).move_to(P(0,-1.2))
        apex=P(0,-1.2+np.sqrt(g*g-r*r))
        sides=VGroup(Line(apex,P(-r,-1.2),color=CYAN),Line(apex,P(r,-1.2),color=CYAN))
        self.caption("Ao abrir a lateral, surge um setor circular de raio g.")
        self.play(Create(base),Create(sides),run_time=1.4)
        self.hide_intro_formula()
        sector=Sector(radius=2.55,angle=240*DEGREES,start_angle=-30*DEGREES,color=CYAN,
                      fill_color=CYAN,fill_opacity=0.18,stroke_width=3).shift(UP*0.15)
        self.play(FadeOut(VGroup(base,sides)),FadeIn(sector),run_time=0.9)
        radius=Line(P(0,0.15),P(2.55*np.cos(-PI/6),.15+2.55*np.sin(-PI/6)),color=GOLD,stroke_width=3)
        self.play(Create(radius),Write(safe_mathtex("g",34,GOLD).next_to(radius,UP,buff=0.08)),run_time=0.65)
        self.caption("O arco do setor tem o mesmo comprimento da circunferência da base.")
        self.equation(r"L_{arco}=2\pi r")
        arc=Arc(radius=2.55,start_angle=-PI/6,angle=4*PI/3,arc_center=P(0,.15),color=GOLD,stroke_width=6)
        self.play(Create(arc))
        self.equation(r"\frac{A_L}{\pi g^2}=\frac{2\pi r}{2\pi g}",size=42)
        self.caption("Área de setor = arco × raio ÷ 2.")
        self.equation(r"A_L=\frac{(2\pi r)g}{2}=\pi rg")
        self.caption("Some a base circular.")
        self.equation(r"A_T=\pi rg+\pi r^2")
        self.end()
