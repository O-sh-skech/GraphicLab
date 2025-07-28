import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from flask import  Blueprint, render_template, request, redirect, url_for, session, flash
from database.models.function import Function  # モデルのインポート（必要に応じてパス変更）
from database.db.database import db

function_bp = Blueprint('function', __name__)

@function_bp.route('/name_function', methods=['GET'])
def name_function():
    function_text = session.get('function_text', '')
    return render_template('name_function.html', function_text=function_text)

@function_bp.route('/prepare_save', methods=['POST'])
def prepare_save():
    function_text = request.form.get('function_text')
    if not function_text:
        return redirect(url_for('index'))
    
    # 関数式をセッションに保存
    session['function_text'] = function_text
    return redirect(url_for('function.name_function'))

@function_bp.route('/save_function', methods=['POST'])
def save_function():
    function_name = request.form.get('function_name')
    function_text = request.form.get('function_text')  # ここでフォームから受け取る

    print("🔍 受け取ったデータ:")
    print(f"function_name = {function_name}")
    print(f"function_text = {function_text}")

    if not function_name or not function_text:
        print("⚠️ データが不足しています。保存処理をスキップします。")
        return redirect(url_for('index'))
    
    new_function = Function(
    name=function_name,
    expression=function_text,   # 文字列のまま保存
    )
    db.session.add(new_function)
    try:
        db.session.commit()
        print("✅ データベースに保存されました。")
    except Exception as e:
        db.session.rollback()
        print(f"❌ データベース保存エラー: {e}")

    # 保存されたすべての関数を確認出力
    all_functions = Function.query.all()
    print("📦 現在のDB内の関数一覧:")
    for f in all_functions:
        print(f"ID: {f.id}, Name: {f.name}, Expression: {f.expression}")

    return redirect(url_for('index'))

@function_bp.route('/show_all', methods=['GET'])
def history():
    functions = Function.query.all()
    return render_template('show_all.html', functions=functions)

@function_bp.route('/select_function', methods=['POST'])
def select_function():
    function_id = request.form.get('function_id')
    print(f"受け取ったfunction_id: {function_id}")  # ← 確認用
    if not function_id:
        flash("関数IDが送信されませんでした。", "error")
        return redirect(url_for('function.history'))

    func = Function.query.get(function_id)
    if func:
        print(f"選択された関数: {func.expression}")  # ← 確認用
        session['selected_function_text'] = func.expression
        flash(f"関数を選択しました: {func.expression}", "info")
    else:
        print("関数が見つかりませんでした")  # ← 確認用
        flash("関数が見つかりませんでした。", "error")
    
    return redirect(url_for('index'))

@function_bp.route('/delete_function/<int:function_id>', methods=['POST'])
def delete_function(function_id):
    func = Function.query.get(function_id)
    if not func:
        print(f"⚠️ 削除対象の関数が見つかりません: ID={function_id}")
        return '', 404

    try:
        db.session.delete(func)
        db.session.commit()
        print(f"🗑️ 関数を削除しました: ID={function_id}, Name={func.name}")
        return '', 204
    except Exception as e:
        db.session.rollback()
        print(f"❌ 削除中にエラーが発生しました: {e}")
        return '', 500