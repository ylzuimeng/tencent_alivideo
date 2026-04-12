"""
时间处理工具模块

提供时区转换、时间序列化等功能，统一应用中的时间处理逻辑。
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional

# 时区配置
BEIJING_TZ = ZoneInfo('Asia/Shanghai')
UTC_TZ = timezone.utc


def utcnow() -> datetime:
    """
    获取当前UTC时间（带时区信息）

    Returns:
        datetime对象，timezone设置为UTC
    """
    return datetime.now(UTC_TZ)


def to_beijing_time(utc_datetime: Optional[datetime]) -> Optional[datetime]:
    """
    将UTC时间转换为北京时间

    Args:
        utc_datetime: UTC时间对象（naive或aware）

    Returns:
        北京时间对象（aware），如果输入为None则返回None
    """
    if utc_datetime is None:
        return None

    # 如果是naive datetime，假设为UTC
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=UTC_TZ)

    return utc_datetime.astimezone(BEIJING_TZ)


def serialize_datetime(dt: Optional[datetime], to_beijing: bool = True) -> Optional[str]:
    """
    序列化datetime为ISO 8601字符串

    Args:
        dt: datetime对象
        to_beijing: 是否转换为北京时间后再序列化（默认True）

    Returns:
        ISO 8601格式字符串，带时区信息
    """
    if dt is None:
        return None

    # 如果是naive datetime，假设为UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)

    # 转换为北京时间（如果需要）
    if to_beijing:
        dt = dt.astimezone(BEIJING_TZ)

    return dt.isoformat()


def format_datetime_beijing(dt: Optional[datetime], format_str: str = '%Y-%m-%d %H:%M') -> Optional[str]:
    """
    格式化datetime为北京时间字符串（用于Jinja2模板）

    Args:
        dt: datetime对象（naive或aware）
        format_str: 格式化字符串

    Returns:
        格式化后的字符串
    """
    if dt is None:
        return None

    beijing_dt = to_beijing_time(dt)
    return beijing_dt.strftime(format_str)
