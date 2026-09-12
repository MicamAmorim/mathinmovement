from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class VolumePrismas(Base):
    def construct(self):
        self.header("22", "Volume de prismas", r"V=A_bh", "PRISMAS")
        # Pilha de seções idênticas.
        base=Polygon(*regular_polygon_points(6,1.8,center=P(0,-1.4),start_angle=PI/6),color=CYAN,fill_color=CYAN,fill_opacity=0.18)
        base.stretch(.3,1,about_point=P(0,-1.4))
        self.caption("Pense no prisma como uma pilha de bases idênticas.")
        self.play(Create(base),run_time=1.0)
        layers=VGroup(base)
        for i in range(1,8):
            q=base.copy().shift(UP*0.42*i).set_opacity(0.18+0.04*i)
            layers.add(q)
        self.play(LaggedStart(*[TransformFromCopy(base,layers[i]) for i in range(1,8)],lag_ratio=0.08),run_time=1.5)
        self.hide_intro_formula()
        self.caption("Cada camada tem a mesma área A_b.")
        self.equation(r"\Delta V=A_b\,\Delta h")
        hbrace=BraceBetweenPoints(P(2.2,-1.4),P(2.2,1.54),RIGHT,color=GOLD)
        self.play(FadeIn(hbrace),Write(safe_mathtex("h",34,GOLD).next_to(hbrace,RIGHT,buff=0.08)),run_time=0.7)
        self.caption("Somando todas as camadas ao longo da altura h.")
        self.equation(r"V=nA_b\Delta h,\quad n\Delta h=h",size=42)
        self.equation(r"V=A_bh")
        self.end()
