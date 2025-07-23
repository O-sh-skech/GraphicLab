from sympy import symbols, cos, sin, simplify, oo, zoo, nan
from math import radians

class FunctionSimpler:
    def __init__(self, functionType, value):
        self.functionType = functionType
        self.value = value

    @property
    def getValue(self):
        return self.value

    @property
    def getFunctionType(self):
        return self.functionType
    

    def __repr__(self):
        return f"FunctionSimpler(type={self.functionType}, value={self.value})"
    
def check_value(evaluated, functionType):
    # 発散・未定義チェック
    if evaluated in [oo, -oo, zoo] or evaluated.has(oo, zoo):
        return FunctionSimpler(functionType, nan)
    
    try:
        # Python floatに変換して絶対値をチェック
        val = float(evaluated)
        THRESHOLD = 1e10  # 好きな閾値を設定
        if abs(val) > THRESHOLD:
            return FunctionSimpler(functionType, nan)
    except (TypeError, ValueError):
        # floatに変換できない場合はそのまま返すかnanにするなど適宜対応
        pass
    
    return FunctionSimpler(functionType, evaluated)

def simpler(functionText, r, θ):
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
    
    # ラジアン変換（θが度指定なら）
    θ_rad = radians(θ)
    evaluated = f_polar_simplified.subs({radius: r, theta: θ_rad}).evalf()
    return check_value(evaluated, functionType)