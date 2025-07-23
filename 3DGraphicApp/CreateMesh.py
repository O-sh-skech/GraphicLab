import math
from FunctionSimpler import simpler
import json
import os
from sympy import symbols

def print_vector(vector):
  for i in vector:
      print("全ての座標データ",i)

# 下位クラスはそのまま
class MeshCreated:
    def __init__(self, meshGroup, otherWall):
        self.meshGroup = meshGroup
        self.otherWall = otherWall

    @property
    def getMeshGroup(self):
        return self.meshGroup

    @property
    def getOtherWall(self):
        return self.otherWall

class MeshCalculated:
    def __init__(self, outerWall, innerWall, otherWall):
        self.outerWall = outerWall
        self.innerWall = innerWall
        self.otherWall = otherWall

    @property
    def getOuterWall(self):
        return self.outerWall

    @property
    def getInnerWall(self):
        return self.innerWall

    @property
    def getOtherWall(self):
        return self.otherWall

class Mesh:
    def __init__(self, mesh, meshView):
        self.mesh = mesh
        self.meshView = meshView
        self.otherWall = []

    @property
    def getMesh(self):
        return self.mesh

    @property
    def getMeshView(self):
        return self.meshView

    @property
    def getOtherWall(self):
        return self.otherWall

class TriangleMesh:
    def __init__(self):
        self.points = []
        self.faces = []
        self.texCoords = []

class MeshView:
    pass

class CopyList:
    def __init__(self, lst):
        self.list = lst.copy()

    @property
    def getList(self):
        return self.list
    

def flatten_vector(vector):
    flat_list = []
    for item in vector:
        if isinstance(item, (list, tuple)):
            flat_list.extend(flatten_vector(item))  # 再帰的に展開
        else:
            flat_list.append(item)
    return flat_list

def toJson(vector, filename):
    flat = flatten_vector(vector)
    filepath = os.path.join("static/Json", filename + ".json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(flat, f, ensure_ascii=False, indent=2)

def max_min_divider(zPos: float, size: int) -> float:
    if zPos < 0:
        zPos = max(zPos, -size * 10**5)
    else:
        zPos = min(zPos, size * 10**5)
    return zPos

def list_index_sum(lst):
    sumList = []
    sum_val = 0
    for i in range(len(lst) - 1):
        if len(lst[i]) <= 1:
            continue
        sum_val += len(lst[i])
        sumList.append(sum_val)
    return sumList

def adjust_z_pos(r, θ, functionText, functionType, size, adjustR, adjustθ):
    newR = r + 0.1 if adjustR else r
    newTheta = θ - 1 if adjustθ else θ
    newZPos = max_min_divider(float(simpler(functionText, newR, newTheta).getValue), size)
    if math.isnan(newZPos):
        if functionType == 1:
            return adjust_z_pos(newR, newTheta, functionText, functionType, size, True, False)
        if functionType == 2:
            return adjust_z_pos(newR, newTheta, functionText, functionType, size, False, True)
        raise ValueError("zPos is NaN")
    return newZPos

def shift_wall(r,newR, functionText, angle, size, wall, innerWall, outerWall):
  #  print(newR)
    for θ in range(angle + 1):
        radian = math.radians(θ)
        xPos = (newR) * math.cos(radian)
        yPos = (newR) * math.sin(radian)
        zPos = float(simpler(functionText, (newR), θ).getValue)
        u = (newR) / size
        v = θ / angle
        xyzPos = [xPos, zPos, yPos, u, v, r, θ]
        wall.append(xyzPos)
    innerWall.append(CopyList(wall).getList)
   # print(len(wall))
    wall.clear()
    outerWall.append(CopyList(innerWall).getList)
    innerWall.clear()#配列の構造を守る

def adjust_wall(r, functionText, angle, size):
    wall = []
    innerWall = []
    outerWall = []
    if r==0:
        newR = r + 0.2
        while newR < r + 1.0:
            shift_wall(r,newR, functionText, angle, size, wall, innerWall, outerWall)
            newR += 0.2
    else :
        newR = r - 0.2
        while newR > r - 1.0:
            shift_wall(r,newR, functionText, angle, size, wall, innerWall, outerWall)
            newR -= 0.2
    return outerWall




def calculate_surface_mesh(angle, size, functionText):
    functionType = simpler(functionText, 0, 0).getFunctionType
    outerWall = []
    innerWall = []
    wall = []
    wallSet = []
    otherWall = []
    isNaN = False

    r = 0.0
    while r <= size:
       # print(r)
        innerWall.clear()
        for θ in range(angle + 1):
            radian = math.radians(θ)
            xPos = r * math.cos(radian)
            yPos = r * math.sin(radian)
            zPos = float(simpler(functionText, r, θ).getValue)
           
            u = r / size
            v = θ / angle
            try:
                if math.isnan(zPos):
                    if functionType != 1 and (functionType != 2 or r != 0):
                        zPos = adjust_z_pos(r, θ, functionText, functionType, size, False, True)
                        raise ValueError("zPos is NaN")
                    elif functionType == 1:
                        if θ == 0:
                           # print("ここ")
                            wallSet = adjust_wall(r, functionText, angle, size)
                          # print(f"wallSet length = {len(wallSet)}")
                        zPos = adjust_z_pos(r, θ, functionText, functionType, size, True, False)#θが0の時も->+0.1と+0.2で補足が充実するはず
            except ValueError:
                isNaN = True
                continue
            finally:
                xyzPos = [xPos, zPos, yPos, u, v, r, θ]
                if (r == 0 or r == 1 or r == 2) and θ <= angle:
                    otherWall.append(xyzPos)
                wall.append(xyzPos)
               # print("現実",xyzPos[1])
                if isNaN or θ == angle:
                #    print("到達した")
                    innerWall.append(CopyList(wall).getList)
                  #  print(len(wall))
                    wall.clear()
                    isNaN = False
        outerWall.append(CopyList(innerWall).getList)
        if wallSet:
                #+0.1を追加した後に+0.2を追加する。
                print("補完された")
                outerWall.extend(CopyList(wallSet).getList)
                wallSet.clear()
       # print(f"r = {r}, innerWall length = {len(innerWall)}")
       # print(f"outerWall length = {len(outerWall)}")
        r += 1.0

        
    return MeshCalculated(outerWall, innerWall, otherWall)

def create_surface_mesh(angle, size, functionText):
    meshGroup = []
    foundMeshList = []
    foundMesh = TriangleMesh()
    materialMesh = calculate_surface_mesh(angle, size, functionText)
    outerWall = materialMesh.getOuterWall
    #print(len(outerWall))
    innerWall = materialMesh.getInnerWall
    #print("innerwallは",len(innerWall[0])+len(innerWall[1]))
    
    otherWall = materialMesh.getOtherWall

    for inner in range(len(innerWall)):
        foundMeshList.clear()
        for outer in range(len(outerWall)):
            foundMeshList.append(outerWall[outer][inner])
            #print_vector(foundMeshList)
            #print(outer)
        for i in range(len(foundMeshList)):
            #print_vector(foundMeshList)
            xyzPosList = foundMeshList[i]
            if len(xyzPosList) <= 2:
                continue
            for xyzPos in xyzPosList:
                foundMesh.points.append((xyzPos[0], xyzPos[1], xyzPos[2]))
             #   print(xyzPos[1])
                foundMesh.texCoords.append((xyzPos[3], xyzPos[4]))

            wallSize = 0
            if i + 1 < len(foundMeshList):
                if len(foundMeshList[i]) <= len(foundMeshList[i + 1]):
                    wallSize = len(foundMeshList[i])
                else:
                    wallSize = len(foundMeshList[i + 1])

            lineIndex = 0
            for listIndex in list_index_sum(foundMeshList):
                for PosIndex in range(wallSize - 1):
                    foundMesh.faces.extend([
                        (PosIndex+lineIndex, PosIndex+listIndex, PosIndex+lineIndex+1),
                        (PosIndex+lineIndex+1, PosIndex+listIndex, PosIndex+listIndex+1)
                    ])
                lineIndex += wallSize


        toJson(foundMesh.points,f"points_{inner}")#r方向のメッシュ切りが起こらない問題。
        toJson(foundMesh.texCoords,f"texCoords_{inner}")
        toJson(foundMesh.faces,f"faces_{inner}")

        foundMesh.faces.clear()
        foundMesh.texCoords.clear()
        foundMesh.points.clear()
    toJson(otherWall,"animation")

#x, y = symbols('x y')
#print(create_surface_mesh(90,1,1/(y**2+x**2)))





