from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

class ComprimentoCircunferenciaPi(Base):
    def construct(self):
        self.header("07","Circunferência e π",r"C=\pi d=2\pi r","CÍRCULO")
        self.hide_intro_formula()
        start=P(-PI,-1)
        wheel=Circle(radius=1,color=CYAN).move_to(start+UP)
        spoke=Line(start+UP,start,color=GOLD,stroke_width=5)
        floor=Line(start+LEFT*.2,start+RIGHT*(TAU+.2),color=MUTED)
        self.caption("Uma volta completa, sem escorregar.")
        self.play(Create(wheel),Create(spoke),Create(floor),run_time=2)
        diameter=Line(start+P(-1,1),start+P(1,1),color=GOLD)
        dlabel=safe_mathtex("d=2r",30,GOLD).next_to(diameter,UP)
        self.play(Create(diameter),Write(dlabel))
        self.wait(2)
        self.play(FadeOut(diameter),FadeOut(dlabel))
        t=ValueTracker(0)
        wheel.add_updater(lambda m:m.move_to(start+P(t.get_value(),1)))
        spoke.add_updater(lambda m:m.put_start_and_end_on(start+P(t.get_value(),1),
            start+P(t.get_value()-np.sin(t.get_value()),1-np.cos(t.get_value()))))
        trail=always_redraw(lambda:Line(start,start+RIGHT*max(.001,t.get_value()),color=CYAN,stroke_width=6))
        self.add(trail)
        self.play(t.animate.set_value(TAU),run_time=7,rate_func=linear)
        for m in (wheel,spoke,trail): m.clear_updaters()
        self.caption("A distância percorrida é o comprimento C.")
        self.play(FadeOut(wheel),FadeOut(spoke))
        self.caption("Compare com diâmetros de tamanho d = 2r.")
        for i in range(3):
            unit=Line(start+P(2*i,.7),start+P(2*i+2,.7),color=GOLD,stroke_width=6)
            self.play(Create(unit),Write(safe_mathtex("d",32,GOLD).next_to(unit,UP)),run_time=1)
        self.play(Create(Line(start+P(6,.7),start+P(TAU,.7),color=PINK,stroke_width=6)))
        self.equation(r"C/d\approx3{,}14159")
        self.caption("A razão não muda com a escala. Seu nome é π.")
        self.equation(r"\pi:=C/d")
        self.caption("O diâmetro mede dois raios.")
        self.equation(r"C=\pi d=2\pi r")
        self.end()
