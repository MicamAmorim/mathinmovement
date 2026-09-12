from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class AreaTrianguloSeno(Base):
    def construct(self):
        self.header("17", "Área do triângulo usando seno", r"A=\frac12bc\sin A", "TRIGONOMETRIA")
        A=P(-3,-1.2); B=P(3,-1.2); C=P(0.7,2.0); H=P(0.7,-1.2)
        tri=Polygon(A,B,C,color=CYAN,fill_color=CYAN,fill_opacity=0.15,stroke_width=3)
        alt=DashedLine(C,H,color=GOLD,stroke_width=3)
        self.caption("A fórmula comum usa base c e altura h.")
        self.play(Create(tri),Create(alt),run_time=1.5)
        labs=VGroup(
            safe_mathtex("b",32,CYAN).move_to((A+C)/2+P(-0.25,0.2)),
            safe_mathtex("c",32,CYAN).move_to(P(0,-1.55)),
            safe_mathtex("h",32,GOLD).next_to(alt,RIGHT,buff=0.08),
            safe_mathtex("A",30,WHITE).next_to(A,UP+RIGHT,buff=0.1),
        )
        self.play(Write(labs),run_time=0.8)
        self.hide_intro_formula()
        self.equation(r"A_{\triangle}=\frac{ch}{2}")
        self.caption("No triângulo retângulo, h = b sen A.")
        half=Polygon(A,H,C,color=GOLD,fill_opacity=.18)
        self.play(FadeIn(half))
        self.equation(r"\sin A=\frac{h}{b}\Rightarrow h=b\sin A")
        self.caption("Substitua a altura.")
        self.equation(r"A_{\triangle}=\frac{c(b\sin A)}{2}")
        self.equation(r"A_{\triangle}=\frac12bc\sin A")
        self.end()
