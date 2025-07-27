from database.db.database import db
from pytz import timezone
from datetime import datetime

JST = timezone('Asia/Tokyo')

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # フィードバックのカテゴリ
    title = db.Column(db.String(100), nullable=False)  # フィードバックのタイトル
    content = db.Column(db.Text, nullable=False)  # フィードバック内容
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(JST))  # 送信日時
    file = db.Column(db.String(255), nullable=True)  # 添付ファイルのパス

    def __str__(self):
        return f'<Feedback {self.id}: {self.category[:20]}...: {self.title[:20]}...: {self.created_at}>'
    
    '''
    __tablename__
    実際のDBで使うテーブル名

    content
    フィードバックの内容を保存する

    created_at
    フィードバックが作成された日時を自動で記録

    __str__
    管理者ページなどでデバッグ・確認しやすくする文字列表示
    '''