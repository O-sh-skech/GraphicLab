import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "default-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///db/database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False