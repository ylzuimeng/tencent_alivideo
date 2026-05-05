import logging
from flask import Blueprint, request, jsonify
from models import db, File, VideoTemplate, ProcessingTask
from services.oss_service import OSSConfig, OSSClient

logger = logging.getLogger(__name__)

task_bp = Blueprint('task_api', __name__)


@task_bp.route('/api/tasks/create', methods=['POST'])
def create_task():
    """创建视频处理任务"""
    try:
        data = request.get_json()

        if not data.get('source_file_id'):
            return jsonify({'error': '缺少source_file_id参数'}), 400

        source_file = File.query.get(data['source_file_id'])
        if not source_file:
            return jsonify({'error': '源文件不存在'}), 404

        task_name = data.get('task_name', f"处理_{source_file.filename}")

        from services.task_processor import task_processor

        use_advanced_timeline = False
        if data.get('video_template_id'):
            template = VideoTemplate.query.get(data['video_template_id'])
            if template and template.is_advanced:
                use_advanced_timeline = True

        task = task_processor.create_task(
            task_name=task_name,
            source_file_id=data['source_file_id'],
            task_style_id=data.get('task_style_id'),
            doctor_info_id=data.get('doctor_info_id'),
            video_template_id=data.get('video_template_id'),
            use_advanced_timeline=use_advanced_timeline
        )

        return jsonify({
            'message': '任务创建成功',
            'task_id': task.id,
            'task_name': task.task_name,
            'status': task.status
        })

    except Exception as e:
        logger.error(f"创建任务失败: {str(e)}")
        return jsonify({'error': f'创建任务失败: {str(e)}'}), 500


@task_bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取任务列表"""
    try:
        from services.task_processor import task_processor
        tasks = task_processor.get_all_tasks(limit=50)
        return jsonify(tasks)

    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        return jsonify({'error': f'获取任务列表失败: {str(e)}'}), 500


@task_bp.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task_detail(task_id):
    """获取任务详情"""
    try:
        from services.task_processor import task_processor
        task = task_processor.get_task_status(task_id)
        if not task:
            return jsonify({'error': '任务不存在'}), 404
        return jsonify(task)

    except Exception as e:
        logger.error(f"获取任务详情失败: {str(e)}")
        return jsonify({'error': f'获取任务详情失败: {str(e)}'}), 500


@task_bp.route('/api/tasks/<int:task_id>/progress', methods=['GET'])
def get_task_progress(task_id):
    """获取任务进度"""
    try:
        from services.task_processor import task_processor
        task = task_processor.get_task_status(task_id)
        if not task:
            return jsonify({'error': '任务不存在'}), 404

        return jsonify({
            'task_id': task['id'],
            'status': task['status'],
            'progress': task['progress'],
            'error_message': task['error_message']
        })

    except Exception as e:
        logger.error(f"获取任务进度失败: {str(e)}")
        return jsonify({'error': f'获取任务进度失败: {str(e)}'}), 500


@task_bp.route('/api/tasks/<int:task_id>/download', methods=['GET'])
def download_task_output(task_id):
    """下载成品视频"""
    try:
        task = ProcessingTask.query.get_or_404(task_id)

        if task.status != 'completed':
            return jsonify({'error': f'任务未完成，当前状态: {task.status}'}), 400
        if not task.output_oss_url:
            return jsonify({'error': '成品视频URL不存在'}), 404

        return jsonify({
            'message': '获取下载链接成功',
            'download_url': task.output_oss_url,
            'task_name': task.task_name,
            'completed_at': task.completed_at.isoformat()
        })

    except Exception as e:
        logger.error(f"下载成品失败: {str(e)}")
        return jsonify({'error': f'下载成品失败: {str(e)}'}), 500


@task_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    try:
        task = ProcessingTask.query.get_or_404(task_id)

        if task.status == 'completed' and task.output_oss_url:
            try:
                oss_config = OSSConfig()
                oss_client = OSSClient(oss_config)
                filename = task.output_oss_url.split('/')[-1]
                oss_path = f"processed_videos/{filename}"
                oss_client.delete_file(oss_path)
                logger.info(f"已删除成品文件: {oss_path}")
            except Exception as e:
                logger.warning(f"删除OSS文件失败: {str(e)}")

        db.session.delete(task)
        db.session.commit()

        return jsonify({'message': '任务删除成功'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除任务失败: {str(e)}")
        return jsonify({'error': f'删除任务失败: {str(e)}'}), 500


@task_bp.route('/api/tasks/<int:task_id>/retry', methods=['POST'])
def retry_task(task_id):
    """重试失败的任务"""
    try:
        from services.task_processor import task_processor
        task = ProcessingTask.query.get_or_404(task_id)

        if task.status != 'failed':
            return jsonify({'error': '只能重试失败的任务'}), 400

        task.status = 'pending'
        task.progress = 0
        task.error_message = None
        db.session.commit()

        task_processor.executor.submit(task_processor._process_task, task.id)

        return jsonify({'message': '任务已重新提交处理'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"重试任务失败: {str(e)}")
        return jsonify({'error': f'重试失败: {str(e)}'}), 500
