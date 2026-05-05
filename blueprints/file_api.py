import logging
from flask import Blueprint, request, jsonify, redirect, url_for
from models import db, File, Template
from utils.file_handler import FileHandler
from utils.time_helpers import serialize_datetime

logger = logging.getLogger(__name__)

file_bp = Blueprint('file_api', __name__)


@file_bp.route('/api/files', methods=['GET'])
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


@file_bp.route('/api/upload/video', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400

        file = request.files['file']
        if file.filename == '' or not FileHandler.allowed_file(file.filename):
            return jsonify({'error': '没有选择文件或不支持的文件格式'}), 400

        from services.upload_service import upload_to_oss
        success, data, status_code = upload_to_oss(file, 'uploads', File, db)
        return jsonify(data), status_code

    except Exception as e:
        logger.error(f"上传文件异常: {str(e)}")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@file_bp.route('/api/upload/template', methods=['POST'])
def upload_template():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400

        file = request.files['file']
        if file.filename == '' or not FileHandler.allowed_file(file.filename):
            return jsonify({'error': '没有选择文件或不支持的文件格式'}), 400

        from services.upload_service import upload_to_oss
        success, data, status_code = upload_to_oss(file, 'templates', Template, db)
        return jsonify(data), status_code

    except Exception as e:
        logger.error(f"上传模板文件异常: {str(e)}")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@file_bp.route('/api/templates', methods=['GET'])
def get_templates():
    templates = Template.query.all()
    return jsonify([{
        'id': t.id,
        'filename': t.filename,
        'oss_url': t.oss_url,
        'upload_time': serialize_datetime(t.upload_time, to_beijing=True)
    } for t in templates])


@file_bp.route('/api/upload/templates/delete/<int:file_id>', methods=['POST'])
def template_delete_file(file_id):
    try:
        file = Template.query.get_or_404(file_id)

        from services.upload_service import delete_from_oss
        success, data, status_code = delete_from_oss(file, 'templates', db)

        if success:
            return redirect(url_for('pages.templates'))
        return jsonify(data), status_code

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除模板文件失败: {str(e)}")
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@file_bp.route('/api/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    try:
        file = File.query.get_or_404(file_id)

        from services.upload_service import delete_from_oss
        success, data, status_code = delete_from_oss(file, 'uploads', db)

        if success:
            return redirect(url_for('pages.files'))
        return jsonify(data), status_code

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除文件记录失败: {str(e)}")
        return jsonify({'error': f'删除失败: {str(e)}'}), 500
