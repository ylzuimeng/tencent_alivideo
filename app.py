from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from models import db, File, Template, TaskStyle, ProcessingTask
import os
import logging
from datetime import datetime
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
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'uploads/{timestamp}_{safe_filename}'

# 模版处理类
class TemplateHandler:

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in FileHandler.ALLOWED_EXTENSIONS

    @staticmethod
    def generate_oss_path(filename):
        safe_filename = secure_filename(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
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
# 路由处理
@app.route('/')
def index():
    return render_template('upload_videos.html')

@app.route('/upload/video')
def upload():
    return render_template('upload_videos.html')

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

# 获取模板列表API
@app.route('/api/templates')
def get_templates():
    templates = Template.query.all()
    return jsonify([{
        'id': t.id,
        'filename': t.filename,
        'oss_url': t.oss_url,
        'upload_time': t.upload_time.isoformat()
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
                    'task_id': datetime.now().isoformat()
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
                    'task_id': datetime.now().isoformat()
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
                'created_at': ts.created_at.isoformat()
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

        # 创建任务
        task = task_processor.create_task(
            task_name=task_name,
            source_file_id=data['source_file_id'],
            task_style_id=data.get('task_style_id')
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


if __name__ == '__main__':
    app.run(debug=True)