from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

class VolumeEsfera(Base):
    def construct(self):
        self.header("29","Volume da esfera",r"V=\frac43\pi R^3","ESFERA")
        self.hide_intro_formula()
        R=1.4; left=P(-2,-.8); right=P(2,-.8)
        hemi=VGroup(Arc(radius=R,start_angle=0,angle=PI,arc_center=left,color=CYAN),
                   Line(left+LEFT*R,left+RIGHT*R,color=CYAN))
        cyl=Rectangle(width=2*R,height=R,color=GOLD).move_to(right+UP*R/2)
        cone=Polygon(right,right+P(-R,R),right+P(R,R),color=RED,fill_opacity=.18)
        self.caption("Cortes axiais: semiesfera e cilindro menos cone.")
        self.play(Create(hemi),Create(cyl),Create(cone),run_time=2)
        self.caption("O cone tem vértice na base: seu raio na altura y é y.")
        t=ValueTracker(.55)
        section=always_redraw(lambda:VGroup(
            Line(left+P(-np.sqrt(R*R-t.get_value()**2),t.get_value()),
                 left+P(np.sqrt(R*R-t.get_value()**2),t.get_value()),color=CYAN,stroke_width=7),
            Line(right+P(-R,t.get_value()),right+P(-t.get_value(),t.get_value()),color=CYAN,stroke_width=7),
            Line(right+P(t.get_value(),t.get_value()),right+P(R,t.get_value()),color=CYAN,stroke_width=7)))
        self.add(section)
        self.equation(r"\rho^2+y^2=R^2")
        self.caption("Ao girar: disco à esquerda, coroa à direita.")
        self.equation(r"A_{\rm disco}=\pi(R^2-y^2)")
        self.equation(r"A_{\rm coroa}=\pi R^2-\pi y^2")
        self.play(t.animate.set_value(1.25),run_time=3)
        self.play(t.animate.set_value(.2),run_time=3)
        section.clear_updaters()
        self.caption("Áreas iguais em toda altura: Cavalieri iguala os volumes.")
        self.equation(r"V_{\rm hemi}=\pi R^2R-\frac13\pi R^2R",size=40)
        self.equation(r"V_{\rm hemi}=\frac23\pi R^3")
        self.caption("Duas metades formam a esfera.")
        self.equation(r"V=2V_{\rm hemi}=\frac43\pi R^3")
        self.end()

