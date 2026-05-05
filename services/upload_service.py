import logging
from services.oss_service import OSSConfig, OSSClient
from utils.time_helpers import utcnow
from utils.file_handler import FileHandler

logger = logging.getLogger(__name__)


def upload_to_oss(file, prefix, model_class, db):
    """通用文件上传逻辑

    Args:
        file: request.files 中的文件对象
        prefix: OSS 路径前缀 ('uploads' 或 'templates')
        model_class: 数据库模型类 (File 或 Template)
        db: SQLAlchemy db 实例

    Returns:
        tuple: (success: bool, data: dict, status_code: int)
    """
    oss_config = OSSConfig()
    if not oss_config.is_valid():
        return False, {'error': 'OSS配置不完整，请检查环境变量'}, 500

    # 生成 OSS 路径
    oss_path = FileHandler.generate_oss_path(file.filename, prefix)
    file_content = file.read()
    file_size = len(file_content)

    # 上传到 OSS
    oss_client = OSSClient(oss_config)
    if not oss_client.upload_file(file_content, oss_path):
        return False, {'error': '文件上传失败'}, 500

    file_url = oss_config.get_file_url(oss_path)
    logger.info(f"文件上传成功，URL: {file_url}")

    # 保存到数据库
    try:
        new_file = model_class(
            filename=file.filename,
            oss_url=file_url,
            size=file_size
        )
        db.session.add(new_file)
        db.session.commit()

        return True, {
            'message': '文件上传成功',
            'file_id': new_file.id,
            'file_url': file_url,
            'filename': file.filename,
            'task_id': utcnow().isoformat()
        }, 200
    except Exception as db_error:
        db.session.rollback()
        logger.error(f"数据库保存失败: {str(db_error)}")
        # 尝试回滚 OSS 删除
        try:
            oss_client.delete_file(oss_path)
            logger.info(f"已回滚删除OSS文件: {oss_path}")
        except Exception as rollback_error:
            logger.error(f"回滚删除OSS文件失败: {str(rollback_error)}")
        return False, {'error': '数据库保存失败'}, 500


def delete_from_oss(file_record, prefix, db):
    """通用文件删除逻辑

    Args:
        file_record: 数据库中的文件记录
        prefix: OSS 路径前缀 ('uploads', 'templates', 'processed_videos')
        db: SQLAlchemy db 实例

    Returns:
        tuple: (success: bool, data: dict, status_code: int)
    """
    oss_config = OSSConfig()
    oss_client = OSSClient(oss_config)

    filename = file_record.oss_url.split('/')[-1]
    oss_path = f"{prefix}/{filename}"

    logger.info(f"准备删除OSS文件: {oss_path}")
    delete_success = oss_client.delete_file(oss_path)

    if not delete_success:
        logger.warning(f"OSS文件删除失败或文件不存在: {oss_path}")

    db.session.delete(file_record)
    db.session.commit()

    logger.info(f"文件记录删除成功: {file_record.filename}")
    return True, {'message': '删除成功'}, 200
