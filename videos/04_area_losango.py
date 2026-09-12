from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class AreaLosango(Base):
    def construct(self):
        self.header("04", "Área do losango", r"A=\frac{Dd}{2}", "ÁREAS")
        pts = [(0,1.8),(3,0),(0,-1.8),(-3,0)]
        whole = polygon_xy(pts)
        self.caption("As diagonais se cruzam ao meio.")
        self.play(Create(whole), run_time=1.8)
        dh = Line(P(-3,0),P(3,0),color=CYAN,stroke_width=4)
        dv = Line(P(0,-1.8),P(0,1.8),color=GOLD,stroke_width=4)
        labs = VGroup(
            safe_mathtex("D",36,CYAN).move_to(P(0,-0.42)),
            safe_mathtex("d",36,GOLD).move_to(P(0.38,0.22)),
        )
        self.play(Create(dh),Create(dv),Write(labs),run_time=1.1)

        self.caption("Elas criam quatro triângulos congruentes em pares.")
        tris = VGroup(
            polygon_xy([(0,0),(3,0),(0,1.8)],GOLD),
            polygon_xy([(0,0),(0,1.8),(-3,0)],CYAN),
            polygon_xy([(0,0),(-3,0),(0,-1.8)],GOLD),
            polygon_xy([(0,0),(0,-1.8),(3,0)],CYAN),
        )
        self.remove(whole)
        self.add(*tris,dh,dv,labs)
        self.wait(0.8)

        self.caption("Rearranje as próprias peças em um retângulo.")
        self.hide_intro_formula()
        self.play(FadeOut(dh),FadeOut(dv),FadeOut(labs),run_time=0.4)
        # Rigid motions: no vertex morphing, shear or reflection.
        for i,angle,shift in ((0,0,P(-3,-.9)),(2,0,P(0,.9)),(1,PI,P(0,.9)),(3,PI,P(3,-.9))):
            self.play(rigid_motion(tris[i],angle,shift),run_time=1.6)
        outline = Rectangle(width=6,height=1.8,color=WHITE)
        b = BraceBetweenPoints(P(-3,-1.05),P(3,-1.05),DOWN,color=CYAN)
        h = BraceBetweenPoints(P(3.15,-0.9),P(3.15,0.9),RIGHT,color=GOLD)
        dims = VGroup(
            b,safe_mathtex("D",34,CYAN).next_to(b,DOWN,buff=0.08),
            h,safe_mathtex(r"\frac d2",34,GOLD).next_to(h,RIGHT,buff=0.08),
        )
        self.play(Create(outline),FadeIn(dims),run_time=0.85)
        self.caption("O retângulo mede D por d/2.")
        self.equation(r"A=D\cdot\frac d2")
        self.equation(r"A=\frac{Dd}{2}")
        self.end()
