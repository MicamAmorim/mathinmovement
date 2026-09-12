from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class EscalasComprimentosAreasVolumes(Base):
    def construct(self):
        self.header("18", "Escalas: comprimentos, áreas e volumes", r"L\to kL,\ A\to k^2A,\ V\to k^3V", "SEMELHANÇA")
        s1=Square(1.5,color=GOLD,fill_color=GOLD,fill_opacity=0.18).move_to(P(-2.2,0.5))
        s2=Square(3.0,color=CYAN,fill_color=CYAN,fill_opacity=0.14).move_to(P(1.4,0.5))
        self.caption("Se todos os comprimentos dobram, k = 2.")
        self.play(Create(s1),run_time=0.8)
        self.play(TransformFromCopy(s1,s2),run_time=1.1)
        labels=VGroup(safe_mathtex("L",30,GOLD).next_to(s1,DOWN),safe_mathtex("2L",30,CYAN).next_to(s2,DOWN))
        self.play(Write(labels),run_time=0.6)
        self.hide_intro_formula()
        self.caption("A área recebe o fator duas vezes.")
        grid=VGroup(
            Line(P(1.4,-1.0),P(1.4,2.0),color=MUTED,stroke_width=1.5),
            Line(P(-0.1,0.5),P(2.9,0.5),color=MUTED,stroke_width=1.5)
        )
        self.play(Create(grid),run_time=0.7)
        self.equation(r"A'=(2L)^2=4L^2=2^2A")
        self.caption("No volume, o fator aparece em três dimensões.")
        # Cubos em projeção isométrica simples.
        front=Square(1.5,color=GOLD).move_to(P(-1.8,0.2))
        back=front.copy().shift(P(0.55,0.55))
        edges=VGroup(*[Line(front.get_vertices()[i],back.get_vertices()[i],color=GOLD) for i in range(4)])
        cube=VGroup(front,back,edges).scale(0.85).move_to(P(0,0.15))
        self.play(FadeOut(s1),FadeOut(s2),FadeOut(grid),FadeIn(cube),run_time=0.8)
        self.play(FadeOut(labels),FadeOut(cube))
        self.caption("Duas unidades em cada direção: 2 × 2 × 2 cubinhos.")
        cubes=VGroup()
        for z in (1,0):
            for y in (0,1):
                for x in (0,1):
                    f=Square(.9,color=GOLD,fill_opacity=.12).move_to(P(x*.9-.8+z*.35,y*.9-.5+z*.35))
                    b=f.copy().shift(P(.35,.35))
                    e=VGroup(*[Line(f.get_vertices()[i],b.get_vertices()[i],color=GOLD) for i in range(4)])
                    cubes.add(VGroup(f,b,e))
        self.play(LaggedStart(*[Create(c) for c in cubes],lag_ratio=.25),run_time=4)
        self.equation(r"V'=2\cdot2\cdot2\,V=8V")
        self.equation(r"V'=(kL)^3=k^3V")
        self.caption("Regra geral: expoente = dimensão medida.")
        self.equation(r"L:k\qquad A:k^2\qquad V:k^3")
        self.end()
