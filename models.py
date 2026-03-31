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
    name = db.Column(db.String(200))                      # 模板名称
    open_oss_url = db.Column(db.String(255))              # 片头视频
    close_oss_url = db.Column(db.String(255))             # 片尾视频
    title_picture_oss_url_1 = db.Column(db.String(255))   # 背景图片1
    title_picture_oss_url_2 = db.Column(db.String(255))   # 背景图片2
    change_material_oss_url = db.Column(db.String(255))   # 过渡效果
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TaskStyle {self.name or self.id}>'

class ProcessingTask(db.Model):
    """视频处理任务"""
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(200), nullable=False) # 任务名称
    source_file_id = db.Column(db.Integer, db.ForeignKey('file.id'))  # 源视频文件ID
    task_style_id = db.Column(db.Integer, db.ForeignKey('task_style.id'))  # TaskStyle模板ID
    status = db.Column(db.String(50), default='pending')  # 任务状态：pending/processing/completed/failed
    ice_job_id = db.Column(db.String(255))                # 阿里云ICE作业ID
    ice_project_id = db.Column(db.String(255))            # 阿里云ICE工程ID
    output_oss_url = db.Column(db.String(255))            # 成品视频OSS地址
    progress = db.Column(db.Integer, default=0)           # 处理进度(0-100)
    error_message = db.Column(db.Text)                    # 错误信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)                 # 完成时间

    # 关联关系
    source_file = db.relationship('File', backref='processing_tasks')
    task_style = db.relationship('TaskStyle', backref='processing_tasks')

    def __repr__(self):
        return f'<ProcessingTask {self.task_name}>'

class TaskMaterial(db.Model):
    """任务素材关联表"""
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('processing_task.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    material_type = db.Column(db.String(50))              # 素材类型：main_video/header/footer/transition/bg
    sort_order = db.Column(db.Integer, default=0)         # 排序顺序

    # 关联关系
    task = db.relationship('ProcessingTask', backref='materials')
    file = db.relationship('File')

    def __repr__(self):
        return f'<TaskMaterial {self.material_type}>'
