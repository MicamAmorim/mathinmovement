import ast, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
from specs import SPECS
from render_all import SCENES
questions={q["canonical_id"]:q for q in json.loads((ROOT/"data/questions.json").read_text(encoding="utf8"))}
narr=json.loads((ROOT/"narrations/narrations.json").read_text(encoding="utf8"))
assert len(SPECS)==len(SCENES)==len(questions)==len(narr)==30
assert len({s["id"] for s in SPECS})==30
for i,s in enumerate(SPECS):
    q=questions[s["id"]]
    assert s["answer"]==q["answer"],(s["id"],s["answer"],q["answer"])
    assert s["data"] and s["plan"] and len(s["steps"])>=3
    assert bool(q.get("has_visual"))==bool(s.get("statement_visual")),(s["id"],q.get("has_visual"),s.get("statement_visual"))
    segments={x["key"] for x in narr[s["id"]]["segments"]}
    needed={"source","options","data","strategy","visual","answer"}|{f"step_{j:02d}" for j in range(1,len(s["steps"])+1)}
    if s.get("statement_visual"): needed.add("figure")
    assert needed<=segments,(s["id"],sorted(needed-segments))
    assert any(k.startswith("statement_") for k in segments),s["id"]
    file=ROOT/"videos"/SCENES[i][1]
    tree=ast.parse(file.read_text(encoding="utf8"))
    assert any(isinstance(n,ast.ClassDef) and n.name==SCENES[i][2] for n in tree.body)
# Regression guards for the two corrected questions.
q146=SPECS[0]; q145=SPECS[7]
assert any("8 cm" in d for d in q146["data"]) and all("7,7" not in d for d in q146["data"])
assert any("(20,40)" in d for d in q145["data"]) and any("(50,20)" in d for d in q145["data"])
for f in (ROOT/"common.py",ROOT/"visuals.py",ROOT/"specs.py",ROOT/"render_all.py",ROOT/"narration_builder.py",ROOT/"generate_voice.py"):
    ast.parse(f.read_text(encoding="utf8"))
# Horizontal patch guards: vertical remains the default and 16:9 is opt-in.
common_src=(ROOT/"common.py").read_text(encoding="utf8")
render_src=(ROOT/"render_all.py").read_text(encoding="utf8")
pipeline_src=(ROOT/"pipeline.py").read_text(encoding="utf8")
assert 'os.getenv("ENEM_FORMAT","vertical")' in common_src
assert 'choices=["vertical", "horizontal"]' in render_src
assert 'default="vertical"' in render_src
assert '1920,1080' in render_src and '1080,1920' in render_src
assert "media_horizontal" in render_src
assert "'--format',a.video_format" in pipeline_src
print("PASS: 30 questões, gabaritos, figuras, narrações, regressões críticas e layouts vertical/horizontal validados.")
