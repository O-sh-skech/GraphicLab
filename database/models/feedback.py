from database.db.database import db
from pytz import timezone
from datetime import datetime

JST = timezone('Asia/Tokyo')

'''
    __tablename__
    実際のDBで使うテーブル名

    id
    フィードバックを一意に認識するためのid。自動で生成される
    
    category
    項目名 -必須
    
    title
    タイトル -必須
    
    content
    内容 -必須
    
    created_at
    フィードバックが作成された日時を自動で記録 
    
    file
    static/uploadsに保存したスクリーンショット等ファイルのパス -任意

    __str__
    管理者ページなどでデバッグ・確認しやすくする文字列表示
'''
class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # フィードバックのカテゴリ
    title = db.Column(db.String(100), nullable=False)  # フィードバックのタイトル
    content = db.Column(db.Text, nullable=False)  # フィードバック内容
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(JST))  # 送信日時
    file = db.Column(db.String(255), nullable=True)  # 添付ファイルのパス
    status = db.Column(db.String(20), default='pending') #　フィードバックのステータス pending (保留中), confirmed (確認済)

    def __str__(self):
        return f'<Feedback {self.id}: {self.category[:20]}...: {self.title[:20]}...: {self.created_at}>'