from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class LeiCossenos(Base):
    def construct(self):
        self.header("16", "Lei dos cossenos", r"a^2=b^2+c^2-2bc\cos A", "TRIGONOMETRIA")
        A=P(-3,-1.2); B=P(3,-1.2); C=P(0.8,2.0); H=P(0.8,-1.2)
        tri=Polygon(A,B,C,color=CYAN,fill_color=CYAN,fill_opacity=0.12,stroke_width=3)
        alt=DashedLine(C,H,color=GOLD,stroke_width=3)
        self.caption("Projete o lado b sobre o lado c.")
        self.play(Create(tri),Create(alt),run_time=1.5)
        labs=VGroup(
            safe_mathtex("a",32,CYAN).move_to((B+C)/2+P(0.25,0.18)),
            safe_mathtex("b",32,CYAN).move_to((A+C)/2+P(-0.25,0.18)),
            safe_mathtex("c",32,CYAN).move_to(P(0,-2.15)),
            safe_mathtex("A",30,WHITE).next_to(A,UP+RIGHT,buff=0.12),
        )
        self.play(Write(labs),run_time=0.8)
        self.hide_intro_formula()
        self.caption("A projeção horizontal de b é b cos A.")
        proj=Line(A,H,color=GOLD,stroke_width=5)
        self.play(Create(proj),Write(safe_mathtex(r"b\cos A",30,GOLD).next_to(proj,DOWN,buff=0.08)),run_time=0.8)
        self.play(Write(safe_mathtex(r"b\sin A",28,GOLD).next_to(alt,RIGHT)))
        self.caption("O outro trecho da base mede c − b cos A.")
        self.pulse(Line(H,B,color=GREEN))
        self.equation(r"AH=b\cos A,\quad CH=b\sin A",size=42)
        self.caption("Aplique Pitágoras ao triângulo da direita.")
        self.equation(r"a^2=(c-b\cos A)^2+(b\sin A)^2")
        self.caption("Expanda e use sen²A + cos²A = 1.")
        self.equation(r"a^2=c^2-2bc\cos A+b^2(\cos^2A+\sin^2A)")
        self.equation(r"a^2=b^2+c^2-2bc\cos A")
        self.end()
