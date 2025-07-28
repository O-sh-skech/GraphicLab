import os
from flask import Flask, render_template, request, abort,redirect, session
from CreateMesh import create_surface_mesh, reset_json_dir
from sympy import sympify
from database.db.database import db
from database.routes.function_routes import function_bp  # Blueprint
from database.routes.feedback_routes import feedback_bp  # Blueprint

from database.config import Config  # 設定クラス

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 任意の長いランダムな文字列
app.config.from_object(Config)

# SQLAlchemy の初期化
db.init_app(app)

# アプリコンテキスト内でテーブル作成
with app.app_context():
    db.create_all()

# Blueprint の登録
app.register_blueprint(function_bp)
app.register_blueprint(feedback_bp)

# グローバル変数
latest_function_Text = ""
message = ""
reset_json_dir()

@app.route('/', methods=['GET', 'POST'])
def index():
    global latest_function_Text
    global message

    if request.method == 'POST':
        # ▼▼▼【変更点】ここに関数呼び出しを追加 ▼▼▼
        # 新しいファイルを生成する前に、古いファイルをすべて削除する
        reset_json_dir()

        # フォームから送信された関数を取得
        function_text = request.form.get('function_text')

        if not function_text:
            error = "入力が空です！"
            return render_template('draw.html', function_text="", error=error)
        
        #値を保持
        latest_function_Text = function_text
        try: # sympifyはエラーを出す可能性があるのでtry-exceptで囲むとより安全
            create_surface_mesh(360, 2, sympify(function_text))
            message = f"入力された関数: {function_text}"
        except Exception as e:
            message = f"関数の解析中にエラーが発生しました: {e}"
            # エラー時も入力内容とメッセージは画面に返す
            return render_template('draw.html', function_text=function_text, message=message)
            
        return render_template('draw.html', function_text=latest_function_Text, message=message)
    
    # GETのときの処理は変更なし
    selected_function = session.get('selected_function_text')
    if selected_function:
        # こちらも同様にリセットを入れると、より確実
        reset_json_dir() 
        latest_function_Text = selected_function
        try:
            create_surface_mesh(360, 2, sympify(selected_function))
            message = f"保存された関数を選択: {selected_function}"
        except Exception as e:
            message = f"関数の解析中にエラーが発生しました: {e}"
        # 一度使ったら削除しておく（好みに応じて）
        session.pop('selected_function_text', None)
        
    return render_template('draw.html', function_text=latest_function_Text, message=message)

@app.route('/animate', methods=['POST'])
def animate():
    global latest_function_Text  # ← 追加！
    animation_path = os.path.join(app.static_folder, 'Json', 'animation.json')

    if not os.path.exists(animation_path):
        error = "アニメーションデータが見つかりませんでした。ClickMeを押して関数を送信してください。"
        return render_template('draw.html', error=error)
    #フォームから送信された関数を取得
    message = f"入力された関数: {latest_function_Text}"
    return render_template('anim.html', function_text=latest_function_Text, message=message)

BASE_DIR = os.path.abspath("static/Json")

@app.route('/delete-file', methods=['DELETE'])
def delete_file():
    name = request.args.get('name')
    if not name:
        abort(400, "ファイル名指定なし")

    # 先頭の /static/Json/ を取り除く（あれば）
    prefix = '/static/Json/'
    if name.startswith(prefix):
        name = name[len(prefix):]

    # 余計なパスが入っていないかチェック（パス・トラバーサル対策）
    filename = os.path.basename(name)

    file_path = os.path.join(BASE_DIR, filename)

    # BASE_DIR外に出ていないかチェック
    if not os.path.abspath(file_path).startswith(BASE_DIR):
        abort(403, "アクセス禁止")

    if os.path.exists(file_path):
        os.remove(file_path)
        return "Deleted", 200
    else:
        abort(404, "ファイルが見つかりません")
        
#　管理者認証
@app.route('/manager/login', methods=['GET','POST'])
def admin():
    if request.method == 'GET':
        print("GETリクエストを受け取りました")
        return render_template('admin.html')
    else:
        password = request.form.get('password')
        username = request.form.get('username')
        if password == "データベースから参照したハッシュ化password" | username == "データベースから参照したusername":
            print("ログイン成功")
            return redirect('/manager/feedback')
        
if __name__ == '__main__':
    app.run(debug=True, port=5002)
