from database.db.database import db
from pytz import timezone
from datetime import datetime

JST = timezone('Asia/Tokyo')

class Function(db.Model):
    __tablename__ = 'functions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)       # 保存名
    expression = db.Column(db.Text, nullable=False)        
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(JST))
    

'''
__tablename__
実際のDBで使うテーブル名を明示的に指定（慣習）

function_text
SymPyで解釈するための文字列式（例えば "1/(x**2 + y**2)"）

timestamp
datetime.utcnow を default に設定して自動記録

__repr__
管理者ページなどでデバッグ・確認しやすくする文字列表示

'''