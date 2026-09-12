from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class VolumeCone(Base):
    def construct(self):
        self.header("28", "Volume do cone", r"V=\frac13\pi r^2h", "CONE")
        self.caption("Aproxime o cone por pirâmides regulares com mais e mais lados.")
        # Sequência: pirâmide de base quadrada -> hexagonal -> quase circular.
        shapes=VGroup()
        centers=[P(-2.5,-0.6),P(0,-0.6),P(2.5,-0.6)]
        ns=[4,6,14]
        for center,n in zip(centers,ns):
            pts=regular_polygon_points(n,0.95,center=center,start_angle=PI/2)
            pts=[center+(v-center)*np.array([1,.3,1]) for v in pts]
            base=Polygon(*pts,color=CYAN,fill_color=CYAN,fill_opacity=0.12,stroke_width=2)
            apex=center+UP*2.25
            edges=VGroup(*[Line(apex,v,color=GOLD,stroke_width=1.7) for v in pts])
            shapes.add(VGroup(base,edges))
        self.play(LaggedStart(*[FadeIn(s) for s in shapes],lag_ratio=0.18),run_time=1.6)
        self.hide_intro_formula()
        self.caption("Toda pirâmide da sequência satisfaz V = A_b h / 3.")
        self.equation(r"V_n=\frac13A_{b,n}h")
        self.caption("Quando n cresce, a base poligonal tende ao círculo.")
        circle=Ellipse(width=1.9,height=.57,color=GREEN,stroke_width=4).move_to(centers[-1])
        self.play(Create(circle),run_time=0.7)
        self.equation(r"A_{b,n}\longrightarrow \pi r^2")
        self.caption("No limite, a pirâmide torna-se um cone.")
        self.equation(r"V=\frac13\pi r^2h")
        self.end()
