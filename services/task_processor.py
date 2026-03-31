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
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional, Dict, List

from models import db, ProcessingTask, File, TaskStyle
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

    def create_task(
        self,
        task_name: str,
        source_file_id: int,
        task_style_id: Optional[int] = None
    ) -> ProcessingTask:
        """
        创建处理任务

        Args:
            task_name: 任务名称
            source_file_id: 源视频文件ID
            task_style_id: TaskStyle模板ID（可选）

        Returns:
            ProcessingTask实例
        """
        try:
            task = ProcessingTask(
                task_name=task_name,
                source_file_id=source_file_id,
                task_style_id=task_style_id,
                status='pending'
            )
            db.session.add(task)
            db.session.commit()

            logger.info(f"创建任务成功: {task_name} (ID: {task.id})")

            # 异步提交ICE作业
            self.executor.submit(self._process_task, task.id)

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

        Args:
            task: ProcessingTask实例
            main_video_url: 主视频URL

        Returns:
            Timeline JSON字符串
        """
        if task.task_style_id:
            # 使用TaskStyle模板
            task_style = TaskStyle.query.get(task.task_style_id)
            if not task_style:
                raise Exception(f"TaskStyle不存在: {task.task_style_id}")

            ice_client = ICEClient()
            return ice_client.create_timeline_from_taskstyle(task_style, main_video_url)
        else:
            # 不使用模板，直接使用主视频
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
            'output_url': task.output_oss_url,
            'error_message': task.error_message,
            'created_at': task.created_at.isoformat(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None
        }

    def get_all_tasks(self, limit: int = 50) -> list:
        """
        获取所有任务

        Args:
            limit: 最多返回数量

        Returns:
            任务列表
        """
        tasks = ProcessingTask.query.order_by(
            ProcessingTask.created_at.desc()
        ).limit(limit).all()

        return [self.get_task_status(task.id) for task in tasks]


# 全局任务处理器实例
task_processor = TaskProcessor()
