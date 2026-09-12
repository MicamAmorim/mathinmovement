from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

class AreaCirculo(Base):
    def construct(self):
        self.header("08","Área do círculo",r"A=\pi r^2","CÍRCULO")
        self.hide_intro_formula()
        r=1.65
        sectors=None
        for n in (8,16,32):
            if sectors is not None: self.play(FadeOut(sectors))
            alpha=TAU/n
            sectors=VGroup(*[Sector(radius=r,angle=alpha,start_angle=i*alpha,
                color=CYAN if i%2==0 else GOLD,fill_opacity=.35,stroke_width=1) for i in range(n)])
            self.caption(f"Divida o círculo em {n} setores iguais.")
            self.play(LaggedStart(*[Create(s) for s in sectors],lag_ratio=.04),run_time=2)
            self.caption("Gire e alterne as peças, sem deformá-las.")
            chord=2*r*np.sin(alpha/2)
            self.play(*[rigid_motion(s,(PI/2-alpha/2 if i%2==0 else -PI/2-alpha/2)-i*alpha,
                P((i//2)*chord+(chord/2 if i%2 else 0)
                -((n/2-.5)*chord)/2,-.8+(r*np.cos(alpha/2) if i%2 else 0)))
                for i,s in enumerate(sectors)],run_time=5)
            self.caption("As bordas curvas ficam cada vez mais planas.")
        self.caption("No limite: altura r e base igual à meia circunferência.")
        self.equation(r"b\to C/2=\pi r,\quad h\to r",size=44)
        self.equation(r"A=(\pi r)r=\pi r^2")
        self.end()
