from flask import Flask
from models import db
from config import Config
from services.oss_service import OSSConfig
import os
import logging
from dotenv import load_dotenv

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


def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 数据库初始化
    db.init_app(app)

    # 注册 Blueprint
    from blueprints.pages import pages_bp
    from blueprints.file_api import file_bp
    from blueprints.task_api import task_bp
    from blueprints.doctor_api import doctor_bp
    from blueprints.template_api import template_bp
    from blueprints.legacy_api import legacy_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(template_bp)
    app.register_blueprint(legacy_bp)

    # Jinja2 过滤器
    @app.template_filter('beijing_time')
    def beijing_time_filter(dt):
        from utils.time_helpers import format_datetime_beijing
        return format_datetime_beijing(dt, '%Y-%m-%d %H:%M')

    # 启动验证
    with app.app_context():
        db.create_all()
        _validate_config(app)

    return app


def _validate_config(app):
    """验证应用启动时配置是否完整"""
    warnings = []

    oss_config = OSSConfig()
    if not oss_config.is_valid():
        warnings.append("警告: OSS配置不完整，文件上传功能将无法使用")
        warnings.append(f"  - OSS_ACCESS_KEY_ID: {'已设置' if os.getenv('OSS_ACCESS_KEY_ID') else '未设置'}")
        warnings.append(f"  - OSS_ACCESS_KEY_SECRET: {'已设置' if os.getenv('OSS_ACCESS_KEY_SECRET') else '未设置'}")
        warnings.append(f"  - OSS_BUCKET_NAME: {'已设置' if os.getenv('OSS_BUCKET_NAME') else '未设置'}")

    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        logger.info("数据库连接正常")
    except Exception as e:
        warnings.append(f"警告: 数据库连接异常 - {str(e)}")

    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        try:
            os.makedirs(upload_folder)
            logger.info(f"创建上传目录: {upload_folder}")
        except Exception as e:
            warnings.append(f"警告: 无法创建上传目录 - {str(e)}")

    if warnings:
        logger.warning("=" * 60)
        logger.warning("配置验证警告:")
        for warning in warnings:
            logger.warning(warning)
        logger.warning("=" * 60)
    else:
        logger.info("配置验证通过，所有功能正常")


# 兼容: 允许 task_processor 等模块 import app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
