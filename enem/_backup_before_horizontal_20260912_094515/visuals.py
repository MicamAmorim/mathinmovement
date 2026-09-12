from manim import *
import numpy as np
import os
from font_utils import TEXT_FONT

CYAN="#55D6CF"; GOLD="#FFCC78"; WHITE="#EEF2FF"; MUTED="#9CAAC5"; GREEN="#8DE2A7"; PINK="#F28DB2"; RED="#FF7D7D"
IS_HORIZONTAL=os.getenv("ENEM_FORMAT","vertical").strip().lower()=="horizontal"

def P(x,y): return np.array([x,y,0.])

def math_label(tex, size=26, color=WHITE):
    return MathTex(tex,font_size=size,color=color)

def panel_title(text, x):
    return Text(text,font=TEXT_FONT,font_size=17,color=MUTED).move_to(P(x,2.7))

def source_figure(kind):
    """Schematic reconstructions of the official figures. They are intentionally vector-redrawn, not scans."""
    if kind=="triangle_instrument":
        a=P(-3.3,-1.0); b=P(-.7,-1.0); c=P(-2.0,1.5)
        instrument=VGroup(Line(a,b,color=CYAN),Line(b,c,color=CYAN),Line(c,a+RIGHT*.35,color=CYAN),
                          Line(a+RIGHT*.35,a+RIGHT*.7,color=GOLD))
        a2=P(.7,-1.1); b2=P(3.3,-1.1); c2=P(2.0,1.5)
        tri=Polygon(a2,b2,c2,color=CYAN,fill_opacity=.08)
        alt=DashedLine(c2,P(2,-1.1),color=GOLD)
        return VGroup(panel_title("Figura 1",-2),instrument,panel_title("Figura 2",2),tri,alt,
                      math_label(r"8\,\mathrm{cm}",24,GOLD).next_to(alt,RIGHT,buff=.12))
    if kind=="cup_frustum":
        trap=Polygon(P(-1.8,-1.6),P(1.8,-1.6),P(2.4,1.6),P(-2.4,1.6),color=CYAN,fill_opacity=.12)
        handle=Arc(radius=1.25,start_angle=-PI/2,angle=PI,color=GOLD).shift(RIGHT*2.1)
        h=DoubleArrow(P(-2.8,-1.6),P(-2.8,1.6),buff=0,color=GOLD,tip_length=.12)
        return VGroup(trap,handle,h,math_label("12",22,GOLD).next_to(h,LEFT),
                      math_label(r"D=10",22).move_to(P(0,2.0)),math_label(r"d=8",22).move_to(P(0,-2.0)))
    if kind=="castle_scale":
        castle=VGroup(Rectangle(width=3.4,height=2.1,color=CYAN,fill_opacity=.08).shift(UP*.25),
                      Polygon(P(-1.7,1.3),P(-1.05,2.0),P(-.4,1.3),color=CYAN),
                      Polygon(P(.4,1.3),P(1.05,2.0),P(1.7,1.3),color=CYAN))
        bridge=Line(P(-3,-1.8),P(3,-1.8),color=GOLD,stroke_width=7)
        return VGroup(castle,bridge,math_label(r"38{,}4\,m\to160\,cm",24,GOLD).next_to(bridge,DOWN),
                      math_label(r"1{,}68\,m\to7\,cm",24).move_to(P(0,-2.8)))
    if kind=="roads":
        ax=Axes(x_range=[0,55,10],y_range=[0,45,10],x_length=6.5,y_length=5.2,tips=False,
                axis_config={"color":MUTED,"stroke_width":2})
        A=ax.c2p(20,40); B=ax.c2p(50,20)
        dots=VGroup(Dot(A,color=CYAN),Dot(B,color=CYAN))
        labels=VGroup(math_label("A",22,CYAN).next_to(dots[0],UP),math_label("B",22,CYAN).next_to(dots[1],UP))
        xs=[20,30,35,40,50]; romans=["I","II","III","IV","V"]
        cand=VGroup()
        for x,r in zip(xs,romans):
            d=Dot(ax.c2p(x,0),radius=.06,color=GOLD); t=math_label(r,18,GOLD).next_to(d,DOWN,buff=.08); cand.add(VGroup(d,t))
        x4=ax.c2p(40,0)
        roads=VGroup(Line(A,x4,color=GREEN),Line(B,x4,color=GREEN))
        return VGroup(ax,roads,dots,labels,cand)
    if kind=="cone_dims":
        base=Ellipse(width=4.4,height=1.0,color=CYAN)
        apex=P(0,3.0)
        sides=VGroup(Line(base.get_left(),apex,color=CYAN),Line(base.get_right(),apex,color=CYAN))
        alt=DashedLine(P(0,0),apex,color=GOLD)
        return VGroup(base,sides,alt,math_label(r"8\,cm",24).move_to(P(0,-.75)),math_label(r"10\,cm",24,GOLD).next_to(alt,RIGHT))
    if kind=="stairs":
        pts=[P(-2.8,-1.8),P(2.8,-1.8),P(2.8,1.8),P(1.0,1.8),P(1.0,.6),P(-.8,.6),P(-.8,-.6),P(-2.8,-.6)]
        stair=Polygon(*pts,color=CYAN,fill_opacity=.10)
        return VGroup(stair,math_label(r"0{,}25",20,GOLD).move_to(P(1.9,2.12)),
                      math_label(r"0{,}20",20,GOLD).move_to(P(3.15,1.2)),math_label(r"1{,}0\,m",22).move_to(P(0,-2.25)))
    if kind=="moon_castle":
        moon=Circle(2.2,color=GOLD,fill_opacity=.10)
        roof=Polygon(P(0,0),P(-2.2,-1.8),P(2.2,-1.8),color=CYAN,fill_opacity=.18)
        center=Dot(ORIGIN,color=PINK)
        return VGroup(moon,roof,center,math_label("S",22,PINK).next_to(center,UP))
    if kind=="pool":
        outer=Square(5.5,color=GOLD,fill_opacity=.08); inner=Square(3.5,color=CYAN,fill_opacity=.15)
        return VGroup(outer,inner,DoubleArrow(P(1.75,0),P(2.75,0),buff=0,color=GOLD,tip_length=.12),
                      math_label(r"5\,m",22,GOLD).move_to(P(2.25,.35)))
    if kind=="sculpture":
        left=VGroup(Ellipse(width=3.0,height=.7,color=CYAN).shift(DOWN*1.4),Line(P(-1.5,-1.4),P(0,2.2),color=CYAN),Line(P(1.5,-1.4),P(0,2.2),color=CYAN),
                    DashedLine(P(-.5,.9),P(.5,.9),color=GOLD))
        right=VGroup(Polygon(P(.4,-1.4),P(3.0,-1.4),P(2.1,.9),P(1.3,.9),color=CYAN,fill_opacity=.1),
                     DashedLine(P(1.7,-1.4),P(1.7,.9),color=PINK,stroke_width=5))
        left.shift(LEFT*1.7); right.shift(RIGHT*.7)
        return VGroup(left,right,math_label(r"H=36,\ D=18",20).move_to(P(-1.7,-2.45)),math_label(r"d=6",20,GOLD).move_to(P(2.3,-2.45)))
    if kind=="ferris_choices":
        c=Circle(2.5,color=CYAN); hub=Dot(ORIGIN,color=MUTED); p=Dot(P(0,2.5),color=GOLD)
        spokes=VGroup(*[Line(ORIGIN,c.point_at_angle(k*TAU/8),color="#334568") for k in range(8)])
        ground=Line(P(-3,-3),P(3,-3),color=MUTED)
        return VGroup(c,spokes,hub,p,math_label("P",22,GOLD).next_to(p,UP),ground,CurvedArrow(P(.8,2.7),P(2.6,.6),angle=-.6,color=PINK))
    if kind=="cistern_table":
        cistern=VGroup(Circle(1.6,color=CYAN,fill_opacity=.08),Rectangle(width=3.2,height=1.3,color=CYAN,fill_opacity=.05).shift(DOWN*1.2)).shift(LEFT*2.1)
        rows=[("6 h","0,5 m"),("8 h","1,1 m"),("12 h","2,3 m"),("15 h","3,2 m")]
        table=VGroup(); y=1.5
        for t,h in rows:
            table.add(Text(f"{t}  →  {h}",font=TEXT_FONT,font_size=20,color=WHITE).move_to(P(2.0,y))); y-=.8
        return VGroup(cistern,table,Text("registros",font=TEXT_FONT,font_size=17,color=GOLD).move_to(P(2,2.2)))
    if kind=="mast":
        ground=Line(P(-3,-1.7),P(3,-1.7),color=MUTED); mast=Line(P(-1.1,-1.7),P(-1.1,2.5),color=CYAN,stroke_width=7); cable=Line(P(-1.1,1.8),P(2.4,-1.7),color=GOLD)
        return VGroup(ground,mast,cable,math_label("h",22,CYAN).move_to(P(-1.45,.1)),math_label(r"\alpha",25,GOLD).move_to(P(1.8,-1.35)))
    if kind=="graph_scale":
        ax=Axes(x_range=[0,12,2],y_range=[0,2,1],x_length=6.2,y_length=3.8,tips=False,axis_config={"color":MUTED})
        pts=[ax.c2p(*p) for p in [(0,0),(2,1),(7,1),(9,.5),(10,.5),(12,0)]]
        g=VMobject(color=CYAN,stroke_width=5).set_points_as_corners(pts)
        return VGroup(ax,g,math_label(r"1\,cm",22,GOLD).move_to(P(-3.5,1.1)))
    if kind=="pizza_pythagoras":
        tri=Polygon(P(-2.4,-1.6),P(2.1,-1.6),P(.9,1.4),color=WHITE)
        arcs=VGroup(ArcBetweenPoints(P(-2.4,-1.6),P(2.1,-1.6),angle=-PI,color=CYAN),
                    ArcBetweenPoints(P(-2.4,-1.6),P(.9,1.4),angle=PI,color=GOLD),
                    ArcBetweenPoints(P(.9,1.4),P(2.1,-1.6),angle=PI,color=PINK))
        return VGroup(tri,arcs,math_label(r"\alpha",24,GOLD).move_to(P(.75,1.05)))
    if kind=="sector":
        sec=Sector(radius=2.6,angle=PI/2,color=CYAN,fill_opacity=.20)
        return VGroup(sec,Line(ORIGIN,P(2.6,0),color=GOLD),math_label("R",22,GOLD).move_to(P(1.3,-.3)),math_label(r"\alpha",24).move_to(P(.6,.5)))
    if kind=="trapezoid_spin":
        trap=Polygon(P(0,-2),P(2.7,-1.2),P(1.7,1.8),P(0,2),color=CYAN,fill_opacity=.15)
        axis=Line(P(0,-2.8),P(0,2.8),color=GOLD,stroke_width=6)
        arr=CurvedArrow(P(.7,2.4),P(-.7,2.4),angle=PI/1.7,color=PINK)
        return VGroup(trap,axis,arr,math_label("PS",22,GOLD).move_to(P(-.4,0)))
    if kind=="cylinders_sheet":
        rect1=Rectangle(width=2.2,height=4.4,color=GOLD); rect2=Rectangle(width=4.4,height=2.2,color=GOLD)
        cyl1=VGroup(Ellipse(width=1.4,height=.45,color=CYAN),Line(P(-.7,0),P(-.7,-2.5),color=CYAN),Line(P(.7,0),P(.7,-2.5),color=CYAN),Ellipse(width=1.4,height=.45,color=CYAN).shift(DOWN*2.5)).scale(.65)
        cyl2=VGroup(Ellipse(width=2.5,height=.55,color=CYAN),Line(P(-1.25,0),P(-1.25,-1.4),color=CYAN),Line(P(1.25,0),P(1.25,-1.4),color=CYAN),Ellipse(width=2.5,height=.55,color=CYAN).shift(DOWN*1.4)).scale(.65)
        return VGroup(VGroup(rect1,cyl1.next_to(rect1,RIGHT,buff=.25)).shift(LEFT*1.8),VGroup(rect2,cyl2.next_to(rect2,DOWN,buff=.2)).shift(RIGHT*1.6)).scale(.72)
    if kind=="circle_patrol":
        c=Circle(2.7,color=CYAN); p=Dot(c.point_at_angle(PI/2),color=GOLD); arc=Arc(radius=2.7,start_angle=PI/2-.42,angle=.84,color=PINK,stroke_width=10)
        return VGroup(c,arc,p,math_label("P",22,GOLD).next_to(p,UP),math_label(r"400\,m",22,PINK).move_to(P(0,2.0)))
    return VGroup(Rectangle(width=5.5,height=3.5,color=CYAN),Text("Figura",font=TEXT_FONT,font_size=22,color=MUTED))

def ferris_alternatives():
    group=VGroup()
    def one(label,mode):
        ax=Axes(x_range=[0,4,1],y_range=[0,2.6,1],x_length=3.45 if IS_HORIZONTAL else 4.6,y_length=1.2 if IS_HORIZONTAL else 1.35,tips=False,
                axis_config={"color":"#52617C","stroke_width":1.5})
        if mode=='cos':
            curve=ax.plot(lambda x:1.5+.75*np.cos(np.pi*x),x_range=[0,4],color=CYAN,stroke_width=3)
        elif mode=='zig':
            pts=[ax.c2p(*p) for p in [(0,2.25),(1,.75),(2,2.25),(3,.75),(4,2.25)]]
            curve=VMobject(color=CYAN,stroke_width=3).set_points_as_corners(pts)
        elif mode=='plateau':
            pts=[ax.c2p(*p) for p in [(0,2.25),(.6,.8),(1.1,.8),(1.7,2.25),(2.3,2.25),(2.9,.8),(3.4,.8),(4,2.25)]]
            curve=VMobject(color=CYAN,stroke_width=3).set_points_as_corners(pts)
        elif mode=='downpar':
            curve=ax.plot(lambda x:.8+1.35*(1-(2*((x%1.33)/1.33)-1)**2),x_range=[0,4],color=CYAN,stroke_width=3)
        else:
            curve=ax.plot(lambda x:.75+1.35*(2*((x%2)/2)-1)**2,x_range=[0,4],color=CYAN,stroke_width=3)
        lab=Text(label,font=TEXT_FONT,font_size=19,color=GOLD).next_to(ax,LEFT,buff=.25)
        return VGroup(lab,ax,curve)
    choices=[one(label,mode) for label,mode in zip("ABCDE",['cos','zig','plateau','downpar','uppar'])]
    if IS_HORIZONTAL:
        top=VGroup(*choices[:3]).arrange(RIGHT,buff=.45)
        bottom=VGroup(*choices[3:]).arrange(RIGHT,buff=.65)
        group=VGroup(top,bottom).arrange(DOWN,buff=.42)
    else:
        group=VGroup(*choices).arrange(DOWN,buff=.25,aligned_edge=LEFT)
    return group

def concept_diagram(kind):
    if kind=="equilateral":
        tri=Polygon(P(-2,-1.3),P(2,-1.3),P(0,2.1),color=CYAN,fill_opacity=.15); alt=DashedLine(P(0,-1.3),P(0,2.1),color=GOLD)
        return VGroup(tri,alt,math_label(r"8\,cm",25,GOLD).next_to(alt,RIGHT),math_label(r"\ell/2",25).move_to(P(-1,-1.65)))
    if kind in ("cone_frustum","trapezoid_spin"):
        trap=Polygon(P(-2,-1.5),P(2,-1.5),P(1,1.7),P(-1,1.7),color=CYAN,fill_opacity=.18); axis=DashedLine(P(0,-2.1),P(0,2.3),color=GOLD)
        return VGroup(trap,axis,math_label("R",25,GOLD).move_to(P(1,-1.85)),math_label("r",25).move_to(P(.5,2.05)))
    if kind=="shape_areas":
        return VGroup(RegularPolygon(3,radius=.9,color=CYAN),Square(1.5,color=GOLD),Circle(.85,color=GREEN)).arrange(RIGHT,buff=.7)
    if kind in ("box","pool","stairs"):
        rect=Rectangle(width=5.5,height=3.3,color=CYAN,fill_opacity=.12); lines=VGroup(*[Line(P(-2.75+i*1.1,-1.65),P(-2.75+i*1.1,1.65),color=MUTED) for i in range(1,5)])
        return VGroup(rect,lines,math_label("A_b",28,GOLD).move_to(P(0,-2)),math_label("h",28,GOLD).move_to(P(3.2,0)))
    if kind in ("cylinder","cylinder_compare","cylinder_sphere","cylinders_sheet"):
        e1=Ellipse(width=4,height=1,color=CYAN).shift(UP*1.5); e2=e1.copy().shift(DOWN*3); sides=VGroup(Line(P(-2,1.5),P(-2,-1.5),color=CYAN),Line(P(2,1.5),P(2,-1.5),color=CYAN)); r=Line(ORIGIN,P(2,0),color=GOLD)
        return VGroup(e1,e2,sides,r,math_label("r",25,GOLD).next_to(r,UP),math_label("h",25,GOLD).move_to(P(2.4,0)))
    if kind=="scale":
        small=Square(1.4,color=GOLD).shift(LEFT*2); large=Square(3,color=CYAN).shift(RIGHT*1.2); return VGroup(small,large,Arrow(small.get_right(),large.get_left(),color=WHITE),math_label("k",30,GREEN))
    if kind=="reflection":
        ax=Axes(x_range=[0,55,10],y_range=[-25,45,10],x_length=6.2,y_length=6.0,tips=False,axis_config={"color":MUTED}); A=ax.c2p(20,40);B=ax.c2p(50,20);Br=ax.c2p(50,-20);X=ax.c2p(40,0)
        return VGroup(ax,Dot(A,color=CYAN),Dot(B,color=CYAN),Dot(Br,color=GOLD),DashedLine(B,Br,color=GOLD),Line(A,Br,color=GREEN),Dot(X,color=PINK),math_label("IV",20,PINK).next_to(Dot(X),DOWN))
    if kind=="sphere_scale": return VGroup(Circle(.8,color=GOLD),Circle(1.6,color=CYAN)).arrange(RIGHT,buff=1)
    if kind=="cone": return source_figure("cone_dims")
    if kind=="sector": return source_figure("sector")
    if kind=="ferris":
        c=Circle(2,color=CYAN); p=Dot(P(0,2),color=GOLD); axes=Axes(x_range=[0,6],y_range=[0,3],x_length=4,y_length=2.2,tips=False).shift(DOWN*3); graph=axes.plot(lambda x:1.5+np.cos(x),x_range=[0,6],color=GREEN)
        return VGroup(c,p,Line(ORIGIN,P(0,2),color=GOLD),axes,graph)
    if kind=="mast": return source_figure("mast")
    if kind=="graph_scale": return source_figure("graph_scale")
    if kind=="pizza": return source_figure("pizza_pythagoras")
    if kind=="regular_polygons": return VGroup(RegularPolygon(3,radius=1,color=GOLD),Square(1.5,color=CYAN),RegularPolygon(6,radius=1.5,color=GREEN)).arrange(RIGHT,buff=.5)
    if kind=="circle_patrol": return source_figure("circle_patrol")
    return VGroup(Rectangle(width=5,height=3,color=CYAN),Text(kind,font=TEXT_FONT,font_size=20,color=MUTED))
