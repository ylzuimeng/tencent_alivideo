"""
模板模式转换器

功能：
- 简单模式 → 高级模式：生成标准Timeline JSON
- 高级模式 → 简单模式：解析JSON填充表单字段
"""
import json
import logging
from typing import Dict, Any
from models import VideoTemplate

logger = logging.getLogger(__name__)


class TemplateConverter:
    """模板模式转换器"""

    @staticmethod
    def simple_to_advanced(template: VideoTemplate) -> Dict[str, Any]:
        """
        简单模式 → 高级模式
        生成标准Timeline JSON：片头 → 主视频 → 片尾

        Args:
            template: VideoTemplate实例（简单模式）

        Returns:
            dict: 包含timeline_json的字典
        """
        try:
            timeline = {
                "VideoTracks": [{
                    "VideoTrackClips": []
                }]
            }

            # 添加片头视频
            if template.header_video_url:
                timeline["VideoTracks"][0]["VideoTrackClips"].append({
                    "MediaURL": template.header_video_url,
                    "Duration": 3
                })

            # 添加主视频（占位符）
            timeline["VideoTracks"][0]["VideoTrackClips"].append({
                "MediaURL": "$main_video",
                "MainTrack": True
            })

            # 添加片尾视频
            if template.footer_video_url:
                timeline["VideoTracks"][0]["VideoTrackClips"].append({
                    "MediaURL": template.footer_video_url,
                    "Duration": 3
                })

            # 添加字幕配置（如果启用）
            if template.enable_subtitle:
                subtitle_config = {
                    "SubtitleTracks": [{
                        "SubtitleTrackClips": []
                    }]
                }

                # 根据字幕位置配置
                if template.subtitle_position:
                    position_map = {
                        'top': 'Top',
                        'bottom': 'Bottom',
                        'center': 'Center'
                    }
                    if template.subtitle_position in position_map:
                        subtitle_config["SubtitleTracks"][0]["SubtitleTrackClips"].append({
                            "Type": "Text",
                            "Text": "",
                            "Position": position_map[template.subtitle_position]
                        })

                timeline.update(subtitle_config)

            # 生成输出配置（默认）
            output_config = {
                "Width": 1280,
                "Height": 720
            }

            return {
                'timeline_json': json.dumps(timeline, ensure_ascii=False, indent=2),
                'output_media_config': json.dumps(output_config, ensure_ascii=False),
                'auto_generated': True
            }

        except Exception as e:
            logger.error(f"简单转高级模式失败: {str(e)}")
            raise ValueError(f"转换失败: {str(e)}")

    @staticmethod
    def advanced_to_simple(template: VideoTemplate) -> Dict[str, Any]:
        """
        高级模式 → 简单模式
        智能解析Timeline，提取片头片尾

        Args:
            template: VideoTemplate实例（高级模式）

        Returns:
            dict: 包含解析出的简单字段
        """
        try:
            if not template.timeline_json:
                return {
                    'warnings': ['Timeline JSON为空']
                }

            timeline = json.loads(template.timeline_json)
            warnings = []

            # 提取视频片段
            video_tracks = timeline.get("VideoTracks", [])
            if not video_tracks:
                return {
                    'warnings': ['Timeline中没有VideoTracks']
                }

            clips = video_tracks[0].get("VideoTrackClips", [])
            if not clips:
                return {
                    'warnings': ['VideoTracks中没有片段']
                }

            # 查找主视频位置
            main_track_indices = []
            for i, clip in enumerate(clips):
                if clip.get("MainTrack") or "$main_video" in clip.get("MediaURL", ""):
                    main_track_indices.append(i)

            if not main_track_indices:
                warnings.append('未找到主视频轨道($main_video)')
                return {
                    'header_video_url': None,
                    'footer_video_url': None,
                    'warnings': warnings
                }

            main_index = main_track_indices[0]
            header_url = None
            footer_url = None

            # 主视频之前的可能是片头
            if main_index > 0:
                prev_clip = clips[main_index - 1]
                if prev_clip.get("MediaURL") and not prev_clip.get("MainTrack"):
                    header_url = prev_clip["MediaURL"]

            # 主视频之后的可能是片尾
            if main_index < len(clips) - 1:
                next_clip = clips[main_index + 1]
                if next_clip.get("MediaURL") and not next_clip.get("MainTrack"):
                    footer_url = next_clip["MediaURL"]

            if header_url or footer_url:
                warnings.append('已自动识别片头片尾')

            # 提取字幕配置
            enable_subtitle = False
            subtitle_position = 'bottom'

            subtitle_tracks = timeline.get("SubtitleTracks", [])
            if subtitle_tracks:
                subtitle_clips = subtitle_tracks[0].get("SubtitleTrackClips", [])
                if subtitle_clips:
                    enable_subtitle = True
                    # 尝试获取位置
                    position = subtitle_clips[0].get("Position", "Bottom")
                    position_map = {
                        'Top': 'top',
                        'Bottom': 'bottom',
                        'Center': 'center'
                    }
                    subtitle_position = position_map.get(position, 'bottom')

            return {
                'header_video_url': header_url,
                'footer_video_url': footer_url,
                'enable_subtitle': enable_subtitle,
                'subtitle_position': subtitle_position,
                'warnings': warnings
            }

        except json.JSONDecodeError as e:
            logger.error(f"解析Timeline JSON失败: {str(e)}")
            return {
                'warnings': [f'JSON格式错误: {str(e)}']
            }
        except Exception as e:
            logger.error(f"高级转简单模式失败: {str(e)}")
            return {
                'warnings': [f'解析失败: {str(e)}']
            }

    @staticmethod
    def validate_timeline_json(timeline_json: str) -> tuple[bool, str]:
        """
        验证Timeline JSON格式

        Args:
            timeline_json: Timeline JSON字符串

        Returns:
            tuple: (是否有效, 错误消息)
        """
        try:
            timeline = json.loads(timeline_json)

            # 基本结构验证
            if "VideoTracks" not in timeline:
                return False, "缺少VideoTracks字段"

            if not isinstance(timeline["VideoTracks"], list):
                return False, "VideoTracks必须是数组"

            if len(timeline["VideoTracks"]) == 0:
                return False, "VideoTracks不能为空"

            video_track = timeline["VideoTracks"][0]
            if "VideoTrackClips" not in video_track:
                return False, "缺少VideoTrackClips字段"

            if not isinstance(video_track["VideoTrackClips"], list):
                return False, "VideoTrackClips必须是数组"

            return True, ""

        except json.JSONDecodeError as e:
            return False, f"JSON格式错误: {str(e)}"
        except Exception as e:
            return False, f"验证失败: {str(e)}"
