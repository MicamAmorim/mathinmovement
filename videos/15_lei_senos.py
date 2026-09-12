from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class LeiSenos(Base):
    def construct(self):
        self.header("15", "Lei dos senos", r"\frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C}", "TRIGONOMETRIA")
        A=P(-3,-1.2); B=P(3,-1.2); C=P(0.8,2.0); H=P(0.8,-1.2)
        tri=Polygon(A,B,C,color=CYAN,fill_color=CYAN,fill_opacity=0.12,stroke_width=3)
        alt=DashedLine(C,H,color=GOLD,stroke_width=3)
        self.caption("Trace uma altura e olhe para os dois triângulos retângulos.")
        self.play(Create(tri),Create(alt),run_time=1.6)
        labs=VGroup(
            safe_mathtex("A",30,WHITE).next_to(A,LEFT,buff=0.08),
            safe_mathtex("B",30,WHITE).next_to(B,RIGHT,buff=0.08),
            safe_mathtex("C",30,WHITE).next_to(C,UP,buff=0.08),
            safe_mathtex("c",32,CYAN).move_to(P(0,-1.65)),
            safe_mathtex("a",32,CYAN).move_to((B+C)/2+P(0.25,0.15)),
            safe_mathtex("b",32,CYAN).move_to((A+C)/2+P(-0.25,0.15)),
            safe_mathtex("h",32,GOLD).next_to(alt,RIGHT,buff=0.08),
        )
        self.play(Write(labs),run_time=0.8)
        self.hide_intro_formula()
        self.caption("A mesma altura pode ser escrita de duas formas.")
        self.equation(r"h=b\sin A")
        self.equation(r"h=a\sin B")
        self.caption("Iguale e reorganize.")
        self.equation(r"b\sin A=a\sin B")
        self.equation(r"\frac{a}{\sin A}=\frac{b}{\sin B}")
        self.caption("Repetindo com outra altura, entra o terceiro lado.")
        K=A+np.dot(B-A,C-A)/np.dot(C-A,C-A)*(C-A)
        second=DashedLine(B,K,color=GREEN)
        self.play(FadeOut(alt),FadeOut(labs[-1]),Create(second))
        self.equation(r"h'=c\sin A=a\sin C")
        self.equation(r"\frac{a}{\sin A}=\frac{c}{\sin C}")
        self.equation(r"\frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C}")
        self.end()
