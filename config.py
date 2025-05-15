import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    
    # OSS配置
    OSS_ACCESS_KEY_ID = os.getenv('OSS_ACCESS_KEY_ID')
    OSS_ACCESS_KEY_SECRET = os.getenv('OSS_ACCESS_KEY_SECRET')
    OSS_BUCKET_NAME = os.getenv('OSS_BUCKET_NAME')
    OSS_ENDPOINT = os.getenv('OSS_ENDPOINT', 'http://oss-cn-shanghai.aliyuncs.com')
    
    # 上传配置
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 限制上传文件大小为500MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'}