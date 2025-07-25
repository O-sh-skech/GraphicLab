import os
from flask import Flask, render_template, request, abort,redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from CreateMesh import create_surface_mesh, reset_json_dir
from sympy import sympify


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# グローバル変数
latest_function_Text = ""
message = ""
reset_json_dir()

@app.route('/', methods=['GET', 'POST'])
def index():
    global latest_function_Text  # ← 追加！
    global message
    if request.method == 'POST':
        # フォームから送信された関数を取得
        function_text =  request.form['function_text']
        
        if not function_text:
            error = "入力が空です！"
            return render_template('draw.html', function_text="", error=error)
        # 値を保持
        latest_function_Text = function_text
        create_surface_mesh(360,2,sympify(function_text))
        message = f"入力された関数: {function_text}"
        return render_template('draw.html', function_text=latest_function_Text, message=message)
    # GET時は直前の入力値を渡す（なければ空）
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
#フィードバック送信
@app.route('/feedback', methods=['GET', 'POST'])
def submit_feedback():
    if request.method == 'POST':
        feedback_text = request.form.get('feedback_text')
        if not feedback_text:
            error = "フィードバックが空です！"
            return render_template('feedback.html', error=error)
        
        # ここでフィードバックをデータベースに保存するロジックを追加
        # 例: new_feedback = Feedback(content=feedback_text)
        # db.session.add(new_feedback)
        # db.session.commit()
        
        message = "フィードバックが送信されました。ありがとうございます！"
        return render_template('feedback.html', message=message)
    
    return render_template('feedback.html')

# PDF保存 ---関数と生成したグラフの画面をPDFとして保存---
@app.route('/save_pdf', methods=['GET'])
def save_pdf():
    # ここでPDF保存のロジックを追加
    # 例: pdf_path = generate_pdf()
    # return send_file(pdf_path, as_attachment=True)
    
    message = "PDFが保存されました。"
    return render_template('save_pdf.html', message=message)

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
        
# フィードバック一覧
@app.route('/manager/feedback', methods=['GET','POST'])
def manage_feedback():
    if request.method == 'GET':
        print("フィードバック管理ページにアクセス")
        return render_template('showFeedback.html')
        
# フィードバックの詳細ページ
@app.route('/manager/feedback/<int:feedback_id>', methods=['GET'])
def feedback_detail(feedback_id):
    # ここでフィードバックの詳細を取得するロジックを追加
    # 例: feedback = Feedback.query.get(feedback_id)
    feedback = {"id": feedback_id, "content": "フィードバックの内容"}
    return render_template('feedback_detail.html', feedback=feedback)


# フィードバックを指定した条件でソート。項目,日付,評価でソート可能

# フィードバックの検索
if __name__ == '__main__':
    app.run(debug=True, port=5002)
