from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class VolumeCilindro(Base):
    def construct(self):
        self.header("24", "Volume do cilindro", r"V=\pi r^2h", "CILINDRO")
        base=Ellipse(width=4.6,height=1.25,color=CYAN,fill_color=CYAN,fill_opacity=0.16).move_to(P(0,-1.45))
        self.caption("Empilhe discos de mesma área.")
        self.play(Create(base),run_time=0.9)
        disks=VGroup(base)
        for i in range(1,9):
            d=base.copy().shift(UP*0.36*i)
            disks.add(d)
        self.play(LaggedStart(*[TransformFromCopy(base,disks[i]) for i in range(1,9)],lag_ratio=0.07),run_time=1.5)
        sideL=Line(P(-2.3,-1.45),P(-2.3,1.43),color=WHITE,stroke_width=2)
        sideR=Line(P(2.3,-1.45),P(2.3,1.43),color=WHITE,stroke_width=2)
        self.play(Create(sideL),Create(sideR),run_time=0.55)
        self.hide_intro_formula()
        self.caption("Cada seção tem área πr².")
        self.equation(r"A_b=\pi r^2")
        self.caption("Área constante em cada altura: some as camadas.")
        self.equation(r"V=n\pi r^2\Delta h,\quad n\Delta h=h",size=42)
        self.equation(r"V=A_bh")
        self.equation(r"V=\pi r^2h")
        self.end()
