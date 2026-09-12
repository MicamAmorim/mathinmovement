from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class RazoesTrigonometricasSemelhanca(Base):
    def construct(self):
        self.header("14", "Razões trigonométricas por semelhança", r"\sin\theta=\frac{op}{hip}", "TRIGONOMETRIA")
        theta=32*DEGREES
        # Dois triângulos semelhantes, mesma inclinação.
        A=P(-3,-1.5); B=P(-0.4,-1.5); C=P(-0.4,-1.5+2.6*np.tan(theta))
        A2=P(-3,-1.5); B2=P(2.5,-1.5); C2=P(2.5,-1.5+5.5*np.tan(theta))
        small=Polygon(A,B,C,color=GOLD,fill_color=GOLD,fill_opacity=0.16,stroke_width=3)
        large=Polygon(A2,B2,C2,color=CYAN,fill_color=CYAN,fill_opacity=0.10,stroke_width=3)
        self.caption("Mude o tamanho, mas preserve o mesmo ângulo θ.")
        self.play(Create(small),run_time=1.0)
        self.play(TransformFromCopy(small,large),run_time=1.2)
        arc=Arc(radius=0.65,start_angle=0,angle=theta,arc_center=A,color=WHITE,stroke_width=3)
        self.play(Create(arc),Write(safe_mathtex(r"\theta",30,WHITE).next_to(arc,RIGHT,buff=0.05)),run_time=0.6)
        self.hide_intro_formula()
        sides=VGroup(
            safe_mathtex("op",30,CYAN).next_to(Line(B2,C2),RIGHT),
            safe_mathtex("adj",30,CYAN).next_to(Line(A2,B2),DOWN),
            safe_mathtex("hip",30,GOLD).next_to(Line(A2,C2),UP))
        self.play(Write(sides))
        self.caption("Triângulos semelhantes multiplicam todos os lados pelo mesmo fator.")
        self.equation(r"\frac{op_1}{hip_1}=\frac{op_2}{hip_2}")
        self.equation(r"\frac{k\,op_1}{k\,hip_1}=\frac{op_1}{hip_1}")
        self.caption("Por isso as razões dependem do ângulo, não do tamanho.")
        self.equation(r"\sin\theta=\frac{op}{hip}\quad \cos\theta=\frac{adj}{hip}")
        self.equation(r"\tan\theta=\frac{op}{adj}")
        self.end()
