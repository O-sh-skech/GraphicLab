import os
from flask import Flask, render_template, request, abort,redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from CreateMesh import create_surface_mesh
from sympy import sympify


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # フォームから送信された関数を取得
        function_text =  request.form['function_text']
        if not function_text:
            error = "入力が空です！"
            return render_template('draw.html', function_text=function_text, error=error)
        # 値を保持
        create_surface_mesh(360,2,sympify(function_text))
        message = f"入力された関数: {function_text}"
        return render_template('draw.html', function_text=function_text, message=message)
    # GET時は直前の入力値を渡す（なければ空）
    return render_template('draw.html', function_text="")


@app.route('/animate', methods=['POST'])
def animate():
    animation_path = os.path.join(app.static_folder, 'Json', 'animation.json')

    if not os.path.exists(animation_path):
        error = "アニメーションデータが見つかりませんでした。ClickMeを押して関数を送信してください。"
        return render_template('draw.html', error=error)

    return render_template('anim.html')


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
@app.route('/admin/login', methods=['GET','POST'])
def admin():
    if request.method == 'GET':
        print("GETリクエストを受け取りました")
        return render_template('admin.html')
    else:
        password = request.form.get('password')
        return "未実装" , 501
        
if __name__ == '__main__':
    app.run(debug=True, port=5002)
