import logging
from flask import Blueprint, request, jsonify, redirect, url_for
from models import db, TaskStyle
from utils.time_helpers import serialize_datetime

logger = logging.getLogger(__name__)

legacy_bp = Blueprint('legacy_api', __name__)


@legacy_bp.route('/api/save_taskstyle', methods=['POST'])
def save_taskstyle():
    try:
        data = request.get_json()
        logger.debug(f"接收到的数据: {data}")

        if not data.get('name'):
            return jsonify({'error': '模板名称不能为空'}), 400

        new_taskstyle = TaskStyle(
            name=data.get('name'),
            open_oss_url=data.get('header_file'),
            close_oss_url=data.get('footer_file'),
            title_picture_oss_url_1=data.get('background_file'),
            title_picture_oss_url_2=data.get('background2_file'),
            change_material_oss_url=data.get('transition_file'),
            description=data.get('description', f"模板：{data.get('name')}")
        )

        db.session.add(new_taskstyle)
        db.session.commit()

        return jsonify({'message': '模板保存成功', 'id': new_taskstyle.id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@legacy_bp.route('/api/taskstyles')
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
                'created_at': serialize_datetime(ts.created_at, to_beijing=True)
            })

        logger.info(f"返回TaskStyle列表，共{len(result)}个模板")
        return jsonify({'taskstyles': result})

    except Exception as e:
        logger.error(f"获取TaskStyle列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@legacy_bp.route('/api/delete_taskstyle/<int:taskstyle_id>', methods=['POST'])
def taskstyle_delete_file(taskstyle_id):
    taskstyle = TaskStyle.query.get_or_404(taskstyle_id)

    db.session.delete(taskstyle)
    db.session.commit()

    return redirect(url_for('pages.taskstyles'))
