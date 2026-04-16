"""
阿里云ICE（智能视频制作）服务集成模块

参考：example/subtitle.py
"""
import json
import os
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime
from utils.time_helpers import utcnow

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
            # 从环境变量读取凭证
            access_key_id = os.getenv('OSS_ACCESS_KEY_ID') or os.getenv('ACCESS_KEY_ID')
            access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET') or os.getenv('ACCESS_KEY_SECRET')

            if not access_key_id or not access_key_secret:
                raise ValueError("阿里云访问凭证未配置：请检查 OSS_ACCESS_KEY_ID 和 OSS_ACCESS_KEY_SECRET 环境变量")

            # 直接在Config中设置凭证
            config = Config(
                access_key_id=access_key_id,
                access_key_secret=access_key_secret,
                endpoint=f'ice.{self.region}.aliyuncs.com'
            )

            logger.info(f"创建ICE客户端成功，Region: {self.region}")
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

    def create_timeline_with_overlay(self, video_template, main_video_url: str, doctor_info) -> str:
        """
        创建支持文字叠加的Timeline

        Args:
            video_template: VideoTemplate模型实例
            main_video_url: 主视频URL
            doctor_info: DoctorInfo模型实例

        Returns:
            Timeline JSON字符串
        """
        clips = []
        subtitle_clips = []

        logger.info(f"创建增强Timeline - 模板: {video_template.name}")
        logger.info(f"  片头: {video_template.header_video_url}")
        logger.info(f"  片尾: {video_template.footer_video_url}")
        logger.info(f"  主视频: {main_video_url}")

        # 1. 添加片头视频
        header_duration = 0
        if video_template.header_video_url:
            clips.append({
                "MediaURL": video_template.header_video_url,
                "Duration": 3
            })
            header_duration = 3
            logger.info("✅ 已添加片头到Timeline")

        # 2. 添加主视频（主轨道）
        clips.append({
            "MediaURL": main_video_url,
            "MainTrack": True
        })
        logger.info("✅ 已添加主视频到Timeline")

        # 3. 添加片尾视频
        if video_template.footer_video_url:
            clips.append({
                "MediaURL": video_template.footer_video_url,
                "Duration": 3
            })
            logger.info("✅ 已添加片尾到Timeline")

        # 构建基础Timeline
        timeline = {
            "VideoTracks": [{
                "VideoTrackClips": clips
            }]
        }

        # 4. 添加医生信息文字叠加
        if doctor_info:
            overlay_clips = self._create_doctor_overlay_clips(doctor_info, header_duration)
            subtitle_clips.extend(overlay_clips)

        # 5. 添加字幕轨道（如果有配置）
        if subtitle_clips:
            timeline["SubtitleTracks"] = [{
                "SubtitleTrackClips": subtitle_clips
            }]

        timeline_json = json.dumps(timeline, ensure_ascii=False)
        logger.debug(f"生成的增强Timeline: {timeline_json}")
        return timeline_json

    def _create_doctor_overlay_clips(self, doctor_info, header_duration: int) -> List[Dict]:
        """
        创建医生信息文字叠加片段

        Args:
            doctor_info: 医生信息对象
            header_duration: 片头时长

        Returns:
            字幕片段列表
        """
        clips = []

        # 医生姓名 - 显示在片头上
        if doctor_info.name:
            clips.append({
                "Type": "Text",
                "Text": doctor_info.name,
                "FontId": "SimHei",
                "FontSize": 36,
                "FontColor": "#FFFFFF",
                "FontFace": {
                    "Bold": True
                },
                "X": 0.1,  # 左侧10%
                "Y": 0.1,  # 顶部10%
                "TimelineIn": 0,
                "TimelineOut": header_duration
            })

        # 医院科室职称 - 显示在姓名下方
        info_text = f"{doctor_info.hospital or ''}"
        if doctor_info.department:
            info_text += f" {doctor_info.department}"
        if doctor_info.title:
            info_text += f" {doctor_info.title}"

        if info_text.strip():
            clips.append({
                "Type": "Text",
                "Text": info_text,
                "FontId": "SimHei",
                "FontSize": 24,
                "FontColor": "#CCCCCC",
                "X": 0.1,
                "Y": 0.15,  # 姓名下方
                "TimelineIn": 0,
                "TimelineOut": header_duration
            })

        return clips

    def add_text_overlay(self, timeline_json: str, text_overlays: List[Dict]) -> str:
        """
        向Timeline添加自定义文字叠加

        Args:
            timeline_json: 原始Timeline JSON字符串
            text_overlays: 文字叠加配置列表
                每个配置包含: text, x, y, font_size, font_color, timeline_in, timeline_out

        Returns:
            更新后的Timeline JSON字符串
        """
        try:
            timeline = json.loads(timeline_json)

            # 创建字幕轨道（如果不存在）
            if "SubtitleTracks" not in timeline:
                timeline["SubtitleTracks"] = []

            # 添加文字叠加片段
            overlay_clips = []
            for overlay in text_overlays:
                clip = {
                    "Type": "Text",
                    "Text": overlay.get("text", ""),
                    "FontId": overlay.get("font_id", "SimHei"),
                    "FontSize": overlay.get("font_size", 24),
                    "FontColor": overlay.get("font_color", "#FFFFFF"),
                    "X": overlay.get("x", 0.1),
                    "Y": overlay.get("y", 0.1),
                    "TimelineIn": overlay.get("timeline_in", 0),
                    "TimelineOut": overlay.get("timeline_out", 5)
                }

                # 添加字体样式
                if overlay.get("bold"):
                    clip["FontFace"] = {"Bold": True}

                overlay_clips.append(clip)

            # 添加到字幕轨道
            if overlay_clips:
                timeline["SubtitleTracks"].append({
                    "SubtitleTrackClips": overlay_clips
                })

            return json.dumps(timeline, ensure_ascii=False)

        except Exception as e:
            logger.error(f"添加文字叠加失败: {str(e)}")
            raise

    def submit_subtitle_job(self, video_url: str, output_url: str) -> Optional[Dict]:
        """
        提交字幕生成作业（语音识别）

        Args:
            video_url: 视频URL
            output_url: 输出字幕文件URL

        Returns:
            作业信息
        """
        try:
            # 注意：这需要根据阿里云ICE的实际API进行调整
            # 这里提供一个框架示例

            request = ice20201109_models.SubmitMediaProducingJobRequest()

            # 构建Timeline用于字幕提取
            timeline = {
                "VideoTracks": [{
                    "VideoTrackClips": [{
                        "MediaURL": video_url
                    }]
                }]
            }

            request.timeline = json.dumps(timeline, ensure_ascii=False)
            request.output_media_config = json.dumps({
                "mediaURL": output_url,
                "SubtitleConfig": {
                    "ExtractSubtitle": True,
                    "Format": "SRT"
                }
            }, ensure_ascii=False)

            response = self.client.submit_media_producing_job(request)

            return {
                'job_id': response.body.job_id,
                'request_id': response.body.request_id
            }

        except Exception as e:
            logger.error(f"提交字幕生成作业失败: {str(e)}")
            return None

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
            request.title = f"VideoProcessing_{utcnow().strftime('%Y%m%d%H%M%S')}"
            request.description = "自动生成的视频处理工程"
            request.timeline = timeline

            # 创建工程
            create_response = self.client.create_editing_project(request)
            logger.info(f"创建剪辑工程成功: {create_response.body.request_id}")

            # 提取project ID字符串
            project_obj = create_response.body.project

            # project_obj 是一个特殊的对象，可以通过 to_map() 方法转换为字典
            # 或者直接访问属性
            try:
                # 方法1：尝试转换为字典
                if hasattr(project_obj, 'to_map'):
                    project_dict = project_obj.to_map()
                    project_id = project_dict.get('ProjectId')
                # 方法2：直接通过属性访问
                elif hasattr(project_obj, 'project_id'):
                    project_id = project_obj.project_id
                # 方法3：尝试字符串键访问
                else:
                    project_id = str(project_obj).get('ProjectId', project_obj)
            except Exception as e:
                # 如果都失败，尝试直接转换
                logger.warning(f"Project ID提取异常: {e}")
                # 直接使用字符串表示
                project_id = str(project_obj)
                # 从字符串中提取 ProjectId（如果包含）
                if 'ProjectId' in str(project_obj):
                    import re
                    match = re.search(r"ProjectId':\s*'([^']+)'", str(project_obj))
                    if match:
                        project_id = match.group(1)

            logger.info(f"提取的 Project ID: {project_id}")

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

            # 🔍 记录提交的完整信息用于调试
            logger.info(f"🔍 提交剪辑作业成功 - Job ID: {submit_response.body.job_id}")
            logger.info(f"🔍 提交的 Timeline: {timeline}")
            logger.info(f"🔍 提交的 OutputMediaConfig: {submit_request.output_media_config}")
            logger.info(f"🔍 完整响应: {submit_response}")

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
            # 使用正确的API查询作业状态
            request = ice20201109_models.GetMediaProducingJobRequest()
            request.job_id = job_id

            response = self.client.get_media_producing_job(request)

            # 🔍 记录完整响应用于调试
            logger.info(f"🔍 阿里云 ICE 完整响应: {response}")

            # 解析状态 - response.body.media_producing_job 是一个对象
            job_obj = response.body.media_producing_job

            # 使用 to_map() 方法转换为字典
            job_dict = job_obj.to_map() if hasattr(job_obj, 'to_map') else dict(job_obj)
            status_code = job_dict.get('Status')

            # 映射状态码到内部状态
            status_map = {
                'Created': 'pending',
                'Queued': 'pending',
                'Processing': 'processing',
                'Success': 'completed',
                'Finished': 'completed',
                'Failed': 'failed',
                'Canceled': 'failed'
            }
            status = status_map.get(status_code, 'pending')

            # 计算进度
            progress_map = {
                'Created': 0,
                'Queued': 10,
                'Processing': 50,
                'Success': 100,
                'Finished': 100,
                'Failed': 0,
                'Canceled': 0
            }
            progress = progress_map.get(status_code, 0)

            return {
                'status': status,
                'progress': progress,
                'output_url': job_dict.get('MediaURL')
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

    def create_timeline_from_advanced_template(self, video_template, main_video_url: str, doctor_info) -> str:
        """
        从高级VideoTemplate创建格式化Timeline（支持占位符）

        Args:
            video_template: VideoTemplate实例（is_advanced=True）
            main_video_url: 主视频URL
            doctor_info: DoctorInfo实例（可选）

        Returns:
            格式化后的Timeline JSON字符串
        """
        from services.timeline_formatter import DefaultTimelineFormatter

        if not video_template.timeline_json:
            raise ValueError(f"VideoTemplate '{video_template.name}' 没有配置 timeline_json")

        # 准备占位符数据
        data = {'main_video_url': main_video_url}

        if doctor_info:
            data.update({
                'hospital': doctor_info.hospital or '',
                'department': doctor_info.department or '',
                'name': doctor_info.name or '',
                'title': doctor_info.title or '',
            })

        # 使用任务名称作为视频标题（如果没有提供）
        data['video_title'] = getattr(video_template, 'name', '视频标题')

        # 格式化Timeline
        formatter = DefaultTimelineFormatter()
        formatted_timeline = formatter.format(video_template.timeline_json, data)

        logger.info(f"使用高级模板 '{video_template.name}' 生成Timeline")
        return formatted_timeline


def create_ice_client() -> ICEClient:
    """
    创建ICE客户端实例的工厂函数

    Returns:
        ICEClient实例
    """
    region = os.getenv('ICE_REGION', 'cn-shanghai')
    return ICEClient(region=region)
