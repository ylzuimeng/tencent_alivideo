from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)  # 原始文件名
    oss_url = db.Column(db.String(255), unique=True)      # OSS 文件访问地址
    upload_time = db.Column(db.DateTime, default=datetime.utcnow) # 上传时间
    size = db.Column(db.Integer)                          # 文件大小（字节）
    description = db.Column(db.String(200))               # 可选：文件描述

    def __repr__(self):
        return f'<File {self.filename}>'

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)  # 原始文件名
    oss_url = db.Column(db.String(255), unique=True)      # OSS 文件访问地址
    upload_time = db.Column(db.DateTime, default=datetime.utcnow) # 上传时间
    size = db.Column(db.Integer)                          # 文件大小（字节）
    description = db.Column(db.String(200))               # 可选：文件描述

    def __repr__(self):
        return f'<Template {self.filename}>'

class TaskStyle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    open_oss_url = db.Column(db.String(255))
    close_oss_url = db.Column(db.String(255))
    title_picture_oss_url_1 = db.Column(db.String(255))
    title_picture_oss_url_2 = db.Column(db.String(255))
    change_material_oss_url = db.Column(db.String(255))
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
