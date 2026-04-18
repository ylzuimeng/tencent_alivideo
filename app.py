from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from models import db, File, Template, TaskStyle, ProcessingTask, DoctorInfo, VideoTemplate
import os
import logging
from datetime import datetime
from utils.time_helpers import utcnow, serialize_datetime
from dotenv import load_dotenv
import alibabacloud_oss_v2 as oss
from config import Config

# 加载环境变量
load_dotenv()

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask应用初始化
app = Flask(__name__)
app.config.from_object(Config)

# 数据库初始化
db.init_app(app)
with app.app_context():
    db.create_all()


# OSS配置类
class OSSConfig:
    def __init__(self):
        self.access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
        self.access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
        self.bucket_name = os.getenv('OSS_BUCKET_NAME')
        self.endpoint = os.getenv('OSS_ENDPOINT', 'oss-cn-shanghai.aliyuncs.com')
        self.oss_endpoint = f'https://{self.endpoint}'

    def is_valid(self):
        return all([
            self.access_key_id,
            self.access_key_secret,
            self.bucket_name,
            self.endpoint
        ])

    def get_file_url(self, oss_path):
        return f'https://{self.bucket_name}.{self.endpoint}/{oss_path}'

# OSS客户端类
class OSSClient:
    def __init__(self, config):
        self.config = config
        self.client = self._create_client()

    def _create_client(self):
        credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()
        cfg = oss.config.load_default()
        cfg.credentials_provider = credentials_provider
        cfg.region = 'cn-shanghai'
        cfg.connection_timeout = 300
        cfg.max_retries = 3
        cfg.endpoint = self.config.oss_endpoint
        return oss.Client(cfg)

    def upload_file(self, file_content, oss_path):
        result = self.client.put_object(oss.PutObjectRequest(
            bucket=self.config.bucket_name,
            key=oss_path,
            body=file_content
        ))
        return result.status == 'OK' or result.status == 200
    
    def delete_file(self, oss_path):
        """删除OSS文件，返回是否成功"""
        try:
            request = oss.DeleteObjectRequest(
                bucket=self.config.bucket_name,
                key=oss_path
            )
            result = self.client.delete_object(request)

            # 记录详细的响应信息
            logger.info(f"OSS删除响应 - status: {result.status}, body: {result.body}")

            # 检查多种可能的成功状态
            # 阿里云OSS SDK可能返回不同的状态码
            if result.status == 200 or result.status == 204 or result.status == 'OK':
                return True

            # 如果状态码不是预期的成功状态，记录警告
            logger.warning(f"OSS删除返回状态码: {result.status}, 路径: {oss_path}")

            # 尝试从body中判断
            if hasattr(result, 'body') and result.body:
                logger.warning(f"OSS删除响应body: {result.body}")

            return False

        except Exception as e:
            logger.error(f"OSS删除异常: {str(e)}, 路径: {oss_path}")
            return False

# 文件处理类
class FileHandler:
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in FileHandler.ALLOWED_EXTENSIONS

    @staticmethod
    def generate_oss_path(filename):
        safe_filename = secure_filename(filename)
        timestamp = utcnow().strftime('%Y%m%d_%H%M%S')
        return f'uploads/{timestamp}_{safe_filename}'

# 模版处理类
class TemplateHandler:

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in FileHandler.ALLOWED_EXTENSIONS

    @staticmethod
    def generate_oss_path(filename):
        safe_filename = secure_filename(filename)
        timestamp = utcnow().strftime('%Y%m%d_%H%M%S')
        return f'templates/{timestamp}_{safe_filename}'

# 启动时验证配置
def validate_config():
    """验证应用启动时配置是否完整"""
    warnings = []

    # 验证OSS配置
    oss_config = OSSConfig()
    if not oss_config.is_valid():
        warnings.append("警告: OSS配置不完整，文件上传功能将无法使用")
        warnings.append(f"  - OSS_ACCESS_KEY_ID: {'已设置' if os.getenv('OSS_ACCESS_KEY_ID') else '未设置'}")
        warnings.append(f"  - OSS_ACCESS_KEY_SECRET: {'已设置' if os.getenv('OSS_ACCESS_KEY_SECRET') else '未设置'}")
        warnings.append(f"  - OSS_BUCKET_NAME: {'已设置' if os.getenv('OSS_BUCKET_NAME') else '未设置'}")

    # 验证数据库
    try:
        # 尝试执行简单查询验证数据库连接
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        logger.info("数据库连接正常")
    except Exception as e:
        warnings.append(f"警告: 数据库连接异常 - {str(e)}")

    # 验证上传目录
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        try:
            os.makedirs(upload_folder)
            logger.info(f"创建上传目录: {upload_folder}")
        except Exception as e:
            warnings.append(f"警告: 无法创建上传目录 - {str(e)}")

    # 输出警告信息
    if warnings:
        logger.warning("=" * 60)
        logger.warning("配置验证警告:")
        for warning in warnings:
            logger.warning(warning)
        logger.warning("=" * 60)
    else:
        logger.info("配置验证通过，所有功能正常")

# 在应用上下文中验证配置
with app.app_context():
    validate_config()

@app.route('/files')
def files():
    files = File.query.all()
    return render_template('files.html', files=files)

@app.route('/files/enhanced')
def files_enhanced():
    """增强版文件管理页面（支持视频预览）"""
    return render_template('files_enhanced.html')

@app.route('/test/api')
def test_api():
    """API 测试页面"""
    return render_template('test_api.html')


# ==================== 文件管理API ====================

@app.route('/api/files', methods=['GET'])
def get_files_api():
    """获取文件列表API"""
    try:
        files = File.query.order_by(File.upload_time.desc()).all()
        return jsonify({
            'success': True,
            'files': [
                {
                    'id': f.id,
                    'filename': f.filename,
                    'oss_url': f.oss_url,
                    'size': f.size,
                    'upload_time': serialize_datetime(f.upload_time, to_beijing=True)
                }
                for f in files
            ]
        })
    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/doctors')
def doctors():
    """医生信息管理页面"""
    return render_template('doctors.html')
# 路由处理
@app.route('/')
def index():
    return render_template('upload_videos.html')

@app.route('/upload/video')
def upload():
    return render_template('upload_videos.html')

@app.route('/upload/enhanced')
def upload_enhanced():
    """增强版视频上传页面"""
    return render_template('upload_enhanced.html')

@app.route('/task_list')
def task_list():
    return render_template('task_list.html')

@app.route('/templates')
def templates():
    files = Template.query.all()
    return render_template('templates.html', files=files)

@app.route('/taskstyles')
def taskstyles():
    files = Template.query.all()
    taskstyles = TaskStyle.query.all()
    return render_template('taskstyles.html', files=files, taskstyles=taskstyles)

@app.route('/video_templates')
def video_templates():
    """视频模板配置页面 - 重定向到统一界面"""
    return redirect('/templates/unified')
    files = File.query.all()  # 从File表获取视频素材，而不是Template表
    return render_template('video_templates.html', files=files)

# 获取模板列表API
@app.route('/api/templates')
def get_templates():
    templates = Template.query.all()
    return jsonify([{
        'id': t.id,
        'filename': t.filename,
        'oss_url': t.oss_url,
        'upload_time': serialize_datetime(t.upload_time, to_beijing=True)
    } for t in templates])

# 文件上传处理
@app.route('/api/upload/video', methods=['POST'])
def upload_file():
    try:
        # 初始化配置
        oss_config = OSSConfig()

        # 验证文件存在
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400

        file = request.files['file']
        template = request.form.get('template', '')

        # 验证文件有效性
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        if not FileHandler.allowed_file(file.filename):
            return jsonify({'error': '不支持的文件格式'}), 400

        # 验证OSS配置
        if not oss_config.is_valid():
            logger.error("OSS配置不完整")
            return jsonify({'error': 'OSS配置不完整，请检查环境变量'}), 500

        # 准备上传
        oss_path = FileHandler.generate_oss_path(file.filename)
        file_content = file.read()
        file_size = len(file_content)

        # 执行上传
        oss_client = OSSClient(oss_config)
        if oss_client.upload_file(file_content, oss_path):
            file_url = oss_config.get_file_url(oss_path)
            logger.info(f"文件上传成功，URL: {file_url}")

            # 使用事务记录到数据库
            try:
                new_file = File(
                    filename=file.filename,
                    oss_url=file_url,
                    size=file_size
                )
                db.session.add(new_file)
                db.session.commit()

                return jsonify({
                    'message': '文件上传成功',
                    'file_id': new_file.id,
                    'file_url': file_url,
                    'filename': file.filename,
                    'task_id': utcnow().isoformat()
                })
            except Exception as db_error:
                db.session.rollback()
                logger.error(f"数据库保存失败: {str(db_error)}")
                # 数据库保存失败，尝试回滚OSS删除
                try:
                    oss_client.delete_file(oss_path)
                    logger.info(f"已回滚删除OSS文件: {oss_path}")
                except Exception as rollback_error:
                    logger.error(f"回滚删除OSS文件失败: {str(rollback_error)}")
                return jsonify({'error': '数据库保存失败'}), 500
        else:
            raise Exception("文件上传失败")

    except Exception as e:
        logger.error(f"上传文件异常: {str(e)}")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

# 模板上传处理
@app.route('/api/upload/template', methods=['POST'])
def upload_template():
    try:
        # 初始化配置
        oss_config = OSSConfig()

        # 验证文件存在
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400

        file = request.files['file']
        template = request.form.get('template', '')

        # 验证文件有效性
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        if not FileHandler.allowed_file(file.filename):
            return jsonify({'error': '不支持的文件格式'}), 400

        # 验证OSS配置
        if not oss_config.is_valid():
            logger.error("OSS配置不完整")
            return jsonify({'error': 'OSS配置不完整，请检查环境变量'}), 500

        # 准备上传
        oss_path = TemplateHandler.generate_oss_path(file.filename)
        file_content = file.read()
        file_size = len(file_content)

        # 执行上传
        oss_client = OSSClient(oss_config)
        if oss_client.upload_file(file_content, oss_path):
            file_url = oss_config.get_file_url(oss_path)
            logger.info(f"模板文件上传成功，URL: {file_url}")

            # 使用事务记录到数据库
            try:
                new_file = Template(
                    filename=file.filename,
                    oss_url=file_url,
                    size=file_size
                )
                db.session.add(new_file)
                db.session.commit()

                return jsonify({
                    'message': '文件上传成功',
                    'file_id': new_file.id,
                    'file_url': file_url,
                    'filename': file.filename,
                    'task_id': utcnow().isoformat()
                })
            except Exception as db_error:
                db.session.rollback()
                logger.error(f"数据库保存失败: {str(db_error)}")
                # 数据库保存失败，尝试回滚OSS删除
                try:
                    oss_client.delete_file(oss_path)
                    logger.info(f"已回滚删除OSS文件: {oss_path}")
                except Exception as rollback_error:
                    logger.error(f"回滚删除OSS文件失败: {str(rollback_error)}")
                return jsonify({'error': '数据库保存失败'}), 500
        else:
            raise Exception("文件上传失败")

    except Exception as e:
        logger.error(f"上传模板文件异常: {str(e)}")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500
# 删除模版文件
@app.route('/api/upload/templates/delete/<int:file_id>', methods=['POST'])
def template_delete_file(file_id):
    try:
        file = Template.query.get_or_404(file_id)

        # 从OSS初始化
        oss_config = OSSConfig()
        oss_client = OSSClient(oss_config)

        # 从OSS删除文件 - 提取原始文件名
        # OSS路径格式: templates/{timestamp}_{filename}
        filename = file.oss_url.split('/')[-1]
        oss_path = f"templates/{filename}"

        logger.info(f"准备删除OSS文件: {oss_path}")
        delete_success = oss_client.delete_file(oss_path)

        # 即使OSS删除失败，也允许删除数据库记录
        if not delete_success:
            logger.warning(f"OSS文件删除失败或文件不存在: {oss_path}")

        # 删除数据库记录
        db.session.delete(file)
        db.session.commit()

        logger.info(f"模板文件记录删除成功: {file.filename}")
        return redirect(url_for('templates'))

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除模板文件失败: {str(e)}")
        return jsonify({'error': f'删除失败: {str(e)}'}), 500
# 删除视频
@app.route('/api/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    try:
        file = File.query.get_or_404(file_id)

        # 从OSS初始化
        oss_config = OSSConfig()
        oss_client = OSSClient(oss_config)

        # 从OSS删除文件 - 提取原始文件名
        # OSS路径格式: uploads/{timestamp}_{filename}
        filename = file.oss_url.split('/')[-1]
        oss_path = f"uploads/{filename}"

        logger.info(f"准备删除OSS文件: {oss_path}")
        delete_success = oss_client.delete_file(oss_path)

        # 即使OSS删除失败，也允许删除数据库记录（文件可能已经不存在）
        # 这提供了更好的用户体验
        if not delete_success:
            logger.warning(f"OSS文件删除失败或文件不存在: {oss_path}")
            # 继续删除数据库记录，但给用户一个提示
            # 在实际生产环境中，你可能想要不同的处理策略

        # 删除数据库记录
        db.session.delete(file)
        db.session.commit()

        logger.info(f"文件记录删除成功: {file.filename}")
        return redirect(url_for('files'))

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除文件记录失败: {str(e)}")
        return jsonify({'error': f'删除失败: {str(e)}'}), 500

@app.route('/api/save_taskstyle', methods=['POST'])
def save_taskstyle():
    try:
        data = request.get_json()
        logger.debug(f"接收到的数据: {data}")

        # 验证模板名称
        if not data.get('name'):
            return jsonify({'error': '模板名称不能为空'}), 400

        # 创建新的TaskStyle记录
        new_taskstyle = TaskStyle(
            name=data.get('name'),
            open_oss_url=data.get('header_file'),
            close_oss_url=data.get('footer_file'),
            title_picture_oss_url_1=data.get('background_file'),
            title_picture_oss_url_2=data.get('background2_file'),
            change_material_oss_url=data.get('transition_file'),
            description=data.get('description', f"模板：{data.get('name')}")
        )
        
        # 保存到数据库
        db.session.add(new_taskstyle)
        db.session.commit()
        
        return jsonify({
            'message': '模板保存成功',
            'id': new_taskstyle.id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== TaskStyle API ====================

@app.route('/api/taskstyles')
def get_taskstyles_api():
    """获取TaskStyle列表供前端选择"""
    try:
        taskstyles = TaskStyle.query.order_by(TaskStyle.created_at.desc()).all()

        result = []
        for ts in taskstyles:
            result.append({
                'id': ts.id,
                'name': ts.name or '未命名模板',
                'open_oss_url': ts.open_oss_url,
                'close_oss_url': ts.close_oss_url,
                'title_picture_oss_url_1': ts.title_picture_oss_url_1,
                'title_picture_oss_url_2': ts.title_picture_oss_url_2,
                'change_material_oss_url': ts.change_material_oss_url,
                'description': ts.description,
                'created_at': serialize_datetime(ts.created_at, to_beijing=True)
            })

        logger.info(f"返回TaskStyle列表，共{len(result)}个模板")
        return jsonify({'taskstyles': result})

    except Exception as e:
        logger.error(f"获取TaskStyle列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 删除task
@app.route('/api/delete_taskstyle/<int:taskstyle_id>', methods=['POST'])
def taskstyle_delete_file(taskstyle_id):
    taskstyle = TaskStyle.query.get_or_404(taskstyle_id)

    # 删除数据库记录
    db.session.delete(taskstyle)
    db.session.commit()

    return redirect(url_for('taskstyles'))

# ==================== 任务管理API ====================

@app.route('/api/tasks/create', methods=['POST'])
def create_task():
    """创建视频处理任务"""
    try:
        data = request.get_json()

        # 验证参数
        if not data.get('source_file_id'):
            return jsonify({'error': '缺少source_file_id参数'}), 400

        # 获取源文件
        source_file = File.query.get(data['source_file_id'])
        if not source_file:
            return jsonify({'error': '源文件不存在'}), 404

        # 生成任务名称
        task_name = data.get('task_name', f"处理_{source_file.filename}")

        # 导入任务处理器
        from services.task_processor import task_processor

        # 检查是否使用高级模板（支持占位符）
        use_advanced_timeline = False
        if data.get('video_template_id'):
            template = VideoTemplate.query.get(data['video_template_id'])
            if template and template.is_advanced:
                use_advanced_timeline = True

        # 创建任务
        task = task_processor.create_task(
            task_name=task_name,
            source_file_id=data['source_file_id'],
            task_style_id=data.get('task_style_id'),
            doctor_info_id=data.get('doctor_info_id'),
            video_template_id=data.get('video_template_id'),
            use_advanced_timeline=use_advanced_timeline
        )

        return jsonify({
            'message': '任务创建成功',
            'task_id': task.id,
            'task_name': task.task_name,
            'status': task.status
        })

    except Exception as e:
        logger.error(f"创建任务失败: {str(e)}")
        return jsonify({'error': f'创建任务失败: {str(e)}'}), 500


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取任务列表"""
    try:
        from services.task_processor import task_processor

        tasks = task_processor.get_all_tasks(limit=50)
        return jsonify(tasks)

    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        return jsonify({'error': f'获取任务列表失败: {str(e)}'}), 500


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task_detail(task_id):
    """获取任务详情"""
    try:
        from services.task_processor import task_processor

        task = task_processor.get_task_status(task_id)
        if not task:
            return jsonify({'error': '任务不存在'}), 404

        return jsonify(task)

    except Exception as e:
        logger.error(f"获取任务详情失败: {str(e)}")
        return jsonify({'error': f'获取任务详情失败: {str(e)}'}), 500


@app.route('/api/tasks/<int:task_id>/progress', methods=['GET'])
def get_task_progress(task_id):
    """获取任务进度"""
    try:
        from services.task_processor import task_processor

        task = task_processor.get_task_status(task_id)
        if not task:
            return jsonify({'error': '任务不存在'}), 404

        return jsonify({
            'task_id': task['id'],
            'status': task['status'],
            'progress': task['progress'],
            'error_message': task['error_message']
        })

    except Exception as e:
        logger.error(f"获取任务进度失败: {str(e)}")
        return jsonify({'error': f'获取任务进度失败: {str(e)}'}), 500


@app.route('/api/tasks/<int:task_id>/download', methods=['GET'])
def download_task_output(task_id):
    """下载成品视频"""
    try:
        task = ProcessingTask.query.get_or_404(task_id)

        # 验证任务状态
        if task.status != 'completed':
            return jsonify({'error': f'任务未完成，当前状态: {task.status}'}), 400

        if not task.output_oss_url:
            return jsonify({'error': '成品视频URL不存在'}), 404

        # 返回下载URL
        return jsonify({
            'message': '获取下载链接成功',
            'download_url': task.output_oss_url,
            'task_name': task.task_name,
            'completed_at': task.completed_at.isoformat()
        })

    except Exception as e:
        logger.error(f"下载成品失败: {str(e)}")
        return jsonify({'error': f'下载成品失败: {str(e)}'}), 500


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    try:
        task = ProcessingTask.query.get_or_404(task_id)

        # 如果任务已完成，尝试删除OSS上的成品文件
        if task.status == 'completed' and task.output_oss_url:
            try:
                oss_config = OSSConfig()
                oss_client = OSSClient(oss_config)
                filename = task.output_oss_url.split('/')[-1]
                oss_path = f"processed_videos/{filename}"
                oss_client.delete_file(oss_path)
                logger.info(f"已删除成品文件: {oss_path}")
            except Exception as e:
                logger.warning(f"删除OSS文件失败: {str(e)}")

        # 删除数据库记录
        db.session.delete(task)
        db.session.commit()

        return jsonify({'message': '任务删除成功'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除任务失败: {str(e)}")
        return jsonify({'error': f'删除任务失败: {str(e)}'}), 500


@app.route('/api/tasks/<int:task_id>/retry', methods=['POST'])
def retry_task(task_id):
    """重试失败的任务"""
    try:
        from services.task_processor import task_processor

        task = ProcessingTask.query.get_or_404(task_id)

        # 检查任务状态
        if task.status != 'failed':
            return jsonify({'error': '只能重试失败的任务'}), 400

        # 重置任务状态
        task.status = 'pending'
        task.progress = 0
        task.error_message = None
        db.session.commit()

        # 重新提交处理
        task_processor.executor.submit(task_processor._process_task, task.id)

        return jsonify({'message': '任务已重新提交处理'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"重试任务失败: {str(e)}")
        return jsonify({'error': f'重试失败: {str(e)}'}), 500

    """删除任务"""
    try:
        task = ProcessingTask.query.get_or_404(task_id)

        # 如果任务已完成，尝试删除OSS上的成品文件
        if task.status == 'completed' and task.output_oss_url:
            try:
                oss_config = OSSConfig()
                oss_client = OSSClient(oss_config)
                filename = task.output_oss_url.split('/')[-1]
                oss_path = f"processed_videos/{filename}"
                oss_client.delete_file(oss_path)
                logger.info(f"已删除成品文件: {oss_path}")
            except Exception as e:
                logger.warning(f"删除OSS文件失败: {str(e)}")

        # 删除数据库记录
        db.session.delete(task)
        db.session.commit()

        return jsonify({'message': '任务删除成功'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除任务失败: {str(e)}")
        return jsonify({'error': f'删除任务失败: {str(e)}'}), 500


# ==================== 医生信息管理API ====================

@app.route('/api/doctors/import', methods=['POST'])
def import_doctors():
    """导入医生信息Excel文件"""
    try:
        from services.doctor_service import doctor_service

        # 验证文件存在
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有文件上传'}), 400

        file = request.files['file']

        # 验证文件名
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'}), 400

        # 验证文件类型
        if not doctor_service.allowed_file(file.filename):
            return jsonify({'success': False, 'message': '不支持的文件格式，请上传.xlsx或.xls文件'}), 400

        # 保存临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            file.save(tmp_file.name)
            tmp_file_path = tmp_file.name

        try:
            # 导入数据
            success, message, doctors = doctor_service.import_from_excel(tmp_file_path)

            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'count': len(doctors)
                })
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400

        finally:
            # 删除临时文件
            import os
            try:
                os.unlink(tmp_file_path)
            except:
                pass

    except Exception as e:
        logger.error(f"导入医生信息失败: {str(e)}")
        return jsonify({'success': False, 'message': f'导入失败: {str(e)}'}), 500


@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    """获取医生列表"""
    try:
        from services.doctor_service import doctor_service

        # 获取分页和筛选参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search')
        hospital = request.args.get('hospital')
        department = request.args.get('department')
        batch_id = request.args.get('batch_id')

        # 查询数据
        doctors, total = doctor_service.get_doctors(
            page=page,
            per_page=per_page,
            search=search,
            hospital=hospital,
            department=department,
            batch_id=batch_id
        )

        # 返回结果
        return jsonify({
            'success': True,
            'doctors': [
                {
                    'id': d.id,
                    'name': d.name,
                    'hospital': d.hospital,
                    'department': d.department,
                    'title': d.title,
                    'batch_id': d.batch_id,
                    'is_validated': d.is_validated,
                    'created_at': serialize_datetime(d.created_at, to_beijing=True)
                }
                for d in doctors
            ],
            'total': total,
            'per_page': per_page
        })

    except Exception as e:
        logger.error(f"获取医生列表失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取列表失败: {str(e)}'}), 500


@app.route('/api/doctors/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    """获取医生详情"""
    try:
        from services.doctor_service import doctor_service

        doctor = doctor_service.get_doctor_by_id(doctor_id)
        if not doctor:
            return jsonify({'success': False, 'message': '医生信息不存在'}), 404

        return jsonify({
            'success': True,
            'doctor': {
                'id': doctor.id,
                'name': doctor.name,
                'hospital': doctor.hospital,
                'department': doctor.department,
                'title': doctor.title,
                'batch_id': doctor.batch_id,
                'is_validated': doctor.is_validated,
                'created_at': doctor.created_at.isoformat()
            }
        })

    except Exception as e:
        logger.error(f"获取医生详情失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取详情失败: {str(e)}'}), 500


@app.route('/api/doctors/<int:doctor_id>', methods=['PUT'])
def update_doctor(doctor_id):
    """更新医生信息"""
    try:
        from services.doctor_service import doctor_service

        data = request.get_json()
        success, message = doctor_service.update_doctor(doctor_id, **data)

        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        logger.error(f"更新医生信息失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@app.route('/api/doctors/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    """删除医生信息"""
    try:
        from services.doctor_service import doctor_service

        success, message = doctor_service.delete_doctor(doctor_id)

        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        logger.error(f"删除医生信息失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@app.route('/api/doctors/<int:doctor_id>/validate', methods=['POST'])
def validate_doctor(doctor_id):
    """校验医生信息"""
    try:
        from services.doctor_service import doctor_service

        success, message = doctor_service.validate_doctor(doctor_id)

        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        logger.error(f"校验医生信息失败: {str(e)}")
        return jsonify({'success': False, 'message': f'校验失败: {str(e)}'}), 500


@app.route('/api/doctors/batches', methods=['GET'])
def get_batches():
    """获取批次列表"""
    try:
        from services.doctor_service import doctor_service

        batches = doctor_service.get_batch_list()
        return jsonify({'success': True, 'batches': batches})

    except Exception as e:
        logger.error(f"获取批次列表失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取批次列表失败: {str(e)}'}), 500


# ==================== 视频模板管理API ====================

@app.route('/api/video_templates', methods=['POST'])
def create_video_template():
    """创建视频模板（支持简单模式和高级模式）"""
    try:
        data = request.get_json()

        # 验证必填字段
        if not data.get('name'):
            return jsonify({'success': False, 'message': '缺少必填字段: name'}), 400

        # 判断是否为高级模式
        is_advanced = data.get('is_advanced', False)

        # 高级模式：验证timeline_json
        if is_advanced:
            if not data.get('timeline_json'):
                return jsonify({'success': False, 'message': '高级模板必须提供 timeline_json'}), 400

            # 验证Timeline JSON
            from services.json_validator import validate_timeline_json
            is_valid, error_msg = validate_timeline_json(data.get('timeline_json'))
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': f'Timeline JSON验证失败: {error_msg}'
                }), 400

        # 简单模式：验证text_overlay_config（如果提供）
        else:
            if data.get('text_overlay_config'):
                from services.json_validator import validate_text_overlay_config
                is_valid, error_msg = validate_text_overlay_config(data['text_overlay_config'])
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'message': f'文字叠加配置验证失败: {error_msg}'
                    }), 400

        # 创建模板
        template = VideoTemplate(
            name=data.get('name'),
            is_advanced=is_advanced,
            category=data.get('category'),
            # 简单模式字段
            header_video_url=data.get('header_video_url'),
            footer_video_url=data.get('footer_video_url'),
            enable_subtitle=data.get('enable_subtitle', False),
            subtitle_position=data.get('subtitle_position', 'bottom'),
            subtitle_extract_audio=data.get('subtitle_extract_audio', True),
            text_overlay_config=data.get('text_overlay_config'),
            # 高级模式字段
            timeline_json=data.get('timeline_json'),
            output_media_config=data.get('output_media_config'),
            editing_produce_config=data.get('editing_produce_config'),
            formatter_type=data.get('formatter_type'),
            thumbnail_url=data.get('thumbnail_url'),
            description=data.get('description', '')
        )

        db.session.add(template)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '模板创建成功',
            'template_id': template.id
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建视频模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500


@app.route('/api/video_templates', methods=['GET'])
def get_video_templates():
    """获取视频模板列表"""
    try:
        templates = VideoTemplate.query.order_by(VideoTemplate.created_at.desc()).all()

        return jsonify({
            'success': True,
            'templates': [
                {
                    'id': t.id,
                    'name': t.name,
                    'header_video_url': t.header_video_url,
                    'footer_video_url': t.footer_video_url,
                    'enable_subtitle': t.enable_subtitle,
                    'subtitle_position': t.subtitle_position,
                    'subtitle_extract_audio': t.subtitle_extract_audio,
                    'is_advanced': t.is_advanced,  # 新增：标识高级模板
                    'category': t.category,  # 新增：模板分类
                    'description': t.description,
                    'created_at': serialize_datetime(t.created_at, to_beijing=True)
                }
                for t in templates
            ]
        })

    except Exception as e:
        logger.error(f"获取视频模板列表失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取列表失败: {str(e)}'}), 500


@app.route('/api/video_templates/<int:template_id>', methods=['GET'])
def get_video_template(template_id):
    """获取单个视频模板详情"""
    try:
        template = VideoTemplate.query.get_or_404(template_id)

        template_data = {
            'id': template.id,
            'name': template.name,
            'header_video_url': template.header_video_url,
            'footer_video_url': template.footer_video_url,
            'enable_subtitle': template.enable_subtitle,
            'subtitle_position': template.subtitle_position,
            'subtitle_extract_audio': template.subtitle_extract_audio,
            'text_overlay_config': template.text_overlay_config,
            'timeline_json': template.timeline_json,
            'output_media_config': template.output_media_config,
            'editing_produce_config': template.editing_produce_config,
            'formatter_type': template.formatter_type,
            'category': template.category,
            'is_advanced': template.is_advanced,
            'thumbnail_url': template.thumbnail_url,
            'description': template.description,
            'created_at': template.created_at.isoformat() if template.created_at else None,
            'updated_at': template.updated_at.isoformat() if template.updated_at else None
        }

        return jsonify({'success': True, 'template': template_data})

    except Exception as e:
        logger.error(f"获取视频模板详情失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'}), 500


@app.route('/api/video_templates/<int:template_id>', methods=['PUT'])
def update_video_template(template_id):
    """更新视频模板（支持简单模式和高级模式）"""
    try:
        template = VideoTemplate.query.get_or_404(template_id)
        data = request.get_json()

        # 验证高级模式的timeline_json（如果提供）
        if data.get('timeline_json'):
            from services.json_validator import validate_timeline_json
            is_valid, error_msg = validate_timeline_json(data['timeline_json'])
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': f'Timeline JSON验证失败: {error_msg}'
                }), 400

        # 验证简单模式的text_overlay_config（如果提供）
        if data.get('text_overlay_config'):
            from services.json_validator import validate_text_overlay_config
            is_valid, error_msg = validate_text_overlay_config(data['text_overlay_config'])
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': f'文字叠加配置验证失败: {error_msg}'
                }), 400

        # 更新基础字段
        if 'name' in data:
            template.name = data['name']
        if 'description' in data:
            template.description = data['description']
        if 'category' in data:
            template.category = data['category']
        if 'is_advanced' in data:
            template.is_advanced = data['is_advanced']

        # 更新简单模式字段
        if 'header_video_url' in data:
            template.header_video_url = data['header_video_url']
        if 'footer_video_url' in data:
            template.footer_video_url = data['footer_video_url']
        if 'enable_subtitle' in data:
            template.enable_subtitle = data['enable_subtitle']
        if 'subtitle_position' in data:
            template.subtitle_position = data['subtitle_position']
        if 'subtitle_extract_audio' in data:
            template.subtitle_extract_audio = data['subtitle_extract_audio']
        if 'text_overlay_config' in data:
            template.text_overlay_config = data['text_overlay_config']

        # 更新高级模式字段
        if 'timeline_json' in data:
            template.timeline_json = data['timeline_json']
        if 'output_media_config' in data:
            template.output_media_config = data['output_media_config']
        if 'editing_produce_config' in data:
            template.editing_produce_config = data['editing_produce_config']
        if 'formatter_type' in data:
            template.formatter_type = data['formatter_type']
        if 'thumbnail_url' in data:
            template.thumbnail_url = data['thumbnail_url']

        db.session.commit()

        return jsonify({'success': True, 'message': '更新成功'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新视频模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@app.route('/api/video_templates/<int:template_id>', methods=['DELETE'])
def delete_video_template(template_id):
    """删除视频模板"""
    try:
        template = VideoTemplate.query.get_or_404(template_id)

        # 检查是否有关联的处理任务
        if template.processing_tasks.count() > 0:
            return jsonify({'success': False, 'message': '该模板已关联处理任务，无法删除'}), 400

        db.session.delete(template)
        db.session.commit()

        return jsonify({'success': True, 'message': '删除成功'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除视频模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


# ==================== 统一模板管理页面 ====================

@app.route('/templates/unified')
def unified_templates_page():
    """统一模板管理页面"""
    return render_template('unified_templates.html')


# ==================== 模板转换API ====================

def _create_temp_template_from_simple(data: dict) -> VideoTemplate:
    """创建临时 VideoTemplate 用于转换（不持久化到数据库）"""
    return VideoTemplate(
        name=data.get('name', 'Temp'),
        header_video_url=data.get('header_video_url'),
        footer_video_url=data.get('footer_video_url'),
        enable_subtitle=data.get('enable_subtitle', False),
        subtitle_position=data.get('subtitle_position', 'bottom'),
        subtitle_extract_audio=data.get('subtitle_extract_audio', True),
        text_overlay_config=data.get('text_overlay_config'),
        is_advanced=False
    )


def _create_temp_template_from_advanced(timeline_json: str) -> VideoTemplate:
    """创建临时 VideoTemplate 用于转换（不持久化到数据库）"""
    return VideoTemplate(
        name='Temp',
        timeline_json=timeline_json,
        is_advanced=True
    )


@app.route('/api/video_templates/convert-demo', methods=['POST'])
def convert_template_demo():
    """在简单模式和高级模式之间转换模板（不保存到数据库）"""
    try:
        req_data = request.get_json()

        if not req_data.get('mode'):
            return jsonify({'success': False, 'message': '缺少mode参数'}), 400

        mode = req_data['mode']

        # 简单模式 → 高级模式
        if mode == 'simple-to-advanced':
            if not req_data.get('data'):
                return jsonify({'success': False, 'message': '缺少data参数'}), 400

            simple_data = req_data['data']
            if not simple_data.get('name'):
                return jsonify({'success': False, 'message': '缺少name字段'}), 400

            # 创建临时模板并转换
            temp_template = _create_temp_template_from_simple(simple_data)

            from services.template_converter import TemplateConverter
            result = TemplateConverter.simple_to_advanced(temp_template)

            # 验证生成的 Timeline
            from services.json_validator import validate_timeline_json
            is_valid, error = validate_timeline_json(result['timeline_json'])
            if not is_valid:
                return jsonify({'success': False, 'message': f'生成Timeline验证失败: {error}'}), 400

            return jsonify({
                'success': True,
                'timeline_json': result['timeline_json'],
                'output_media_config': result['output_media_config'],
                'auto_generated': result['auto_generated']
            })

        # 高级模式 → 简单模式
        elif mode == 'advanced-to-simple':
            if not req_data.get('timeline_json'):
                return jsonify({'success': False, 'message': '缺少timeline_json参数'}), 400

            timeline_json = req_data['timeline_json']

            # 验证输入 Timeline
            from services.json_validator import validate_timeline_json
            is_valid, error = validate_timeline_json(timeline_json)
            if not is_valid:
                return jsonify({'success': False, 'message': f'Timeline JSON验证失败: {error}'}), 400

            # 创建临时模板并转换
            temp_template = _create_temp_template_from_advanced(timeline_json)

            from services.template_converter import TemplateConverter
            result = TemplateConverter.advanced_to_simple(temp_template)

            return jsonify({
                'success': True,
                'data': result
            })

        else:
            return jsonify({'success': False, 'message': f'无效的mode: {mode}'}), 400

    except Exception as e:
        logger.error(f"模板转换失败: {str(e)}")
        return jsonify({'success': False, 'message': f'转换失败: {str(e)}'}), 500


# ==================== Jinja2 过滤器 ====================

@app.template_filter('beijing_time')
def beijing_time_filter(dt):
    """Jinja2过滤器：将UTC时间转换为北京时间字符串"""
    from utils.time_helpers import format_datetime_beijing
    return format_datetime_beijing(dt, '%Y-%m-%d %H:%M')


if __name__ == '__main__':
    app.run(debug=True)