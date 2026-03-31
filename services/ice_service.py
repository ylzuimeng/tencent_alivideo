"""
阿里云ICE（智能视频制作）服务集成模块

参考：example/subtitle.py
"""
import json
import os
import logging
from typing import Dict, Optional, Any
from datetime import datetime

from alibabacloud_ice20201109.client import Client as ICE20201109Client
from alibabacloud_ice20201109 import models as ice20201109_models
from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_tea_openapi.models import Config

logger = logging.getLogger(__name__)


class ICEClient:
    """阿里云ICE客户端封装类"""

    def __init__(self, region: str = 'cn-shanghai'):
        """
        初始化ICE客户端

        Args:
            region: 区域，默认 cn-shanghai
        """
        self.region = region
        self.client = self._create_client()

    def _create_client(self) -> ICE20201109Client:
        """创建ICE客户端"""
        try:
            # 使用默认凭证初始化
            cred = CredClient()
            config = Config(credential=cred)
            config.endpoint = f'ice.{self.region}.aliyuncs.com'
            return ICE20201109Client(config)
        except Exception as e:
            logger.error(f"创建ICE客户端失败: {str(e)}")
            raise

    def create_timeline_from_taskstyle(self, task_style, main_video_url: str) -> str:
        """
        根据TaskStyle配置生成Timeline JSON

        Args:
            task_style: TaskStyle模型实例
            main_video_url: 主视频URL

        Returns:
            Timeline JSON字符串
        """
        clips = []

        # 1. 添加片头视频
        if task_style.open_oss_url:
            clips.append({
                "MediaURL": task_style.open_oss_url,
                "Duration": 3
            })

        # 2. 添加主视频（主轨道）
        clips.append({
            "MediaURL": main_video_url,
            "MainTrack": True
        })

        # 3. 添加片尾视频
        if task_style.close_oss_url:
            clips.append({
                "MediaURL": task_style.close_oss_url,
                "Duration": 3
            })

        # 构建Timeline JSON
        timeline = {
            "VideoTracks": [{
                "VideoTrackClips": clips
            }]
        }

        # 添加背景图层（如果配置了）
        if task_style.title_picture_oss_url_1:
            # 在视频轨道上叠加背景图
            bg_clip = {
                "Type": "Image",
                "MediaURL": task_style.title_picture_oss_url_1,
                "AdaptMode": "Cover",
                "Width": 1,
                "Height": 1,
                "TimelineIn": 0,
                "TimelineOut": 3  # 显示在片头上
            }
            # 如果还没有背景轨道，创建一个
            if "SubtitleTracks" not in timeline:
                timeline["SubtitleTracks"] = []
            timeline["SubtitleTracks"].append({
                "SubtitleTrackClips": [bg_clip]
            })

        timeline_json = json.dumps(timeline, ensure_ascii=False)
        logger.debug(f"生成的Timeline: {timeline_json}")
        return timeline_json

    def submit_editing_job(self, timeline: str, output_url: str) -> Optional[Dict]:
        """
        提交剪辑作业

        Args:
            timeline: Timeline JSON字符串
            output_url: 输出文件OSS URL

        Returns:
            作业信息字典，包含job_id和project_id
        """
        try:
            # 创建剪辑工程请求
            request = ice20201109_models.CreateEditingProjectRequest()
            request.title = f"VideoProcessing_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            request.description = "自动生成的视频处理工程"
            request.timeline = timeline

            # 创建工程
            create_response = self.client.create_editing_project(request)
            logger.info(f"创建剪辑工程成功: {create_response.body.request_id}")

            project_id = create_response.body.project

            # 提交剪辑作业
            submit_request = ice20201109_models.SubmitMediaProducingJobRequest()
            submit_request.project_id = project_id
            submit_request.timeline = timeline
            submit_request.output_media_config = json.dumps({
                "mediaURL": output_url,
                "Width": 1280,
                "Height": 720
            }, ensure_ascii=False)

            submit_response = self.client.submit_media_producing_job(submit_request)
            logger.info(f"提交剪辑作业成功: {submit_response.body.job_id}")

            return {
                'project_id': project_id,
                'job_id': submit_response.body.job_id,
                'request_id': submit_response.body.request_id
            }

        except Exception as e:
            logger.error(f"提交剪辑作业失败: {str(e)}")
            raise

    def query_job_status(self, job_id: str) -> Optional[Dict]:
        """
        查询作业状态

        Args:
            job_id: 作业ID

        Returns:
            作业状态信息
        """
        try:
            # 这里需要调用查询作业状态的API
            # 注意：阿里云ICE SDK可能需要使用不同的API来查询状态
            # 具体API参考官方文档

            # 简化版本：通过查询工程信息来获取状态
            request = ice20201109_models.GetEditingProjectRequest()
            request.project_id = job_id  # 如果job_id是project_id

            response = self.client.get_editing_project(request)

            # 解析状态
            project = response.body.project
            status = self._map_status(project.get('status', 'Unknown'))

            return {
                'status': status,
                'progress': self._parse_progress(project),
                'output_url': project.get('output_media_config', {}).get('mediaURL')
            }

        except Exception as e:
            logger.error(f"查询作业状态失败: {str(e)}")
            return None

    def _map_status(self, ice_status: str) -> str:
        """映射ICE状态到内部状态"""
        status_map = {
            'Created': 'pending',
            'Queued': 'pending',
            'Processing': 'processing',
            'Finished': 'completed',
            'Failed': 'failed',
            'Canceled': 'failed'
        }
        return status_map.get(ice_status, 'pending')

    def _parse_progress(self, project: Dict) -> int:
        """解析进度"""
        status = project.get('status', 'Unknown')
        progress_map = {
            'Created': 0,
            'Queued': 10,
            'Processing': 50,
            'Finished': 100,
            'Failed': 0,
            'Canceled': 0
        }
        return progress_map.get(status, 0)


def create_ice_client() -> ICEClient:
    """
    创建ICE客户端实例的工厂函数

    Returns:
        ICEClient实例
    """
    region = os.getenv('ICE_REGION', 'cn-shanghai')
    return ICEClient(region=region)
