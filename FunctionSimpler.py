from sympy import symbols, cos, sin, simplify, oo, zoo, nan
from math import radians

class FunctionSimpler:#シンプルにした結果とfunctiontypeを返す
    def __init__(self, functionType, f_polar_simplified):
        self.functionType = functionType
        self.f_polar_simplified = f_polar_simplified

    @property
    def getF_polar_simplified(self):
        return self.f_polar_simplified

    @property
    def getFunctionType(self):
        return self.functionType
    

    def __repr__(self):
        return f"FunctionSimpler(type={self.functionType}, value={self.f_polar_simplified})"
    
def check_value(evaluated):
    # 発散・未定義チェック
    if evaluated in [oo, -oo, zoo] or evaluated.has(oo, zoo):
        return nan
    
    try:
        # Python floatに変換して絶対値をチェック
        val = float(evaluated)
        THRESHOLD = 1e10  # 好きな閾値を設定
        if abs(val) > THRESHOLD:
            return nan
    except (TypeError, ValueError):
        # floatに変換できない場合はそのまま返すかnanにするなど適宜対応
        pass
    
    return evaluated



def simpler(functionText):
    # 変数定義
    x, y, radius, theta = symbols('x y radius theta')
    # x, y を極座標に置換
    f_polar = functionText.subs({x: radius*cos(theta), y: radius*sin(theta)})
    # 簡約
    f_polar_simplified = simplify(f_polar)

    # シンボルの判定で関数タイプを決定
    free_symbols = f_polar_simplified.free_symbols

    if radius in free_symbols:
        if theta in free_symbols:
            functionType = 2  # rとθの関数
        else:
            functionType = 1  # rの関数
    elif theta in free_symbols:
        functionType = 0  # θの関数
    else:
        functionType = -1  # 定数など、rもθも含まない
    
    return FunctionSimpler(functionType, f_polar_simplified)

def evaluate(f_polar_simplified,r,θ):#計算結果を返す
    radius, theta = symbols('radius theta')
    θ_rad = radians(θ)
    evaluated = f_polar_simplified.subs({radius: r, theta: θ_rad}).evalf()
    return check_value(evaluated)

'''
def Domein(angle, size, functionText):#angleはθの終点sizeはrの終点
    radius, theta = symbols('radius theta')
    f=simpler(functionText)#極座標変換された関数
    domain = continuous_domain(f, radians, S.Reals)
    domain = continuous_domain(f, theta, S.Reals)
    #範囲がa,♾️
'''