from manim import *
from pathlib import Path
import json, os, textwrap
import numpy as np
from visuals import source_figure, ferris_alternatives, concept_diagram
from font_utils import TEXT_FONT

VIDEO_LAYOUT=os.getenv("ENEM_FORMAT","vertical").strip().lower()
if VIDEO_LAYOUT not in {"vertical","horizontal"}:
    VIDEO_LAYOUT="vertical"
IS_HORIZONTAL=VIDEO_LAYOUT=="horizontal"

def _lv(vertical,horizontal):
    return horizontal if IS_HORIZONTAL else vertical

config.frame_width=_lv(9,16)
config.frame_height=_lv(16,9)
config.background_color="#0B1020"
BG="#0B1020"; WHITE="#EEF2FF"; CYAN="#55D6CF"; GOLD="#FFCC78"
MUTED="#9CAAC5"; GREEN="#8DE2A7"; RED="#FF7D7D"; PINK="#F28DB2"
ROOT=Path(__file__).resolve().parent
QUESTIONS={q["canonical_id"]:q for q in json.loads((ROOT/"data/questions.json").read_text(encoding="utf8"))}
NARRATIONS=json.loads((ROOT/"narrations/narrations.json").read_text(encoding="utf8")) if (ROOT/"narrations/narrations.json").exists() else {}
AUDIO_MANIFEST=json.loads((ROOT/"audio/manifest.json").read_text(encoding="utf8")) if (ROOT/"audio/manifest.json").exists() else {}
FAST_PREVIEW=os.getenv("ENEM_FAST_PREVIEW","0").lower() in {"1","true","yes"}


def P(x,y): return np.array([x,y,0.])

def fit(mob,w=None,h=None):
    if w is None: w=_lv(7.5,13.5)
    if mob.width>w: mob.scale_to_fit_width(w)
    if h and mob.height>h: mob.scale_to_fit_height(h)
    return mob

def mt(tex,size=45,color=WHITE): return fit(MathTex(tex,font_size=size,color=color),_lv(7.5,13.2))

def txt(s,size=26,color=WHITE,width=46,weight=NORMAL):
    wrapped="\n".join(textwrap.fill(p,width) for p in str(s).splitlines())
    return fit(Text(wrapped,font=TEXT_FONT,font_size=size,color=color,weight=weight,line_spacing=.9),_lv(7.5,13.5))

class ENEMSolutionScene(Scene):
    SPEC=None

    def wait(self,duration=1,**kw):
        kw.setdefault("frozen_frame",True)
        return super().wait(duration,**kw)

    def construct(self):
        self.s=self.SPEC; self.q=QUESTIONS[self.s["id"]]
        self.narr={x["key"]:x for x in NARRATIONS.get(self.s["id"],{}).get("segments",[])}
        self.source_screen()
        self.statement_screen()
        if self.s.get("statement_visual"): self.figure_screen()
        self.options_screen()
        self.data_screen()
        self.goal_screen()
        self.visual_screen()
        self.solution_screen()

    # ---------- narration / audio synchronization ----------
    def segment_duration(self,key,default=2.5):
        # Do not call this method ``duration``: Manim's Scene lifecycle uses an
        # instance attribute with that name, which can be None and mask methods.
        rec=AUDIO_MANIFEST.get(self.s["id"],{}).get(key,{})
        raw=rec.get("duration")
        if raw in (None, ""):
            raw=self.narr.get(key,{}).get("estimated_seconds",default)
        try:
            d=float(raw)
        except (TypeError, ValueError):
            d=float(default)
        return max(.35,d*(.16 if FAST_PREVIEW else 1.0))

    def audio_path(self,key):
        rec=AUDIO_MANIFEST.get(self.s["id"],{}).get(key,{})
        rel=rec.get("file")
        if rel:
            p=ROOT/rel
            if p.exists(): return p
        p=ROOT/"audio"/self.s["id"]/f"{key}.mp3"
        return p if p.exists() else None

    def speak(self,key,animations=None,run_time=None):
        duration=self.segment_duration(key)
        audio=self.audio_path(key)
        if audio and not FAST_PREVIEW: self.add_sound(str(audio))
        if animations:
            rt=min(duration*.52,3.8) if run_time is None else min(float(run_time),duration)
            rt=max(.25,rt)
            self.play(*animations,run_time=rt)
            if duration>rt: self.wait(duration-rt)
        else:
            self.wait(duration)
        return duration

    def narration_text(self,key,fallback=""):
        return self.narr.get(key,{}).get("text",fallback)

    # ---------- scene blocks ----------
    def source_screen(self):
        q=self.q
        tag=txt("QUESTÃO COMENTADA",20,CYAN,weight=BOLD).move_to(P(0,_lv(5.8,2.9)))
        code=txt(f'{q["canonical_id"]} — Q{q["question_number"]}',_lv(34,38),WHITE,weight=BOLD)
        src=txt(f'Fonte: ENEM {q["year"]} · {q["caderno"]}',21,MUTED)
        group=VGroup(code,src).arrange(DOWN,buff=.35).move_to(P(0,_lv(.3,0)))
        self.speak("source",[FadeIn(tag,shift=DOWN*.15),Write(code),FadeIn(src)])
        self.play(FadeOut(VGroup(tag,group)),run_time=.45)

    def statement_screen(self):
        heading=txt("1 · LEIA O PROBLEMA",20,CYAN,weight=BOLD).move_to(P(0,_lv(6.7,3.65))); self.add(heading)
        segs=[v for k,v in sorted(self.narr.items()) if k.startswith("statement_")]
        for i,seg in enumerate(segs,1):
            card=RoundedRectangle(width=_lv(7.7,14.2),height=_lv(10.7,5.6),corner_radius=.18,color="#24324E",fill_color="#111A30",fill_opacity=1)
            body=txt(seg["text"],_lv(24,23),WHITE,width=_lv(51,92)); fit(body,_lv(7.1,13.2),_lv(9.4,4.45)); body.move_to(card)
            page_no=txt(f"{i}/{len(segs)}",16,MUTED).move_to(P(0,_lv(-5.25,-2.55))); g=VGroup(card,body,page_no)
            self.speak(seg["key"],[FadeIn(g,shift=UP*.12)])
            self.play(FadeOut(g),run_time=.35)
        self.play(FadeOut(heading),run_time=.25)

    def figure_screen(self):
        h=txt("2 · FIGURA DA QUESTÃO",20,CYAN,weight=BOLD).move_to(P(0,_lv(6.7,3.65)))
        sub=txt("reconstrução vetorial esquemática",16,MUTED).next_to(h,DOWN,buff=.12)
        fig=source_figure(self.s["statement_visual"])
        note=txt(self.q.get("visual_description",""),_lv(18,19),MUTED,width=_lv(52,46))
        if IS_HORIZONTAL:
            fit(fig,8.0,5.25); fig.move_to(P(-3.25,-.15))
            fit(note,5.15,4.5); note.move_to(P(4.35,-.1))
        else:
            fit(fig,7.2,9.0); fig.move_to(P(0,.3))
            fit(note,7.2,2.2); note.move_to(P(0,-5.1))
        children=list(fig) if len(fig)>0 else [fig]
        anim=[FadeIn(VGroup(h,sub)),LaggedStart(*[Create(x) if isinstance(x,VMobject) else FadeIn(x) for x in children],lag_ratio=.09),FadeIn(note)]
        self.speak("figure",anim)
        self.play(FadeOut(VGroup(h,sub,fig,note)),run_time=.4)

    def options_screen(self):
        h=txt("3 · ALTERNATIVAS",20,CYAN,weight=BOLD).move_to(P(0,_lv(6.7,3.65))); self.add(h)
        if self.s["id"]=="ENEM-2023-MT-29":
            body=ferris_alternatives(); fit(body,_lv(7.1,13.6),_lv(11.0,5.55)); body.move_to(P(_lv(.2,0),0))
            self.speak("options",[FadeIn(body,shift=UP*.1)])
            self.play(FadeOut(VGroup(h,body)),run_time=.35); return
        option_lines=[f"{letter}) {value}" for letter,value in self.q.get("options",{}).items()]
        body=txt("\n".join(option_lines),_lv(22,21),WHITE,width=_lv(51,90)); fit(body,_lv(7.1,13.1),_lv(10.2,4.75)); body.move_to(P(0,0))
        box=RoundedRectangle(width=_lv(7.7,14.2),height=_lv(10.9,5.6),corner_radius=.18,color="#24324E",fill_color="#111A30",fill_opacity=1)
        self.speak("options",[FadeIn(box),FadeIn(body,shift=UP*.1)])
        self.play(FadeOut(VGroup(h,box,body)),run_time=.35)

    def data_screen(self):
        h=txt("4 · SEPARE OS DADOS",20,CYAN,weight=BOLD).move_to(P(0,_lv(6.7,3.65))); self.add(h)
        items=[]
        for datum in self.s["data"]:
            if IS_HORIZONTAL:
                t=txt(datum,22,WHITE,width=44); fit(t,6.05,1.6)
                box=RoundedRectangle(width=6.55,height=max(.8,t.height+.35),corner_radius=.13,color="#334568",fill_color="#111A30",fill_opacity=1)
            else:
                t=txt(datum,24,WHITE,width=38)
                box=RoundedRectangle(width=7.5,height=max(.8,t.height+.35),corner_radius=.13,color="#334568",fill_color="#111A30",fill_opacity=1)
            t.move_to(box); items.append(VGroup(box,t))
        if IS_HORIZONTAL:
            rows=VGroup()
            for i in range(0,len(items),2):
                rows.add(VGroup(*items[i:i+2]).arrange(RIGHT,buff=.32))
            cards=rows.arrange(DOWN,buff=.25).move_to(P(0,-.05)); fit(cards,13.7,5.35)
        else:
            cards=VGroup(*items).arrange(DOWN,buff=.2).move_to(P(0,.4)); fit(cards,7.6,10.8)
        self.speak("data",[LaggedStart(*[FadeIn(c,shift=RIGHT*.2) for c in items],lag_ratio=.22)])
        self.play(FadeOut(VGroup(h,cards)),run_time=.35)

    def goal_screen(self):
        h=txt("5 · ESTRATÉGIA",20,CYAN,weight=BOLD).move_to(P(0,_lv(6.7,3.65))); self.add(h)
        if IS_HORIZONTAL:
            goal=txt(self.s["goal"],27,GOLD,width=40,weight=BOLD); fit(goal,6.25,1.55)
            hook=txt(self.s.get("hook",""),20,MUTED,width=42); fit(hook,6.25,1.8)
            left=VGroup(goal,hook).arrange(DOWN,aligned_edge=LEFT,buff=.55).move_to(P(-3.65,.2))
            chain=VGroup(*[txt(f"{i}. {item}",21,WHITE,width=43) for i,item in enumerate(self.s["plan"],1)])
            chain.arrange(DOWN,aligned_edge=LEFT,buff=.38).move_to(P(3.55,-.05)); fit(chain,6.35,5.25)
            divider=Line(P(0,-2.7),P(0,2.55),color="#24324E",stroke_width=2)
            self.speak("strategy",[Write(goal),FadeIn(hook),Create(divider),LaggedStart(*[FadeIn(x,shift=UP*.12) for x in chain],lag_ratio=.3)])
            self.play(FadeOut(VGroup(h,left,chain,divider)),run_time=.4)
        else:
            goal=txt(self.s["goal"],29,GOLD,width=42,weight=BOLD).move_to(P(0,4.5))
            hook=txt(self.s.get("hook",""),22,MUTED,width=47).move_to(P(0,2.7))
            chain=VGroup(*[txt(f"{i}. {item}",23,WHITE,width=43) for i,item in enumerate(self.s["plan"],1)])
            chain.arrange(DOWN,aligned_edge=LEFT,buff=.42).move_to(P(0,-.5)); fit(chain,7.4,6.8)
            self.speak("strategy",[Write(goal),FadeIn(hook),LaggedStart(*[FadeIn(x,shift=UP*.12) for x in chain],lag_ratio=.3)])
            self.play(FadeOut(VGroup(h,goal,hook,chain)),run_time=.4)

    def visual_screen(self):
        h=txt("6 · MODELE VISUALMENTE",20,CYAN,weight=BOLD).move_to(P(0,_lv(6.7,3.65))); self.add(h)
        diagram=concept_diagram(self.s.get("visual","generic"))
        note=txt(self.s["visual_note"],_lv(22,20),MUTED,width=_lv(46,45))
        if IS_HORIZONTAL:
            diagram.move_to(P(-3.3,-.05)); fit(diagram,8.0,5.25)
            fit(note,5.2,4.6); note.move_to(P(4.3,-.05))
        else:
            diagram.move_to(P(0,.5)); fit(diagram,7.2,9.2)
            note.move_to(P(0,-5.15))
        children=list(diagram) if len(diagram)>0 else [diagram]
        self.speak("visual",[LaggedStart(*[Create(x) if isinstance(x,VMobject) else FadeIn(x) for x in children],lag_ratio=.10),FadeIn(note)])
        # A short visual emphasis keeps the scene from feeling like a static slide.
        if not FAST_PREVIEW and len(diagram)>0:
            self.play(Indicate(diagram[0],color=GOLD,scale_factor=1.04),run_time=.65)
        self.play(FadeOut(VGroup(h,diagram,note)),run_time=.35)

    def solution_screen(self):
        h=txt("7 · RESOLVA PASSO A PASSO",20,CYAN,weight=BOLD).move_to(P(0,_lv(6.7,3.65))); self.add(h)
        current=None
        for i,step in enumerate(self.s["steps"],1):
            label=txt(step[0],_lv(22,21),GOLD,width=_lv(44,72)).move_to(P(0,_lv(4.9,2.55)))
            equation=mt(step[1],step[2] if len(step)>2 else _lv(45,43)).move_to(P(0,_lv(.2,.1)))
            if current is None: anim=[FadeIn(label),Write(equation)]
            else: anim=[FadeOut(current[0]),FadeIn(label),ReplacementTransform(current[1],equation)]
            self.speak(f"step_{i:02d}",anim)
            current=(label,equation)
        option=self.q.get("options",{}).get(self.q["answer"],"")
        answer=txt(f'Alternativa {self.q["answer"]}: {option}',_lv(30,27),GREEN,width=_lv(42,76),weight=BOLD).move_to(P(0,_lv(-4.5,-2.55)))
        check=SurroundingRectangle(answer,color=GREEN,buff=.22)
        self.speak("answer",[FadeIn(answer),Create(check)])
