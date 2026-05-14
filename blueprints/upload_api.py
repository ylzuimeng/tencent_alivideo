"""
前端直传OSS上传API

提供STS临时凭证、路径生成、上传完成回调等端点。
"""
import logging
from flask import Blueprint, request, jsonify
from models import db, File
from utils.file_handler import FileHandler
from services.oss_service import OSSConfig

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/api/upload/sts-token', methods=['GET'])
def get_sts_token():
    """返回STS临时凭证和OSS配置信息"""
    try:
        from services.sts_service import get_sts_credentials
        credentials = get_sts_credentials()
        return jsonify({'success': True, 'data': credentials})
    except Exception as e:
        logger.warning(f"获取STS凭证失败（将使用后端中转上传）: {str(e)}")
        return jsonify({'success': False, 'message': f'获取上传凭证失败: {str(e)}'}), 500


@upload_bp.route('/api/upload/generate-path', methods=['POST'])
def generate_path():
    """生成OSS存储路径（后端控制命名规则）"""
    try:
        data = request.get_json()
        if not data or not data.get('filename'):
            return jsonify({'success': False, 'message': '缺少filename参数'}), 400

        filename = data['filename']
        prefix = data.get('prefix', 'uploads')

        # 校验文件扩展名
        if not FileHandler.allowed_file(filename):
            return jsonify({'success': False, 'message': '不支持的文件格式'}), 400

        # 生成OSS路径
        oss_path = FileHandler.generate_oss_path(filename, prefix)
        oss_config = OSSConfig()
        oss_url = oss_config.get_file_url(oss_path)

        return jsonify({
            'success': True,
            'oss_path': oss_path,
            'oss_url': oss_url
        })

    except Exception as e:
        logger.error(f"生成上传路径失败: {str(e)}")
        return jsonify({'success': False, 'message': f'生成路径失败: {str(e)}'}), 500


@upload_bp.route('/api/upload/complete', methods=['POST'])
def upload_complete():
    """前端直传完成后，创建数据库记录"""
    try:
        data = request.get_json()
        if not data or not data.get('filename') or not data.get('oss_url'):
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400

        filename = data['filename']
        oss_url = data['oss_url']
        size = data.get('size', 0)

        # 验证oss_url属于当前bucket
        oss_config = OSSConfig()
        expected_prefix = f'https://{oss_config.bucket_name}.{oss_config.endpoint}/'
        if not oss_url.startswith(expected_prefix):
            return jsonify({'success': False, 'message': '无效的文件URL'}), 400

        # 幂等：检查是否已存在相同URL的记录
        existing = File.query.filter_by(oss_url=oss_url).first()
        if existing:
            return jsonify({
                'success': True,
                'file_id': existing.id,
                'message': '文件记录已存在'
            })

        # 创建数据库记录
        new_file = File(
            filename=filename,
            oss_url=oss_url,
            size=size
        )
        db.session.add(new_file)
        db.session.commit()

        logger.info(f"直传文件记录创建成功: {filename}, ID: {new_file.id}")
        return jsonify({
            'success': True,
            'file_id': new_file.id,
            'message': '文件记录创建成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建文件记录失败: {str(e)}")
        return jsonify({'success': False, 'message': f'创建记录失败: {str(e)}'}), 500
