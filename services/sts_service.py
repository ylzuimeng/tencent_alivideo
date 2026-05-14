"""
STS临时凭证服务

为前端直传OSS提供短期访问凭证，使用阿里云STS AssumeRole API。
凭证缓存在内存中，临近过期时自动刷新。
"""
import os
import json
import time
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# 内存缓存
_cached_credentials: Optional[Dict] = None
_cache_expiration: float = 0


def get_sts_credentials() -> Dict:
    """
    获取OSS上传凭证（带缓存）

    优先使用STS临时凭证；若未配置或失败，则回退到主账号凭证（仅限开发环境）。

    Returns:
        包含凭证和OSS配置的字典

    Raises:
        Exception: 所有方式均失败时抛出
    """
    global _cached_credentials, _cache_expiration

    # 缓存有效（距过期还有5分钟以上）
    if _cached_credentials and time.time() < _cache_expiration - 300:
        logger.debug("使用缓存的凭证")
        return _cached_credentials

    role_arn = os.getenv('OSS_STS_ROLE_ARN')
    if role_arn:
        try:
            return _assume_role(role_arn)
        except Exception as e:
            logger.warning(f"STS AssumeRole失败，回退到主账号凭证: {str(e)}")

    # 开发环境回退：直接使用主账号凭证
    logger.warning("使用主账号凭证（仅限开发环境，生产环境请配置STS）")
    return _direct_credentials()


def _assume_role(role_arn: str) -> Dict:
    """通过STS AssumeRole获取临时凭证"""
    global _cached_credentials, _cache_expiration

    import alibabacloud_sts20150401.client as sts_client
    import alibabacloud_tea_openapi.models as open_api_models
    import alibabacloud_sts20150401.models as sts_models

    config = open_api_models.Config(
        access_key_id=os.getenv('OSS_STS_ACCESS_KEY_ID', os.getenv('OSS_ACCESS_KEY_ID')),
        access_key_secret=os.getenv('OSS_STS_ACCESS_KEY_SECRET', os.getenv('OSS_ACCESS_KEY_SECRET')),
        endpoint='sts.aliyuncs.com'
    )

    client = sts_client.Client(config)

    policy = {
        "Version": "1",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["oss:PutObject"],
            "Resource": [
                f"acs:oss:*:*:{os.getenv('OSS_BUCKET_NAME')}/*"
            ]
        }]
    }

    request = sts_models.AssumeRoleRequest(
        role_arn=role_arn,
        role_session_name=f'oss-upload-{int(time.time())}',
        duration_seconds=3600,
        policy=json.dumps(policy)
    )

    response = client.assume_role(request)
    credentials = response.body.credentials

    bucket = os.getenv('OSS_BUCKET_NAME')
    endpoint = os.getenv('OSS_ENDPOINT', 'oss-cn-shanghai.aliyuncs.com')
    endpoint_clean = endpoint.replace('https://', '').replace('http://', '')
    parts = endpoint_clean.split('.')
    region = parts[0]  # 保留完整格式如 'oss-cn-shanghai'，ali-oss SDK 需要此格式

    result = {
        'access_key_id': credentials.access_key_id,
        'access_key_secret': credentials.access_key_secret,
        'security_token': credentials.security_token,
        'expiration': credentials.expiration,
        'region': region,
        'bucket': bucket,
        'endpoint': endpoint_clean
    }

    _cached_credentials = result
    from datetime import datetime, timezone
    try:
        dt = datetime.fromisoformat(credentials.expiration.replace('Z', '+00:00'))
        _cache_expiration = dt.timestamp()
    except Exception:
        _cache_expiration = time.time() + 3500

    return result


def _direct_credentials() -> Dict:
    """开发环境：直接返回主账号凭证（不安全，仅限开发测试）"""
    global _cached_credentials, _cache_expiration

    bucket = os.getenv('OSS_BUCKET_NAME')
    endpoint = os.getenv('OSS_ENDPOINT', 'oss-cn-shanghai.aliyuncs.com')
    endpoint_clean = endpoint.replace('https://', '').replace('http://', '')
    parts = endpoint_clean.split('.')
    region = parts[0]  # 保留完整格式如 'oss-cn-shanghai'，ali-oss SDK 需要此格式

    # 1小时后过期（模拟）
    from datetime import datetime, timezone, timedelta
    expiration = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    result = {
        'access_key_id': os.getenv('OSS_ACCESS_KEY_ID'),
        'access_key_secret': os.getenv('OSS_ACCESS_KEY_SECRET'),
        'security_token': '',
        'expiration': expiration,
        'region': region,
        'bucket': bucket,
        'endpoint': endpoint_clean
    }

    _cached_credentials = result
    _cache_expiration = time.time() + 3500

    return result
