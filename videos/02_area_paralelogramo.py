from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class AreaParalelogramo(Base):
    def construct(self):
        self.header("02", "Área do paralelogramo", r"A=bh", "ÁREAS")
        whole = polygon_xy([(-3,-1),(1.5,-1),(3,1.5),(-1.5,1.5)])
        self.caption("A inclinação do lado não é a altura.")
        self.play(Create(whole), run_time=1.8)
        cut = DashedLine(P(1.5,-1), P(1.5,1.5), color=GOLD)
        self.play(Create(cut), run_time=0.9)
        self.wait(0.8)

        self.caption("Corte a ponta direita.")
        left = polygon_xy([(-3,-1),(-1.5,-1),(-1.5,1.5)])
        mid = polygon_xy([(-1.5,-1),(1.5,-1),(1.5,1.5),(-1.5,1.5)])
        moving = polygon_xy([(1.5,-1),(3,1.5),(1.5,1.5)], GOLD)
        self.remove(whole)
        self.add(left, mid, moving)
        self.play(FadeOut(cut), run_time=0.35)

        self.caption("Translade a própria peça para o outro lado.")
        self.hide_intro_formula()
        self.play(moving.animate.shift(UP*0.55), run_time=0.55)
        self.play(moving.animate.shift(LEFT*4.5), run_time=2.2)
        self.play(moving.animate.shift(DOWN*0.55), run_time=0.55)
        outline = Rectangle(width=4.5, height=2.5, color=WHITE).move_to(P(-0.75,0.25))
        self.play(Create(outline), run_time=0.8)
        dims = self.base_height(-3,1.5,-1,1.5)
        self.caption("Mesmas peças. Agora vemos um retângulo.")
        self.equation(r"A=b\cdot h")
        self.end()
