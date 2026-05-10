import os
import pytest
import sys

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 设置测试环境变量（在 import app 之前）
os.environ.setdefault('OSS_ACCESS_KEY_ID', 'test-key-id')
os.environ.setdefault('OSS_ACCESS_KEY_SECRET', 'test-key-secret')
os.environ.setdefault('OSS_BUCKET_NAME', 'test-bucket')
os.environ.setdefault('SECRET_KEY', 'test-secret')

from app import create_app
from models import db as _db


@pytest.fixture(scope='session')
def app():
    """创建测试用 Flask 应用"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',  # 内存数据库
    })
    return app


@pytest.fixture(scope='function')
def db(app):
    """每个测试函数使用独立的数据库"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture(scope='function')
def app_context(app, db):
    """提供应用上下文"""
    with app.app_context():
        yield
