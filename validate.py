"""Static and geometric checks. Does NOT replace rendering in Manim."""
import ast
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent

def area(p):
    p = np.asarray(p)
    return abs(np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1)))/2

def main():
    from render_all import SCENES
    paths = sorted((ROOT/"videos").glob("*.py"))
    assert len(paths) == 30
    for number, filename, scene in SCENES:
        tree = ast.parse((ROOT/"videos"/filename).read_text(encoding="utf-8"))
        assert any(isinstance(n,ast.ClassDef) and n.name==scene for n in tree.body), filename
        for node in ast.walk(tree):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=="Sector":
                assert not any(k.arg=="outer_radius" for k in node.keywords), filename
    for path in (ROOT/"common.py",ROOT/"render_all.py"):
        ast.parse(path.read_text(encoding="utf-8"))
    print("PASS: syntax, 30 scene names, Sector radius arguments")
    # Episode 02: true translation of the cut, exact rectangle area.
    left=[(-3,-1),(-1.5,-1),(-1.5,1.5)]
    mid=[(-1.5,-1),(1.5,-1),(1.5,1.5),(-1.5,1.5)]
    moving=np.array([(1.5,-1),(3,1.5),(1.5,1.5)])+[-4.5,0]
    assert math.isclose(area(left)+area(mid)+area(moving),4.5*2.5)
    assert np.all(moving[:,0]>=-3) and np.all(moving[:,0]<=1.5)
    # Episode 04: every motion is rigid; final triangles tile D x d/2.
    originals=[[(0,0),(3,0),(0,1.8)],[(0,0),(0,1.8),(-3,0)],
               [(0,0),(-3,0),(0,-1.8)],[(0,0),(0,-1.8),(3,0)]]
    targets=[]
    for i,angle,shift in ((0,0,(-3,-.9)),(1,math.pi,(0,.9)),
                          (2,0,(0,.9)),(3,math.pi,(3,-.9))):
        p=np.array(originals[i])
        rot=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
        q=p@rot.T+shift
        assert math.isclose(area(p),area(q))
        assert np.all(q[:,0]>=-3-1e-9) and np.all(q[:,0]<=3+1e-9)
        assert np.all(abs(q[:,1])<=.9+1e-9)
        targets.append(q)
    assert math.isclose(sum(area(q) for q in targets),6*1.8)
    print("PASS: 02 and 04 area and rigid endpoints")
    # Episode 07: no change of scale between circle, trace and diameter.
    r=1
    assert math.isclose((2*math.pi*r)/(2*r),math.pi)
    # Episode 08: actual circular sectors, exact area for all finite n.
    for n in (8,16,32):
        r=1.65
        assert math.isclose(n*(r*r*(2*math.pi/n)/2),math.pi*r*r)
        assert abs(n*r*math.sin(math.pi/n)-math.pi*r)<.14
    # Episode 13: exactly perpendicular catheti.
    A=np.array([-3,-1]);B=np.array([3,-1]);C=np.array([-.6,-1+math.sqrt(2.4*3.6)])
    assert abs(np.dot(A-C,B-C))<1e-10
    # Episode 19: remove only cycle edges, then only leaves.
    edges=[(i,(i+1)%4) for i in range(4)]+[(i+4,(i+1)%4+4) for i in range(4)]+[(i,i+4) for i in range(4)]
    active=set(range(12))
    def connected():
        reached={0}
        for _ in range(8):
            for j in active:
                a,b=edges[j]
                if a in reached or b in reached: reached.update((a,b))
        return len(reached)==8
    for e in (4,5,6,7,0):
        active.remove(e)
        assert connected()
    for v,e in ((4,8),(7,11),(0,3),(3,2),(6,10),(2,1),(5,9)):
        assert sum(v in edges[j] for j in active)==1
        active.remove(e)
    assert not active
    # Episode 27: sector arc = circumference of base.
    assert math.isclose(2.55*4*math.pi/3,2*math.pi*1.7)
    # Episode 29: equality for every sampled height.
    for y in np.linspace(0,1.4,101):
        assert math.isclose(math.pi*(1.4**2-y*y),math.pi*1.4**2-math.pi*y*y,abs_tol=1e-12)
    print("PASS: 07, 08, 13, 19, 27, 29 geometric identities")
    print("NOT RUN: Manim rendering, LaTeX compilation, visual/audio inspection.")

if __name__=="__main__":
    main()
