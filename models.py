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
    """视频模板表（统一模板系统）

    支持两种模式：
    - 简单模式 (is_advanced=False): 基于字段的表单配置，适用于基础场景
    - 高级模式 (is_advanced=True): 基于Timeline JSON的完整配置，支持占位符和自定义场景

    字段说明：
    - 简单模式字段: header_video_url, footer_video_url, enable_subtitle, subtitle_position
    - 高级模式字段: timeline_json, output_media_config, editing_produce_config, formatter_type
    - 占位符支持: $main_video, $mainSubtitleDepart, $mainSubtitleName, $beginingSubtitleTitle, $beginingAudioTitle

    使用场景：
    - medical: 医疗视频模板（医生信息、科室等）
    - education: 教育视频模板
    - general: 通用视频模板
    - migrated: 从TaskStyle迁移的模板
    """
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

    # 高级模板功能（支持占位符）
    timeline_json = db.Column(db.Text)                     # 完整Timeline JSON（含占位符）
    output_media_config = db.Column(db.Text)               # 输出配置JSON
    editing_produce_config = db.Column(db.Text)            # 制作配置（封面等）JSON
    formatter_type = db.Column(db.String(50), default='default')  # 格式化器类型

    # 模板元数据
    category = db.Column(db.String(100), default='general') # 分类：medical/education/general/migrated
    is_advanced = db.Column(db.Boolean, default=False)      # 是否为高级模板（使用占位符）
    thumbnail_url = db.Column(db.String(255))               # 缩略图URL

    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    processing_tasks = db.relationship('ProcessingTask', backref='video_template', lazy='dynamic')

    def validate_timeline_json(self) -> tuple[bool, str]:
        """验证timeline_json字段格式"""
        if not self.timeline_json:
            return True, ""  # 简单模式下可以为空

        try:
            import json
            timeline = json.loads(self.timeline_json)

            # 基本结构验证
            if "VideoTracks" not in timeline:
                return False, "缺少VideoTracks字段"

            if not isinstance(timeline["VideoTracks"], list):
                return False, "VideoTracks必须是数组"

            if len(timeline["VideoTracks"]) == 0:
                return False, "VideoTracks不能为空"

            video_track = timeline["VideoTracks"][0]
            if "VideoTrackClips" not in video_track:
                return False, "缺少VideoTrackClips字段"

            if not isinstance(video_track["VideoTrackClips"], list):
                return False, "VideoTrackClips必须是数组"

            return True, ""

        except json.JSONDecodeError as e:
            return False, f"JSON格式错误: {str(e)}"
        except Exception as e:
            return False, f"验证失败: {str(e)}"

    def validate_output_media_config(self) -> tuple[bool, str]:
        """验证output_media_config字段格式"""
        if not self.output_media_config:
            return True, ""  # 可选字段

        try:
            import json
            config = json.loads(self.output_media_config)

            # 验证Width和Height范围
            if "Width" in config:
                width = config["Width"]
                if not isinstance(width, int) or width < 240 or width > 3840:
                    return False, "Width必须是240-3840之间的整数"

            if "Height" in config:
                height = config["Height"]
                if not isinstance(height, int) or height < 240 or height > 2160:
                    return False, "Height必须是240-2160之间的整数"

            return True, ""

        except json.JSONDecodeError as e:
            return False, f"JSON格式错误: {str(e)}"
        except Exception as e:
            return False, f"验证失败: {str(e)}"

    def validate_text_overlay_config(self) -> tuple[bool, str]:
        """验证text_overlay_config字段格式"""
        if not self.text_overlay_config:
            return True, ""  # 可选字段

        try:
            import json
            config = json.loads(self.text_overlay_config)

            # 必须是数组
            if not isinstance(config, list):
                return False, "text_overlay_config必须是数组"

            # 验证每个overlay元素
            for i, overlay in enumerate(config):
                if not isinstance(overlay, dict):
                    return False, f"第{i+1}个元素必须是对象"

                if "text" not in overlay:
                    return False, f"第{i+1}个元素缺少text字段"

                if "x" not in overlay or "y" not in overlay:
                    return False, f"第{i+1}个元素缺少x或y坐标字段"

            return True, ""

        except json.JSONDecodeError as e:
            return False, f"JSON格式错误: {str(e)}"
        except Exception as e:
            return False, f"验证失败: {str(e)}"

    def validate_all_json_fields(self) -> dict[str, tuple[bool, str]]:
        """验证所有JSON字段"""
        results = {}
        results['timeline_json'] = self.validate_timeline_json()
        results['output_media_config'] = self.validate_output_media_config()
        results['text_overlay_config'] = self.validate_text_overlay_config()
        return results

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
    """任务样式模板（已弃用 - Deprecated）

    .. deprecated::
        此模型仅保留用于向后兼容现有数据。
        新项目请使用 VideoTemplate 模型。

        迁移指南:
        - 数据迁移: 使用 scripts/migrate_manager.py 进行自动迁移
        - 文档参考: docs/MIGRATION_GUIDE.md
        - API变更: 参见 CLAUDE.md 中的模板模型说明

    历史说明:
    此模型是早期的模板系统，使用固定字段存储片头、片尾、背景等素材。
    已被 VideoTemplate 模型替代，后者支持更灵活的JSON配置和占位符功能。

    注意:
    - 此模型schema已冻结，不再添加新功能
    - 使用时会触发 DeprecationWarning
    - 建议尽快迁移到 VideoTemplate
    """
    __tablename__ = 'task_style'

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

    # 关联关系
    processing_tasks = db.relationship('ProcessingTask', backref='task_style', lazy='dynamic')

    def __repr__(self):
        import warnings
        warnings.warn(
            f"TaskStyle已弃用，请迁移到VideoTemplate。参见docs/MIGRATION_GUIDE.md",
            DeprecationWarning,
            stacklevel=2
        )
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
