import logging
from flask import Blueprint, request, jsonify
from models import db, VideoTemplate
from utils.time_helpers import serialize_datetime

logger = logging.getLogger(__name__)

template_bp = Blueprint('template_api', __name__)


def _create_temp_template_from_simple(data: dict) -> VideoTemplate:
    """创建临时 VideoTemplate 用于转换（不持久化到数据库）"""
    return VideoTemplate(
        name=data.get('name', 'Temp'),
        header_video_url=data.get('header_video_url'),
        footer_video_url=data.get('footer_video_url'),
        enable_subtitle=data.get('enable_subtitle', False),
        subtitle_position=data.get('subtitle_position', 'bottom'),
        subtitle_extract_audio=data.get('subtitle_extract_audio', True),
        text_overlay_config=data.get('text_overlay_config'),
        is_advanced=False
    )


def _create_temp_template_from_advanced(timeline_json: str) -> VideoTemplate:
    return VideoTemplate(
        name='Temp',
        timeline_json=timeline_json,
        is_advanced=True
    )


@template_bp.route('/api/video_templates', methods=['POST'])
def create_video_template():
    """创建视频模板（支持简单模式和高级模式）"""
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'success': False, 'message': '缺少必填字段: name'}), 400

        is_advanced = data.get('is_advanced', False)

        if is_advanced:
            if not data.get('timeline_json'):
                return jsonify({'success': False, 'message': '高级模板必须提供 timeline_json'}), 400

            from services.json_validator import validate_timeline_json
            is_valid, error_msg = validate_timeline_json(data.get('timeline_json'))
            if not is_valid:
                return jsonify({'success': False, 'message': f'Timeline JSON验证失败: {error_msg}'}), 400
        else:
            if data.get('text_overlay_config'):
                from services.json_validator import validate_text_overlay_config
                is_valid, error_msg = validate_text_overlay_config(data['text_overlay_config'])
                if not is_valid:
                    return jsonify({'success': False, 'message': f'文字叠加配置验证失败: {error_msg}'}), 400

        template = VideoTemplate(
            name=data.get('name'),
            is_advanced=is_advanced,
            category=data.get('category'),
            header_video_url=data.get('header_video_url'),
            footer_video_url=data.get('footer_video_url'),
            enable_subtitle=data.get('enable_subtitle', False),
            subtitle_position=data.get('subtitle_position', 'bottom'),
            subtitle_extract_audio=data.get('subtitle_extract_audio', True),
            text_overlay_config=data.get('text_overlay_config'),
            timeline_json=data.get('timeline_json'),
            output_media_config=data.get('output_media_config'),
            editing_produce_config=data.get('editing_produce_config'),
            formatter_type=data.get('formatter_type'),
            thumbnail_url=data.get('thumbnail_url'),
            description=data.get('description', '')
        )

        db.session.add(template)
        db.session.commit()

        return jsonify({'success': True, 'message': '模板创建成功', 'template_id': template.id})

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建视频模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500


@template_bp.route('/api/video_templates', methods=['GET'])
def get_video_templates():
    try:
        templates = VideoTemplate.query.order_by(VideoTemplate.created_at.desc()).all()
        return jsonify({
            'success': True,
            'templates': [
                {
                    'id': t.id, 'name': t.name,
                    'header_video_url': t.header_video_url,
                    'footer_video_url': t.footer_video_url,
                    'enable_subtitle': t.enable_subtitle,
                    'subtitle_position': t.subtitle_position,
                    'subtitle_extract_audio': t.subtitle_extract_audio,
                    'is_advanced': t.is_advanced,
                    'category': t.category,
                    'description': t.description,
                    'created_at': serialize_datetime(t.created_at, to_beijing=True)
                }
                for t in templates
            ]
        })

    except Exception as e:
        logger.error(f"获取视频模板列表失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取列表失败: {str(e)}'}), 500


@template_bp.route('/api/video_templates/<int:template_id>', methods=['GET'])
def get_video_template(template_id):
    try:
        template = VideoTemplate.query.get_or_404(template_id)
        template_data = {
            'id': template.id, 'name': template.name,
            'header_video_url': template.header_video_url,
            'footer_video_url': template.footer_video_url,
            'enable_subtitle': template.enable_subtitle,
            'subtitle_position': template.subtitle_position,
            'subtitle_extract_audio': template.subtitle_extract_audio,
            'text_overlay_config': template.text_overlay_config,
            'timeline_json': template.timeline_json,
            'output_media_config': template.output_media_config,
            'editing_produce_config': template.editing_produce_config,
            'formatter_type': template.formatter_type,
            'category': template.category,
            'is_advanced': template.is_advanced,
            'thumbnail_url': template.thumbnail_url,
            'description': template.description,
            'created_at': template.created_at.isoformat() if template.created_at else None,
            'updated_at': template.updated_at.isoformat() if template.updated_at else None
        }
        return jsonify({'success': True, 'template': template_data})

    except Exception as e:
        logger.error(f"获取视频模板详情失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'}), 500


@template_bp.route('/api/video_templates/<int:template_id>', methods=['PUT'])
def update_video_template(template_id):
    try:
        template = VideoTemplate.query.get_or_404(template_id)
        data = request.get_json()

        if data.get('timeline_json'):
            from services.json_validator import validate_timeline_json
            is_valid, error_msg = validate_timeline_json(data['timeline_json'])
            if not is_valid:
                return jsonify({'success': False, 'message': f'Timeline JSON验证失败: {error_msg}'}), 400

        if data.get('text_overlay_config'):
            from services.json_validator import validate_text_overlay_config
            is_valid, error_msg = validate_text_overlay_config(data['text_overlay_config'])
            if not is_valid:
                return jsonify({'success': False, 'message': f'文字叠加配置验证失败: {error_msg}'}), 400

        # 更新字段
        updatable_fields = [
            'name', 'description', 'category', 'is_advanced',
            'header_video_url', 'footer_video_url', 'enable_subtitle',
            'subtitle_position', 'subtitle_extract_audio', 'text_overlay_config',
            'timeline_json', 'output_media_config', 'editing_produce_config',
            'formatter_type', 'thumbnail_url'
        ]
        for field in updatable_fields:
            if field in data:
                setattr(template, field, data[field])

        db.session.commit()
        return jsonify({'success': True, 'message': '更新成功'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新视频模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@template_bp.route('/api/video_templates/<int:template_id>', methods=['DELETE'])
def delete_video_template(template_id):
    try:
        template = VideoTemplate.query.get_or_404(template_id)

        if template.processing_tasks.count() > 0:
            return jsonify({'success': False, 'message': '该模板已关联处理任务，无法删除'}), 400

        db.session.delete(template)
        db.session.commit()
        return jsonify({'success': True, 'message': '删除成功'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除视频模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@template_bp.route('/api/video_templates/validate-timeline', methods=['POST'])
def validate_timeline():
    """验证Timeline JSON"""
    try:
        data = request.get_json()
        from services.json_validator import validate_timeline_json
        is_valid, error_msg = validate_timeline_json(data.get('timeline_json', ''))
        return jsonify({'success': is_valid, 'message': error_msg})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@template_bp.route('/api/video_templates/convert-demo', methods=['POST'])
def convert_template_demo():
    """在简单模式和高级模式之间转换模板"""
    try:
        req_data = request.get_json()
        if not req_data.get('mode'):
            return jsonify({'success': False, 'message': '缺少mode参数'}), 400

        mode = req_data['mode']

        if mode == 'simple-to-advanced':
            if not req_data.get('data'):
                return jsonify({'success': False, 'message': '缺少data参数'}), 400
            simple_data = req_data['data']
            if not simple_data.get('name'):
                return jsonify({'success': False, 'message': '缺少name字段'}), 400

            temp_template = _create_temp_template_from_simple(simple_data)
            from services.template_converter import TemplateConverter
            result = TemplateConverter.simple_to_advanced(temp_template)

            from services.json_validator import validate_timeline_json
            is_valid, error = validate_timeline_json(result['timeline_json'])
            if not is_valid:
                return jsonify({'success': False, 'message': f'生成Timeline验证失败: {error}'}), 400

            return jsonify({
                'success': True,
                'timeline_json': result['timeline_json'],
                'output_media_config': result['output_media_config'],
                'auto_generated': result['auto_generated']
            })

        elif mode == 'advanced-to-simple':
            if not req_data.get('timeline_json'):
                return jsonify({'success': False, 'message': '缺少timeline_json参数'}), 400

            from services.json_validator import validate_timeline_json
            is_valid, error = validate_timeline_json(req_data['timeline_json'])
            if not is_valid:
                return jsonify({'success': False, 'message': f'Timeline JSON验证失败: {error}'}), 400

            temp_template = _create_temp_template_from_advanced(req_data['timeline_json'])
            from services.template_converter import TemplateConverter
            result = TemplateConverter.advanced_to_simple(temp_template)

            return jsonify({'success': True, 'data': result})

        else:
            return jsonify({'success': False, 'message': f'无效的mode: {mode}'}), 400

    except Exception as e:
        logger.error(f"模板转换失败: {str(e)}")
        return jsonify({'success': False, 'message': f'转换失败: {str(e)}'}), 500
