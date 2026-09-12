from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

class RelacaoEulerPoliedros(Base):
    def construct(self):
        self.header("19","Relação de Euler",r"V-E+F=2","POLIEDROS")
        self.hide_intro_formula()
        self.caption("Retire uma face do cubo e abra a superfície no plano.")
        verts=[P(-2.5,-2),P(2.5,-2),P(2.5,2),P(-2.5,2),
               P(-1,-.8),P(1,-.8),P(1,.8),P(-1,.8)]
        pairs=[(i,(i+1)%4) for i in range(4)]+[(i+4,(i+1)%4+4) for i in range(4)]+[(i,i+4) for i in range(4)]
        lines=[Line(verts[a],verts[b],color=CYAN) for a,b in pairs]
        dots=VGroup(*[Dot(p,color=GOLD) for p in verts])
        self.play(LaggedStart(*[Create(l) for l in lines],lag_ratio=.1),FadeIn(dots),run_time=3)
        self.equation(r"V-E+F_{\rm int}=8-12+5=1",size=40)
        self.caption("Apague uma aresta de um ciclo: uma região desaparece junto.")
        for idx,remaining in zip((4,5,6,7,0),(4,3,2,1,0)):
            self.play(FadeOut(lines[idx]),run_time=1)
            self.equation(rf"8-{7+remaining}+{remaining}=1")
        self.caption("Restou uma árvore. Remova folhas e suas arestas.")
        for v,edge in ((4,8),(7,11),(0,3),(3,2),(6,10),(2,1),(5,9)):
            self.play(FadeOut(dots[v]),FadeOut(lines[edge]),run_time=.8)
        self.equation(r"1-0+0=1")
        self.caption("Cada remoção preserva V − E + F interno.")
        self.caption("Em uma superfície convexa, o mesmo processo se aplica.")
        self.caption("Devolva a face retirada: o total aumenta em 1.")
        self.equation(r"V-E+F=1+1=2")
        self.end()

