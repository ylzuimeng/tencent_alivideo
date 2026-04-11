from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class DoctorInfo(db.Model):
    """医生信息表"""
    __tablename__ = 'doctor_info'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)        # 姓名
    hospital = db.Column(db.String(200))                    # 医院
    department = db.Column(db.String(100))                  # 科室
    title = db.Column(db.String(50))                        # 职称
    batch_id = db.Column(db.String(100))                    # 导入批次号
    is_validated = db.Column(db.Boolean, default=False)     # 是否已校验
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联关系
    processing_tasks = db.relationship('ProcessingTask', backref='doctor_info', lazy='dynamic')

    def __repr__(self):
        return f'<DoctorInfo {self.name} - {self.hospital}>'


class VideoTemplate(db.Model):
    """视频模板表（替换TaskStyle）"""
    __tablename__ = 'video_template'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)        # 模板名称

    # 视频素材
    header_video_url = db.Column(db.String(255))           # 片头视频URL
    footer_video_url = db.Column(db.String(255))           # 片尾视频URL

    # 字幕配置
    enable_subtitle = db.Column(db.Boolean, default=False)  # 是否生成字幕
    subtitle_position = db.Column(db.String(50))           # 字幕位置：top/bottom/center
    subtitle_extract_audio = db.Column(db.Boolean, default=True)  # 是否提取语音

    # 文字叠加配置（JSON格式存储）
    text_overlay_config = db.Column(db.Text)               # JSON格式的文字叠加配置

    # NEW: 高级模板功能（支持占位符）
    timeline_json = db.Column(db.Text)                     # 完整Timeline JSON（含占位符）
    output_media_config = db.Column(db.Text)               # 输出配置JSON
    editing_produce_config = db.Column(db.Text)            # 制作配置（封面等）JSON
    formatter_type = db.Column(db.String(50), default='default')  # 格式化器类型

    # NEW: 模板元数据
    category = db.Column(db.String(100), default='general') # 分类：medical/education/general
    is_advanced = db.Column(db.Boolean, default=False)      # 是否为高级模板（使用占位符）
    thumbnail_url = db.Column(db.String(255))               # 缩略图URL

    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    processing_tasks = db.relationship('ProcessingTask', backref='video_template', lazy='dynamic')

    def __repr__(self):
        return f'<VideoTemplate {self.name}>'

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
    task_style_id = db.Column(db.Integer, db.ForeignKey('task_style.id'))  # TaskStyle模板ID（兼容旧版）
    doctor_info_id = db.Column(db.Integer, db.ForeignKey('doctor_info.id'))  # 医生信息ID
    video_template_id = db.Column(db.Integer, db.ForeignKey('video_template.id'))  # 视频模板ID
    status = db.Column(db.String(50), default='pending')  # 任务状态：pending/processing/completed/failed
    ice_job_id = db.Column(db.String(255))                # 阿里云ICE作业ID
    ice_project_id = db.Column(db.String(255))            # 阿里云ICE工程ID
    output_oss_url = db.Column(db.String(255))            # 成品视频OSS地址
    progress = db.Column(db.Integer, default=0)           # 处理进度(0-100)
    error_message = db.Column(db.Text)                    # 错误信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)                 # 完成时间

    # NEW: 使用高级模板标志
    use_advanced_timeline = db.Column(db.Boolean, default=False)  # 是否使用高级Timeline（占位符）

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
