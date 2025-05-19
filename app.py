from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from models import db, File, Template, TaskStyle
import os
from datetime import datetime
from dotenv import load_dotenv
import alibabacloud_oss_v2 as oss
from config import Config

# 加载环境变量
load_dotenv()

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
        result = self.client.delete_object(oss.DeleteObjectRequest(
            bucket=self.config.bucket_name,
            key=oss_path
        ))
        return result.status == 'OK' or result.status == 200

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
            return jsonify({'error': 'OSS配置不完整，请检查环境变量'}), 500
        
        # 准备上传
        oss_path = FileHandler.generate_oss_path(file.filename)
        file_content = file.read()
        file_size = len(file_content)  # 获取文件内容的实际大小
        
        # 执行上传
        oss_client = OSSClient(oss_config)
        if oss_client.upload_file(file_content, oss_path):
            file_url = oss_config.get_file_url(oss_path)
            print(f"文件上传成功，URL: {file_url}")
            
            # 创建任务记录
            task = {
                'file_url': file_url,
                'template': template,
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            # 记录到数据库
            new_file = File(
                filename=file.filename,
                oss_url=file_url,
                size=file_size  # 使用实际的文件大小
            )
            db.session.add(new_file)
            db.session.commit()
            
            return jsonify({
                'message': '文件上传成功',
                'file_url': file_url,
                'task_id': str(task['created_at'])
            })
            
        else:
            raise Exception("文件上传失败")
            
    except Exception as e:
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
            return jsonify({'error': 'OSS配置不完整，请检查环境变量'}), 500
        
        # 准备上传
        oss_path = TemplateHandler.generate_oss_path(file.filename)
        file_content = file.read()
        file_size = len(file_content)  # 获取文件内容的实际大小
        
        # 执行上传
        oss_client = OSSClient(oss_config)
        if oss_client.upload_file(file_content, oss_path):
            file_url = oss_config.get_file_url(oss_path)
            print(f"文件上传成功，URL: {file_url}")
            
            # 创建任务记录
            task = {
                'file_url': file_url,
                'template': template,
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            # 记录到数据库
            new_file = Template(
                filename=file.filename,
                oss_url=file_url,
                size=file_size  # 使用实际的文件大小
            )
            db.session.add(new_file)
            db.session.commit()
            
            return jsonify({
                'message': '文件上传成功',
                'file_url': file_url,
                'task_id': str(task['created_at'])
            })
            
        else:
            raise Exception("文件上传失败")
            
    except Exception as e:
        return jsonify({'error': f'上传失败: {str(e)}'}), 500
# 删除模版文件    
@app.route('/api/upload/templates/delete/<int:file_id>', methods=['POST'])
def template_delete_file(file_id):
    file = Template.query.get_or_404(file_id)
    # 从 OSS 初始化
    oss_config = OSSConfig()
    oss_client = OSSClient(oss_config)

    # 从 OSS 删除文件
    oss_path = "templates/" + file.oss_url.split('/')[-1]
    print(oss_path)
    oss_client.delete_file(oss_path)    
    
    # 删除数据库记录
    db.session.delete(file)
    db.session.commit()
    
    return redirect(url_for('templates'))
# 删除视频    
@app.route('/api/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    # 从 OSS 初始化
    oss_config = OSSConfig()
    oss_client = OSSClient(oss_config)

    # 从 OSS 删除文件
    oss_path = "uploads/" + file.oss_url.split('/')[-1]
    print(oss_path)
    oss_client.delete_file(oss_path)    
    
    # 删除数据库记录
    db.session.delete(file)
    db.session.commit()
    
    return redirect(url_for('files'))

@app.route('/api/save_taskstyle', methods=['POST'])
def save_taskstyle():
    try:
        data = request.get_json()
        print(data.get('background_file'))
        # 创建新的TaskStyle记录
        new_taskstyle = TaskStyle(
            open_oss_url=data.get('header_file'),
            close_oss_url=data.get('footer_file'),
            title_picture_oss_url_1=data.get('background_file'),
            title_picture_oss_url_2=data.get('background2_file'),
            change_material_oss_url=data.get('transition_file'),
            description='自定义模板'  # 可以根据需要修改描述
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

if __name__ == '__main__':
    app.run(debug=True)