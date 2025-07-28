from flask import  Blueprint, render_template, request, redirect, url_for
from database.models.feedback import Feedback  # モデルのインポート
from database.db.database import db
from werkzeug.utils import secure_filename
import os

upload_folder = 'static/uploads'  # アップロード先のフォルダ
feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def submit_feedback():
    if request.method == 'POST':
        category = request.form.get('category')
        title = request.form.get('title')
        content = request.form.get('content')
        file = request.files.get('file')

        if not category or not title or not content:
            error = "項目, タイトル、内容は必須です!"
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