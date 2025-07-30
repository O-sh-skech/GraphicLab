from flask import Blueprint, render_template, request, session, redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from database.db.database import db
from database.models.admin import Admin
from database.models.feedback import Feedback


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/register_admin_auth', methods=['POST','GET'])
def register_admin_auth():
    password = request.form.get('password')
    # ここでパスワード認証処理（仮に 'admin123' が正解とする）
    if request.method == 'POST': 
        if password == 'admin123':
            session['is_admin'] = True  # 管理者ログイン済みとしてセッションに保存
            return redirect('/register_admin')  # 認証成功後にトップページへリダイレクト（必要に応じて変更）
        else:
            return render_template('register_admin_auth.html', error='パスワードが間違っています')
        
    # GET
    return render_template('register_admin_auth.html')
    
@admin_bp.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('register_admin.html', error="すべての項目を入力してください")

        # ユーザー名の重複チェック
        if Admin.query.filter_by(username=username).first():
            return render_template('register_admin.html', error="このユーザー名は既に使われています")

        password_hash = generate_password_hash(password)
        new_admin = Admin(username=username, password_hash=password_hash)

        db.session.add(new_admin)
        db.session.commit()
        flash('管理者が登録されました')
        return redirect('/manager/login')  # 登録後ログインページへ

    return render_template('register_admin.html')

@admin_bp.route('/manager/login', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            session['admin_logged_in'] = True
            return redirect(url_for('feedback.manage_feedback'))
        else:
            error = 'ユーザー名またはパスワードが間違っています'
            return render_template('admin.html', error=error)

    return render_template('admin.html')