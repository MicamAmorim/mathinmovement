from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class AreaPiramidesRegulares(Base):
    def construct(self):
        self.header("25", "Área de pirâmides regulares", r"A_T=A_b+\frac{P_bg}{2}", "PIRÂMIDES")
        # Pirâmide quadrangular em projeção.
        base=Polygon(P(-2.3,-1.3),P(1.8,-1.3),P(2.6,-0.45),P(-1.5,-0.45),color=CYAN,fill_color=CYAN,fill_opacity=0.13)
        apex=P(0.3,2.15)
        edges=VGroup(*[Line(apex,v,color=GOLD,stroke_width=3) for v in base.get_vertices()])
        self.caption("Cada face lateral é um triângulo de altura g.")
        self.play(Create(base),Create(edges),run_time=1.5)
        self.hide_intro_formula()
        self.caption("Ao planificar, as faces triangulares ficam lado a lado.")
        n=4; side=1.35; y=-0.75; g=2.0
        faces=VGroup()
        for i in range(n):
            x=-2.9+i*side
            faces.add(Polygon(P(x,y),P(x+side,y),P(x+side/2,y+g),color=(GOLD if i%2==0 else CYAN),
                fill_color=(GOLD if i%2==0 else CYAN),fill_opacity=0.16,stroke_width=2))
        self.play(FadeOut(VGroup(base,edges)),LaggedStart(*[FadeIn(f) for f in faces],lag_ratio=0.08),run_time=1.2)
        baseLine=Line(P(-2.9,y),P(-2.9+n*side,y),color=CYAN,stroke_width=4)
        height=DashedLine(P(-2.9+side/2,y),P(-2.9+side/2,y+g),color=GOLD)
        self.play(Create(baseLine),Create(height),run_time=0.7)
        self.play(Write(safe_mathtex("g",30,GOLD).next_to(height,RIGHT)),
                  Write(safe_mathtex(r"P_b=n\ell",30,CYAN).next_to(baseLine,DOWN)))
        self.caption("A altura g pertence à face, não ao interior da pirâmide.")
        self.equation(r"A_{\rm face}=\frac{\ell g}{2}")
        self.equation(r"A_L=n\cdot\frac{\ell g}{2}=\frac{P_bg}{2}")
        self.caption("Some a área da base.")
        self.equation(r"A_T=A_b+\frac{P_bg}{2}")
        self.end()
