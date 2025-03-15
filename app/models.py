from . import db
from datetime import datetime
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    translated_file_path = db.Column(db.String(255), nullable=True)
    target_language = db.Column(db.String(20), nullable=False, server_default='None')
    status = db.Column(db.String(20), nullable=False, default='in_progress')
    date_uploaded = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
