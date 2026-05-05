import os
import logging
import alibabacloud_oss_v2 as oss
from config import Config

logger = logging.getLogger(__name__)


class OSSConfig:
    """OSS配置类"""
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


class OSSClient:
    """OSS客户端类"""
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

            logger.info(f"OSS删除响应 - status: {result.status}, body: {result.body}")

            if result.status == 200 or result.status == 204 or result.status == 'OK':
                return True

            logger.warning(f"OSS删除返回状态码: {result.status}, 路径: {oss_path}")

            if hasattr(result, 'body') and result.body:
                logger.warning(f"OSS删除响应body: {result.body}")

            return False

        except Exception as e:
            logger.error(f"OSS删除异常: {str(e)}, 路径: {oss_path}")
            return False
