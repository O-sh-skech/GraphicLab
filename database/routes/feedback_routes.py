# 標準ライブラリ
import os

# サードパーティライブラリ
from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

# 自作モジュール
from database.models.feedback import Feedback
from database.db.database import db


upload_folder = 'static/uploads'  # ファイルのアップロード先のフォルダ

feedback_bp = Blueprint('feedback', __name__)

#フィードバックの送信
@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def submit_feedback():
    if request.method == 'POST':
        category = request.form.get('category')
        title = request.form.get('title')
        content = request.form.get('content')
        file = request.files.get('file')

        errors = []
        if not category:
            errors.append("項目を選択してください")
        if not title:
            errors.append("件名を5文字以上で入力してください")
        if not content:
            errors.append("内容を10文字以上で入力してください")
        if not category or not title or not content:
            error = "項目, 件名、内容は必須です!"
            return render_template('feedback.html', error=error)

        if file:
          # 元のファイル名を安全に取得
          original_file = secure_filename(file.filename)
          filename = original_file
          file_path = os.path.join(upload_folder, filename)

          # ファイル名がuploads_folderに存在してたら、リネームして保存名を決める
          i = 1
          while os.path.exists(file_path):
              name, ext = os.path.splitext(original_file) #拡張子を分離
              filename = f"{name}_{i}{ext}" #リネーム
              file_path = os.path.join(upload_folder, filename)
              i += 1

          # ファイルを保存
          file.save(file_path)

          # DBにuploadsフォルダ内のパスを保存
          feedback_file = f"uploads/{filename}"
        else:
          feedback_file = None

        # DB登録
        feedback = Feedback(
            category=category,
            title=title,
            content=content,
            file=feedback_file
        )

        db.session.add(feedback)
        db.session.commit()

        message = "Thank you for your feedback!"
        return render_template('feedback.html', message=message)

    return render_template('feedback.html')

# フィードバック一覧と検索/フィルター/ソート(日付)
@feedback_bp.route('/manager/feedback', methods=['GET', 'POST'])
def manage_feedback():
    query = Feedback.query

    if request.method == 'POST':
        search_word = request.form.get('search_word')
        category = request.form.get('category', '')
        sort = request.form.get('sort', 'newest')
        status = request.form.get('status', 'all')

        if search_word:
            query = query.filter(
                Feedback.title.ilike(f"%{search_word}%") |
                Feedback.content.ilike(f"%{search_word}%")
            )

        if category:
            query = query.filter(Feedback.category == category)

        if status != 'all':
            query = query.filter(Feedback.status == status)

        if sort == 'newest':
            query = query.order_by(Feedback.created_at.desc())
        elif sort == 'oldest':
            query = query.order_by(Feedback.created_at.asc())
        elif sort == 'status':
            query = query.order_by(Feedback.status.asc())

        feedbacks = query.all()
        return render_template("manage_feedback.html", feedbacks=feedbacks)

    feedbacks = Feedback.query.all()
    return render_template('manage_feedback.html', feedbacks=feedbacks)


# フィードバックの詳細
@feedback_bp.route('/manager/feedback/<int:feedback_id>', methods=['GET'])
def feedback_detail(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    return render_template('feedback_detail.html', feedback=feedback)
        
# フィードバックのステータス(保留/確認済)を更新
@feedback_bp.route('/manager/feedback/<int:feedback_id>/update', methods=['POST'])
def update_feedback_status(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'confirmed']:
        feedback.status = new_status
        db.session.commit()
    return redirect(url_for('feedback.manage_feedback'))

# 指定した確認済のフィードバックを削除
@feedback_bp.route('/manager/feedback/delete/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    
    if feedback.status == 'confirmed':
        db.session.delete(feedback)
        db.session.commit()
        return redirect(url_for('feedback.manage_feedback'))
    else:
        return "このフィードバックは確認済ではないため削除できません", 403
