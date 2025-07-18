import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# 直前に入力された関数をグローバル変数で保持（本来はDB推奨）
last_function_text = ""

@app.route('/', methods=['GET', 'POST'])
def index():
    global last_function_text

    if request.method == 'POST':
        # フォームから送信された関数を取得
        function_text =  request.form['function_text']
        if not function_text:
            error = "入力が空です！"
            return render_template('index.html', function_text=function_text, error=error)
        # 値を保持
        last_function_text = function_text
        message = f"入力された関数: {function_text}"
        return render_template('index.html', function_text=function_text, message=message)
    
    # GET時は直前の入力値を渡す（なければ空）
    return render_template('index.html', function_text=last_function_text)
    
if __name__ == '__main__':
    app.run(debug=True)
