from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

class AreaPrismasPlanificacao(Base):
    def construct(self):
        self.header("21","Área de prismas retos",r"A_T=2A_b+P_bh","PRISMAS")
        self.hide_intro_formula()
        s=.9; h=1.5
        self.caption("Cada face lateral vira um retângulo: lado da base × altura.")
        # Orthographic projection of a regular hexagonal prism, then its metric net.
        p3=[np.array([s*np.cos(i*TAU/6),s*np.sin(i*TAU/6),0]) for i in range(6)]
        project=lambda p:P(1.4*p[0]+.5*p[1],.3*p[1]+p[2]-.7)
        faces=VGroup(*[Polygon(project(p3[i]),project(p3[(i+1)%6]),
            project(p3[(i+1)%6]+[0,0,h]),project(p3[i]+[0,0,h]),
            color=CYAN if i%2 else GOLD,fill_opacity=.18) for i in range(6)])
        self.play(LaggedStart(*[Create(f) for f in faces],lag_ratio=.15),run_time=3)
        self.caption("Da projeção do sólido para as medidas reais das faces.")
        targets=[Rectangle(width=s,height=h,color=CYAN if i%2 else GOLD,
                           fill_opacity=.18).move_to(P(-2.7+s*(i+.5),0)) for i in range(6)]
        for face,target in zip(faces,targets):
            self.play(Transform(face,target),run_time=.8)
        self.caption("As larguras somam o perímetro da base.")
        self.equation(r"A_L=(\ell_1+\cdots+\ell_n)h=P_bh",size=40)
        self.base_height(-2.7,2.7,-h/2,h/2,"P_b","h")
        self.caption("Faltam as duas bases congruentes.")
        bases=VGroup(*[Polygon(*regular_polygon_points(6,s,center=P(x,2)),
                       color=GOLD,fill_opacity=.25) for x in (-1.5,1.5)])
        self.play(LaggedStart(*[Create(b) for b in bases],lag_ratio=.5),run_time=2)
        self.equation(r"A_T=A_L+A_b+A_b")
        self.equation(r"A_T=P_bh+2A_b")
        self.end()

