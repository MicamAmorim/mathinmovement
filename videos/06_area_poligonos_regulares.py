from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

class AreaPoligonosRegulares(Base):
    def construct(self):
        self.header("06","Área de polígonos regulares",r"A=\frac{Pa}{2}","ÁREAS")
        pts=regular_polygon_points(6,2.3,start_angle=PI/6)
        sectors=VGroup(*[Polygon(ORIGIN,pts[i],pts[(i+1)%6],color=CYAN if i%2 else GOLD,
                        fill_opacity=.22) for i in range(6)])
        self.caption("Do centro aos vértices: seis triângulos iguais.")
        self.play(LaggedStart(*[Create(s) for s in sectors],lag_ratio=.2),run_time=3)
        mid=(pts[0]+pts[1])/2
        apo=Line(ORIGIN,mid,color=GOLD)
        self.play(Create(apo),Write(safe_mathtex("a",34,GOLD).next_to(apo,LEFT)),
                  Write(safe_mathtex(r"\ell",34).next_to(Line(pts[0],pts[1]),UP)))
        self.hide_intro_formula()
        self.caption("O apótema é perpendicular ao lado: ele é a altura.")
        self.pulse(sectors[0])
        self.equation(r"A_1=\frac{\ell a}{2}")
        self.caption("Some a área de cada triângulo, um por vez.")
        for i,s in enumerate(sectors):
            self.pulse(s)
            self.equation(str(i+1)+r"\cdot\frac{\ell a}{2}",size=44)
        self.caption("Para n lados, são n parcelas iguais.")
        self.equation(r"A=n\frac{\ell a}{2}=\frac{(n\ell)a}{2}")
        self.play(LaggedStart(*[Create(Line(pts[i],pts[(i+1)%6],color=GREEN,stroke_width=6))
                               for i in range(6)],lag_ratio=.2),run_time=2)
        self.caption("A soma dos lados é o perímetro: P = nℓ.")
        self.equation(r"A=\frac{Pa}{2}")
        self.end()

