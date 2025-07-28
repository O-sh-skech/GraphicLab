from database.db.database import db
from datetime import datetime

class Admin(db.Model):
    __tablename__ = 'admins'  # テーブル名を複数形にするのが一般的

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Admin {self.username}>"