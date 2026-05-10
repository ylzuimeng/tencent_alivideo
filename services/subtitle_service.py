"""字幕服务模块

封装字幕相关的业务逻辑：SRT 生成、字幕数据解析、内容更新、OSS 上传。
"""
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SubtitleService:
    """字幕服务"""

    @staticmethod
    def generate_srt_content(segments: list[dict]) -> str:
        """将 segments 数组转为标准 SRT 格式字符串

        Args:
            segments: 字幕分段列表，每条含 index/content/from/to

        Returns:
            标准 SRT 格式字符串
        """
        if not segments:
            return ''

        lines = []
        for i, seg in enumerate(segments):
            index = i + 1
            start = SubtitleService._format_srt_timestamp(seg['from'])
            end = SubtitleService._format_srt_timestamp(seg['to'])
            content = seg['content']

            lines.append(f'{index}')
            lines.append(f'{start} --> {end}')
            lines.append(content)
            lines.append('')

        return '\n'.join(lines)

    @staticmethod
    def _format_srt_timestamp(seconds: float) -> str:
        """将秒数转为 SRT 时间戳格式 HH:MM:SS,mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds - int(seconds)) * 1000))
        return f'{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}'

    @staticmethod
    def parse_subtitle_data(subtitle_json: Optional[str]) -> Optional[dict]:
        """安全解析 subtitle_data JSON

        Args:
            subtitle_json: JSON 字符串

        Returns:
            解析后的字典，无效输入返回 None
        """
        if not subtitle_json:
            return None
        try:
            data = json.loads(subtitle_json)
            if isinstance(data, dict):
                return data
            return None
        except (json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def update_subtitle_content(subtitle_data: dict, updated_segments: list[dict]) -> dict:
        """仅更新 segments 中的 content 字段，保留 from/to 时间戳不变

        Args:
            subtitle_data: 原始 subtitle_data 字典
            updated_segments: 更新后的 segments（只含 index 和 content）

        Returns:
            更新后的 subtitle_data 字典
        """
        # 建立 index -> content 映射
        content_map = {seg['index']: seg['content'] for seg in updated_segments}

        # 仅更新 content，保留其他字段
        for seg in subtitle_data.get('segments', []):
            idx = seg['index']
            if idx in content_map:
                seg['content'] = content_map[idx]

        return subtitle_data

    @staticmethod
    def upload_srt_to_oss(srt_content: str, task_id: int) -> str:
        """将 SRT 文件上传至 OSS

        Args:
            srt_content: SRT 文件内容
            task_id: 任务 ID

        Returns:
            OSS 文件 URL
        """
        from services.oss_service import OSSConfig, OSSClient

        config = OSSConfig()
        client = OSSClient(config)

        oss_path = f'subtitles/{task_id}_{SubtitleService._timestamp()}.srt'
        client.upload_file(srt_content.encode('utf-8'), oss_path)

        return config.get_file_url(oss_path)

    @staticmethod
    def build_subtitle_timeline(timeline_json: str, srt_url: str) -> str:
        """重建 Timeline：保留 VideoTracks/AudioTracks，替换 SubtitleTracks 为 SRT 轨道

        Args:
            timeline_json: 原始 Timeline JSON 字符串（用于提取 VideoTracks/AudioTracks）
            srt_url: 更新后的 SRT 文件 OSS URL

        Returns:
            新的 Timeline JSON 字符串
        """
        original = json.loads(timeline_json)

        # 保留 VideoTracks 和 AudioTracks，替换 SubtitleTracks
        result = {}
        if 'VideoTracks' in original:
            result['VideoTracks'] = original['VideoTracks']
        if 'AudioTracks' in original:
            result['AudioTracks'] = original['AudioTracks']

        result['SubtitleTracks'] = [{
            'SubtitleTrackClips': [{
                'Type': 'Subtitle',
                'SubtitleURL': srt_url,
            }]
        }]

        return json.dumps(result, ensure_ascii=False)

    @staticmethod
    def _timestamp() -> str:
        from utils.time_helpers import utcnow
        return utcnow().strftime('%Y%m%d_%H%M%S')
