from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class AreaCoroaCircular(Base):
    def construct(self):
        self.header("11", "Área da coroa circular", r"A=\pi(R^2-r^2)", "CÍRCULO")
        outer=Circle(2.55,color=CYAN,stroke_width=4,fill_color=CYAN,fill_opacity=0.20)
        inner=Circle(1.35,color=GOLD,stroke_width=4,fill_color=BG,fill_opacity=1)
        self.caption("A coroa é o que sobra do círculo maior.")
        self.play(Create(outer),run_time=1.0)
        self.play(Create(inner),run_time=0.9)
        Rline=Line(P(0,0),P(2.55,0),color=CYAN,stroke_width=3)
        rline=Line(P(0,0),P(1.35*np.cos(140*DEGREES),1.35*np.sin(140*DEGREES)),color=GOLD,stroke_width=3)
        labs=VGroup(safe_mathtex("R",34,CYAN).next_to(Rline,DOWN,buff=0.08),safe_mathtex("r",34,GOLD).next_to(rline,LEFT,buff=0.08))
        self.play(Create(Rline),Create(rline),Write(labs),run_time=0.8)
        self.hide_intro_formula()
        self.caption("Subtraia a área retirada do disco maior.")
        self.equation(r"A=\pi R^2-\pi r^2")
        self.play(Indicate(inner,color=RED),run_time=0.8)
        self.caption("Coloque π em evidência.")
        self.equation(r"A=\pi(R^2-r^2)")
        self.end()
