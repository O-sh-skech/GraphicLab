import math
from FunctionSimpler import simpler, evaluate
import json, os, shutil
from sympy import symbols

class MeshCreated:
    def __init__(self, m, o): self.meshGroup, self.otherWall = m, o
    @property
    def getMeshGroup(self): return self.meshGroup
    @property
    def getOtherWall(self): return self.otherWall

class MeshCalculated:
    def __init__(self, o, i, t, v, f): self.outerWall, self.innerWall, self.otherWall, self.verticalWall, self.functionType = o, i, t, v, f
    @property
    def getOuterWall(self): return self.outerWall
    @property
    def getInnerWall(self): return self.innerWall
    @property
    def getOtherWall(self): return self.otherWall
    @property
    def getVerticalWall(self): return self.verticalWall
    @property
    def getFunctionType(self): return self.functionType

class Mesh:
    def __init__(self, m, v): self.mesh, self.meshView, self.otherWall = m, v, []
    @property
    def getMesh(self): return self.mesh
    @property
    def getMeshView(self): return self.meshView
    @property
    def getOtherWall(self): return self.otherWall

class TriangleMesh:
    def __init__(self): self.points, self.faces, self.texCoords = [], [], []

class MeshView: pass

class CopyList:
    def __init__(self, l): self.list = l.copy()
    @property
    def getList(self): return self.list

def flatten_vector(v):
    flat = []
    for x in v:
        flat.extend(flatten_vector(x)) if isinstance(x, (list, tuple)) else flat.append(x)
    return flat

def toJson(v, name):
    with open(os.path.join("static/Json", name + ".json"), "w", encoding="utf-8") as f:
        json.dump(flatten_vector(v), f, ensure_ascii=False, indent=2)

def max_min_divider(z, s):
    return max(z, -s*1e5) if z < 0 else min(z, s*1e5)

def reset_json_dir():
    d = "static/Json"
    if os.path.exists(d): shutil.rmtree(d)
    os.makedirs(d)

def list_index_sum(l):
    s, res = 0, []
    for i in range(len(l)-1):
        if len(l[i]) > 1:
            s += len(l[i])
            res.append(s)
    return res

def adjust_z_pos(r, t, f, ft, s, ar, at):
    nr = r+0.1 if r==0 and ar else r-0.5 if ar else r
    nt = t-1 if at else t
    rad = math.radians(nt)
    z = max_min_divider(float(evaluate(f, nr, nt)), s)
    x, y = nr*math.cos(rad), nr*math.sin(rad)
    if math.isnan(z):
        return adjust_z_pos(nr, nt, f, ft, s, True, False) if ft==1 else adjust_z_pos(nr, nt, f, ft, s, False, True)
    return [x, z, y]

def shift_wall(r, nr, f, a, s, w, i, o):
    for t in range(a+1):
        rad = math.radians(t)
        x, y = nr*math.cos(rad), nr*math.sin(rad)
        z = float(evaluate(f, nr, t))
        w.append([x, z, y, nr/s, t/a, r, t])
    i.append(CopyList(w).getList); w.clear()
    o.append(CopyList(i).getList); i.clear()

def adjust_wall(r, f, a, s, out, inn):
    w, i, o = [], [], []
    nr = r + 0.2 if r==0 else r + 0.05 if out else r - 0.35
    lim = r+1.0 if r==0 or out else r
    step = 0.2 if r==0 or out else 0.1
    while nr < lim:
        shift_wall(r, nr, f, a, s, w, i, o)
        nr += step
    return o

def calculate_surface_mesh(a, s, func):
    o, i, w, rList, setW, t, vW = [], [], [], [], [], [], []
    sim = simpler(func)
    f, ft = sim.getF_polar_simplified, sim.getFunctionType
    r = 0.0
    while r <= s:
        i.clear(); isNaN = False
        for t_ in range(a+1):
            rad = math.radians(t_)
            x, y = r*math.cos(rad), r*math.sin(rad)
            try:
                z = float(evaluate(f, r, t_))
                if math.isnan(z):
                    if ft != 1 and (ft != 2 or r != 0):
                        z = adjust_z_pos(r, t_, f, ft, s, False, True)[1]
                        raise ValueError
                    elif ft == 1:
                        if t_ == 0:
                            setW = adjust_wall(r, f, a, s, False, False)
                            for _ in range(4): rList.append("NaN")
                        pos = adjust_z_pos(r, t_, f, ft, s, True, False)
                        x, z, y = pos[0], pos[1], pos[2]
            except ValueError: isNaN = True; continue
            finally:
                pos = [x, z, y, r/s, t_/a, r, t_]
                if r in [0,1,2]: w.append(pos)
                t.append(pos)
                if isNaN or t_ == a:
                    rList.append(z)
                    if r == s: vW.append(CopyList(rList).getList); rList.clear()
                    i.append(CopyList(t).getList); t.clear(); isNaN = False
        o.append(CopyList(i).getList)
        if setW:
            o.extend(CopyList(setW).getList); setW.clear()
            if r != 0:
                vW.append(CopyList(rList).getList); rList.clear()
                setW = adjust_wall(r, f, a, s, True, False)
                o.extend(CopyList(setW).getList); setW.clear()
                for _ in range(4): rList.append("NaN")
        r += 1.0
    return MeshCalculated(o, i, w, vW, ft)

def create_surface_mesh(a, s, func):
    reset_json_dir()
    mesh = TriangleMesh()
    calc = calculate_surface_mesh(a, s, func)
    o, i, w, vW, ft = calc.getOuterWall, calc.getInnerWall, calc.getOtherWall, calc.getVerticalWall, calc.getFunctionType
    if ft in [0, 2]:
        for idx in range(len(i)):
            temp = [o[j][idx] for j in range(len(o))]
            for j in range(len(temp)):
                p = temp[j]
                if len(p) <= 2: continue
                for pos in p: mesh.points.append((pos[0], pos[1], pos[2])); mesh.texCoords.append((pos[3], pos[4]))
                wSize = min(len(p), len(temp[j+1])) if j+1 < len(temp) else 0
                line = 0
                for l in list_index_sum(temp):
                    for k in range(wSize-1):
                        mesh.faces += [(k+line, k+l, k+line+1), (k+line+1, k+l, k+l+1)]
                    line += wSize
            toJson(mesh.points,f"points_{idx}"); toJson(mesh.texCoords,f"texCoords_{idx}"); toJson(mesh.faces,f"faces_{idx}")
            mesh.faces.clear(); mesh.texCoords.clear(); mesh.points.clear()
        toJson(w, "animation")
    if ft == 1:
        n, ln = 0, 0
        for v in vW:
            for idx in range(len(i)):
                temp = [o[j+ln][idx] for j in range(len(v))]; ln += len(v)
                for j in range(len(temp)):
                    p = temp[j]
                    if len(p) <= 2: continue
                    for pos in p: mesh.points.append((pos[0], pos[1], pos[2])); mesh.texCoords.append((pos[3], pos[4]))
                    wSize = min(len(p), len(temp[j+1])) if j+1 < len(temp) else 0
                    line = 0
                    for l in list_index_sum(temp):
                        for k in range(wSize-1):
                            mesh.faces += [(k+line, k+l, k+line+1), (k+line+1, k+l, k+l+1)]
                        line += wSize
                toJson(mesh.points,f"points_{n}"); toJson(mesh.texCoords,f"texCoords_{n}"); toJson(mesh.faces,f"faces_{n}")
                mesh.faces.clear(); mesh.texCoords.clear(); mesh.points.clear(); n += 1
        toJson(w,"animation")

#x, y = symbols('x y')
#print(create_surface_mesh(360, 3, 1/(x**2+y**2-1)))