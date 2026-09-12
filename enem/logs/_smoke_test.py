from manim import *
class SmokeTest(Scene):
    def construct(self):
        self.add(Text('ENEM', font='Segoe UI'))
        self.add(MathTex(r'x^2+y^2=1').shift(DOWN))
