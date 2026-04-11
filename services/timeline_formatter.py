"""
Timeline占位符格式化模块

功能：
- 占位符替换 ($main_video, $mainSubtitleDepart, etc.)
- 中文竖排文本转换
- 动态数据注入
"""
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DefaultTimelineFormatter:
    """默认Timeline格式化器 - 支持医疗场景"""

    # 占位符到数据字段的映射
    PLACEHOLDER_MAP = {
        '$main_video': 'main_video_url',
        '$mainSubtitleDepart': 'hospital_department',
        '$mainSubtitleName': 'doctor_title',
        '$beginingSubtitleTitle': 'video_title',
        '$beginingAudioTitle': 'video_title',
    }

    def format(self, template: str, data: Dict[str, Any]) -> str:
        """
        格式化Timeline模板，替换占位符

        Args:
            template: Timeline JSON字符串（包含占位符）
            data: 数据字典，包含:
                - main_video_url: 主视频URL
                - hospital: 医院名称
                - department: 科室
                - name: 医生姓名
                - title: 职称
                - video_title: 视频标题

        Returns:
            格式化后的Timeline JSON字符串
        """
        try:
            timeline_str = template

            # 替换主视频URL
            if 'main_video_url' in data:
                timeline_str = timeline_str.replace('$main_video', data['main_video_url'])

            # 替换医院科室（竖排格式）
            hospital = data.get('hospital', '')
            department = data.get('department', '')
            if hospital or department:
                vertical_text = self._to_vertical_text(f"{hospital} {department}".strip())
                timeline_str = timeline_str.replace('$mainSubtitleDepart', vertical_text)

            # 替换姓名职称（竖排格式）
            name = data.get('name', '')
            title = data.get('title', '')
            if name or title:
                vertical_text = self._to_vertical_text(f"{name} {title}".strip())
                timeline_str = timeline_str.replace('$mainSubtitleName', vertical_text)

            # 替换标题（用于字幕和TTS）
            video_title = data.get('video_title', '')
            timeline_str = timeline_str.replace('$beginingSubtitleTitle', video_title)
            timeline_str = timeline_str.replace('$beginingAudioTitle', video_title)

            # 验证JSON格式
            json.loads(timeline_str)
            return timeline_str

        except Exception as e:
            logger.error(f"格式化Timeline失败: {str(e)}")
            raise ValueError(f"Timeline格式化失败: {str(e)}")

    @staticmethod
    def _to_vertical_text(text: str) -> str:
        """
        将中文文本转换为竖排格式

        Args:
            text: 原始文本

        Returns:
            每个字符后加换行符的文本

        Example:
            "青岛大学附属医院" -> "青\\n岛\\n大\\n学\\n附\\n属\\n医\\n院"
        """
        # 移除多余空格，每个字符单独一行
        cleaned = text.replace(' ', '')
        # 使用 \\n 而不是 \n，这样在JSON中会被正确解析为换行符
        return '\\n'.join(cleaned)


def format_timeline_default(template: str, data: Dict[str, Any]) -> str:
    """
    默认格式化函数（便捷调用）

    Args:
        template: Timeline JSON字符串
        data: 数据字典

    Returns:
        格式化后的Timeline JSON字符串
    """
    formatter = DefaultTimelineFormatter()
    return formatter.format(template, data)


def subtitle_content_to_vertical(text: str) -> str:
    """
    字幕内容竖排格式化（兼容旧代码）

    Args:
        text: 原始文本

    Returns:
        竖排格式文本
    """
    return DefaultTimelineFormatter._to_vertical_text(text)
