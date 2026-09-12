from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common import *

class VolumePiramide(Base):
    def construct(self):
        self.header("26", "Volume da pirâmide", r"V=\frac13A_bh", "PIRÂMIDES")
        # Cubo esquemático.
        front=Square(3.3,color=WHITE).move_to(P(-0.55,-0.35))
        back=front.copy().shift(P(1.0,0.8))
        con=VGroup(*[Line(front.get_vertices()[i],back.get_vertices()[i],color=WHITE,stroke_width=2) for i in range(4)])
        self.caption("Um cubo pode ser particionado em três pirâmides congruentes.")
        self.play(Create(front),Create(back),Create(con),run_time=1.4)
        O=front.get_vertices()[0]
        # Três faces-base opostas ao vértice O, destacadas conceitualmente.
        p1=Polygon(back.get_vertices()[0],back.get_vertices()[1],back.get_vertices()[2],back.get_vertices()[3],
                   color=CYAN,fill_color=CYAN,fill_opacity=0.15)
        p2=Polygon(front.get_vertices()[1],front.get_vertices()[2],back.get_vertices()[2],back.get_vertices()[1],
                   color=GOLD,fill_color=GOLD,fill_opacity=0.14)
        p3=Polygon(front.get_vertices()[3],front.get_vertices()[2],back.get_vertices()[2],back.get_vertices()[3],
                   color=GREEN,fill_color=GREEN,fill_opacity=0.13)
        self.play(FadeIn(p1),FadeIn(p2),FadeIn(p3),run_time=0.8)
        rays=VGroup(*[Line(O,v,color=GOLD,stroke_width=2) for v in
                       (front.get_vertices()[2],back.get_vertices()[1],
                        back.get_vertices()[2],back.get_vertices()[3])])
        self.play(Create(rays),FadeIn(Dot(O,color=RED)),run_time=2)
        self.caption("As três bases têm o mesmo vértice comum O.")
        for face in (p1,p2,p3):
            self.pulse(face)
        self.hide_intro_formula()
        self.caption("As três têm a mesma base s² e altura s, por simetria.")
        self.equation(r"V_{cubo}=3V_{pir}")
        self.equation(r"s^3=3V_{pir}")
        self.caption("Logo, numa pirâmide de base quadrada: V = s²·s/3.")
        self.equation(r"V_{pir}=\frac{s^3}{3}=\frac{A_bh}{3}")
        self.caption("O mesmo fator 1/3 vale para qualquer base, por Cavalieri.")
        self.caption("Esticar a altura multiplica os dois volumes pelo mesmo fator.")
        self.caption("A uma fração t da altura, cada seção tem escala linear t.")
        self.equation(r"A(t)=t^2 A_b,\quad 0\leq t\leq1")
        self.caption("Bases de mesma área e alturas iguais dão seções iguais.")
        self.equation(r"A_1(t)=t^2A_b=A_2(t)")
        self.caption("Cavalieri permite trocar a base, mantendo área e altura.")
        self.equation(r"V=\frac13A_bh")
        self.end()
