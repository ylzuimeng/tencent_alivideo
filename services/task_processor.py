"""
任务处理器模块

负责异步处理视频任务，包括：
- 任务创建
- 提交到阿里云ICE
- 轮询作业状态
- 更新任务进度
"""
import os
import json
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional, Dict, List

from flask import current_app
from sqlalchemy.orm import joinedload
from models import db, ProcessingTask, File, TaskStyle, DoctorInfo, VideoTemplate
from services.ice_service import ICEClient

logger = logging.getLogger(__name__)


class TaskProcessor:
    """任务处理器"""

    def __init__(self, max_workers: int = 5):
        """
        初始化任务处理器

        Args:
            max_workers: 最大并发工作线程数
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = False
        self.poll_thread = None
        self._app_context = None

    def get_app_context(self):
        """获取Flask应用上下文"""
        if self._app_context is None or not self._app_context.push():
            from app import app
            self._app_context = app.app_context()
        return self._app_context

    def create_task(
        self,
        task_name: str,
        source_file_id: int,
        task_style_id: Optional[int] = None,
        doctor_info_id: Optional[int] = None,
        video_template_id: Optional[int] = None,
        use_advanced_timeline: bool = False
    ) -> ProcessingTask:
        """
        创建处理任务

        Args:
            task_name: 任务名称
            source_file_id: 源视频文件ID
            task_style_id: TaskStyle模板ID（可选，兼容旧版）
            doctor_info_id: 医生信息ID（可选）
            video_template_id: 视频模板ID（可选）
            use_advanced_timeline: 是否使用高级Timeline（占位符）

        Returns:
            ProcessingTask实例
        """
        try:
            task = ProcessingTask(
                task_name=task_name,
                source_file_id=source_file_id,
                task_style_id=task_style_id,
                doctor_info_id=doctor_info_id,
                video_template_id=video_template_id,
                use_advanced_timeline=use_advanced_timeline,
                status='pending'
            )
            db.session.add(task)
            db.session.commit()

            logger.info(f"创建任务成功: {task_name} (ID: {task.id})")

            # 异步提交ICE作业（添加异常处理）
            future = self.executor.submit(self._process_task, task.id)

            # 添加异常回调
            def log_exception(future):
                try:
                    future.result(timeout=300)  # 5分钟超时
                except Exception as e:
                    logger.error(f"任务{task.id}处理失败: {str(e)}", exc_info=True)
                    # 更新数据库状态为失败
                    try:
                        with self.get_app_context():
                            failed_task = ProcessingTask.query.get(task.id)
                            if failed_task and failed_task.status == 'pending':
                                failed_task.status = 'failed'
                                failed_task.error_message = str(e)[:500]
                                db.session.commit()
                    except Exception as db_error:
                        logger.error(f"更新任务失败状态时出错: {db_error}")

            # 使用单独的线程来监控Future
            import threading
            def monitor_future():
                log_exception(future)

            monitor_thread = threading.Thread(target=monitor_future, daemon=True)
            monitor_thread.start()

            return task

        except Exception as e:
            db.session.rollback()
            logger.error(f"创建任务失败: {str(e)}")
            raise

    def _process_task(self, task_id: int):
        """
        处理任务的核心逻辑（在独立线程中执行）

        Args:
            task_id: 任务ID
        """
        # 关键修复：在新线程中创建应用上下文
        with self.get_app_context():
            task = ProcessingTask.query.get(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return

            try:
                # 更新状态为处理中
                task.status = 'processing'
                task.progress = 10
                db.session.commit()

                # 获取源文件
                source_file = File.query.get(task.source_file_id)
                if not source_file:
                    raise Exception(f"源文件不存在: {task.source_file_id}")

                # 构建Timeline
                ice_client = ICEClient()
                timeline = self._build_timeline(task, source_file.oss_url)

                # 生成输出URL
                output_url = self._generate_output_url(task)

                # 提交ICE作业
                logger.info(f"提交ICE作业: 任务ID={task_id}")
                job_info = ice_client.submit_editing_job(timeline, output_url)

                # 更新任务信息
                task.ice_job_id = job_info['job_id']
                task.ice_project_id = job_info['project_id']
                task.progress = 20
                db.session.commit()

                # 轮询作业状态
                self._poll_job_status(task)

            except Exception as e:
                logger.error(f"处理任务失败: {str(e)}")
                task.status = 'failed'
                task.error_message = str(e)
                db.session.commit()

    def _build_timeline(self, task: ProcessingTask, main_video_url: str) -> str:
        """
        构建Timeline JSON

        优先级：
        1. VideoTemplate with is_advanced=True（新系统，支持占位符）
        2. VideoTemplate with is_advanced=False（兼容旧版）
        3. TaskStyle（旧版兼容）

        Args:
            task: ProcessingTask实例
            main_video_url: 主视频URL

        Returns:
            Timeline JSON字符串
        """
        ice_client = ICEClient()

        # 1. 新系统：高级VideoTemplate（支持占位符）
        if task.video_template_id and task.use_advanced_timeline:
            video_template = VideoTemplate.query.get(task.video_template_id)
            if not video_template:
                raise Exception(f"VideoTemplate不存在: {task.video_template_id}")

            if not video_template.is_advanced:
                raise Exception(f"VideoTemplate '{video_template.name}' 不是高级模板（is_advanced=False）")

            # 获取医生信息
            doctor_info = None
            if task.doctor_info_id:
                doctor_info = DoctorInfo.query.get(task.doctor_info_id)

            # 使用高级模板生成Timeline（支持占位符）
            return ice_client.create_timeline_from_advanced_template(video_template, main_video_url, doctor_info)

        # 2. 兼容旧版：普通VideoTemplate
        elif task.video_template_id:
            video_template = VideoTemplate.query.get(task.video_template_id)
            if not video_template:
                raise Exception(f"VideoTemplate不存在: {task.video_template_id}")

            # 获取医生信息
            doctor_info = None
            if task.doctor_info_id:
                doctor_info = DoctorInfo.query.get(task.doctor_info_id)

            # 使用增强的Timeline生成（支持文字叠加）
            return ice_client.create_timeline_with_overlay(video_template, main_video_url, doctor_info)

        # 3. 兼容旧版：TaskStyle
        elif task.task_style_id:
            task_style = TaskStyle.query.get(task.task_style_id)
            if not task_style:
                raise Exception(f"TaskStyle不存在: {task.task_style_id}")

            return ice_client.create_timeline_from_taskstyle(task_style, main_video_url)

        # 4. 不使用模板，直接使用主视频
        else:
            return json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [{
                        "MediaURL": main_video_url,
                        "MainTrack": True
                    }]
                }]
            })

    def _generate_output_url(self, task: ProcessingTask) -> str:
        """
        生成输出文件的OSS URL

        Args:
            task: ProcessingTask实例

        Returns:
            输出文件OSS URL
        """
        bucket = os.getenv('OSS_BUCKET_NAME')
        endpoint = os.getenv('OSS_ENDPOINT', 'oss-cn-shanghai.aliyuncs.com')

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"processed_{task.id}_{timestamp}.mp4"

        return f'https://{bucket}.{endpoint}/processed_videos/{filename}'

    def _poll_job_status(self, task: ProcessingTask):
        """
        轮询作业状态

        Args:
            task: ProcessingTask实例
        """
        ice_client = ICEClient()
        max_attempts = 120  # 最多轮询120次（10分钟）
        attempt = 0

        while attempt < max_attempts:
            try:
                # 查询作业状态
                status_info = ice_client.query_job_status(task.ice_job_id)

                if not status_info:
                    logger.warning(f"查询作业状态失败: {task.ice_job_id}")
                    attempt += 1
                    time.sleep(5)
                    continue

                # 更新状态和进度
                task.status = status_info['status']
                task.progress = status_info['progress']
                db.session.commit()

                logger.info(f"任务进度更新: {task.task_name} - {task.progress}%")

                # 检查是否完成
                if task.status == 'completed':
                    task.output_oss_url = status_info.get('output_url', '')
                    task.completed_at = datetime.now()
                    db.session.commit()
                    logger.info(f"任务完成: {task.task_name}")
                    break

                elif task.status == 'failed':
                    logger.error(f"任务失败: {task.task_name}")
                    break

                # 继续轮询
                attempt += 1
                time.sleep(5)  # 每5秒查询一次

            except Exception as e:
                logger.error(f"轮询作业状态异常: {str(e)}")
                attempt += 1
                time.sleep(5)

        if attempt >= max_attempts:
            logger.warning(f"任务轮询超时: {task.task_name}")
            task.status = 'failed'
            task.error_message = "处理超时"
            db.session.commit()

    def get_task_status(self, task_id: int) -> Optional[Dict]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态信息
        """
        task = ProcessingTask.query.get(task_id)
        if not task:
            return None

        return {
            'id': task.id,
            'task_name': task.task_name,
            'status': task.status,
            'progress': task.progress,
            'output_oss_url': task.output_oss_url,
            'error_message': task.error_message,
            'created_at': task.created_at.isoformat(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None
        }

    def get_all_tasks(self, limit: int = 50) -> list:
        """
        获取所有任务（优化版本，避免N+1查询）

        使用joinedload预加载所有关联数据，一次性完成查询。
        优化前：51次数据库查询（1次查询任务列表 + 50次查询每个任务详情）
        优化后：1次数据库查询（使用joinedload预加载关联数据）

        Args:
            limit: 最多返回数量

        Returns:
            任务列表
        """
        # 使用joinedload预加载所有关联数据，避免N+1查询
        tasks = ProcessingTask.query.options(
            joinedload(ProcessingTask.source_file),
            joinedload(ProcessingTask.task_style),
            joinedload(ProcessingTask.video_template),
            joinedload(ProcessingTask.doctor_info)
        ).order_by(
            ProcessingTask.created_at.desc()
        ).limit(limit).all()

        # 直接构建响应，无需额外查询
        return [{
            'id': task.id,
            'task_name': task.task_name,
            'status': task.status,
            'progress': task.progress,
            'output_oss_url': task.output_oss_url,
            'error_message': task.error_message,
            'created_at': task.created_at.isoformat(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            # 关联数据已预加载，可直接访问
            'source_file_name': task.source_file.filename if task.source_file else None,
            'template_name': task.video_template.name if task.video_template else
                          (task.task_style.name if task.task_style else None),
            'doctor_name': task.doctor_info.name if task.doctor_info else None
        } for task in tasks]


# 全局任务处理器实例
task_processor = TaskProcessor()
