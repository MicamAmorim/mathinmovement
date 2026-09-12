from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

class AreaEsfera(Base):
    def construct(self):
        self.header("30","Área da esfera",r"A=4\pi R^2","ESFERA")
        self.hide_intro_formula()
        R=2
        circle=Circle(radius=R,color=CYAN)
        self.caption("Uma faixa estreita: raio ρ e largura inclinada Δs.")
        self.play(Create(circle),run_time=2)
        theta=PI/6; Q=P(R*np.cos(theta),R*np.sin(theta))
        radius=Line(ORIGIN,Q,color=GOLD)
        rho=Line(P(0,Q[1]),Q,color=GREEN)
        a=Q+P(.45*np.sin(theta),-.45*np.cos(theta))
        b=Q+P(-.45*np.sin(theta),.45*np.cos(theta))
        tangent=Line(a,b,color=PINK,stroke_width=6)
        labs=VGroup(safe_mathtex("R",30,GOLD).next_to(radius,DOWN),
                    safe_mathtex(r"\rho",30,GREEN).next_to(rho,UP),
                    safe_mathtex(r"\Delta s",30,PINK).next_to(tangent,RIGHT))
        self.play(Create(radius),Create(rho),Create(tangent),Write(labs))
        self.equation(r"\Delta A\approx2\pi\rho\,\Delta s")
        self.caption("O raio diminui, mas a inclinação aumenta a largura.")
        c=P(a[0],b[1])
        aux=VGroup(DashedLine(a,c,color=WHITE),DashedLine(c,b,color=WHITE))
        dhlabel=safe_mathtex(r"\Delta h",25,WHITE).next_to(Line(a,c),RIGHT,buff=.5)
        self.play(Create(aux))
        self.play(Write(dhlabel))
        self.caption("Triângulos da tangente e do raio são semelhantes.")
        self.equation(r"\frac{\Delta h}{\Delta s}\longrightarrow\frac{\rho}{R}")
        self.caption("No limite, substitua a largura da faixa.")
        self.equation(r"dA=2\pi\rho\frac{R}{\rho}dh=2\pi R\,dh",size=40)
        self.caption("O fator ρ cancela. Cada altura contribui igualmente.")
        self.play(FadeOut(VGroup(radius,rho,tangent,labs,aux,dhlabel)))
        bands=VGroup(*[Line(P(-2,y),P(2,y),color=GOLD,stroke_width=2) for y in np.linspace(-2,2,17)])
        self.play(Create(bands),run_time=2)
        self.caption("Some da base ao topo: altura total 2R.")
        self.equation(r"A=\int_{-R}^{R}2\pi R\,dh")
        self.equation(r"A=2\pi R(2R)=4\pi R^2")
        self.end()
