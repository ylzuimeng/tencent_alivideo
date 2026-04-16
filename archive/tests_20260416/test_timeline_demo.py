#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Timeline 测试演示脚本

展示如何使用 Timeline 验证功能
"""

import json
from services.json_validator import validate_timeline_json


def demo_basic_validation():
    """演示基础验证功能"""
    print("=" * 70)
    print("📋 演示 1: 基础 Timeline 验证")
    print("=" * 70)
    print()

    # 有效的 Timeline
    valid_timeline = {
        "VideoTracks": [{
            "VideoTrackClips": [{
                "MediaURL": "$main_video",
                "MainTrack": True
            }]
        }]
    }

    timeline_json = json.dumps(valid_timeline, ensure_ascii=False)
    is_valid, error_msg = validate_timeline_json(timeline_json)

    print(f"Timeline JSON:")
    print(json.dumps(valid_timeline, indent=2, ensure_ascii=False))
    print()
    print(f"验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
    if not is_valid:
        print(f"错误信息: {error_msg}")
    print()


def demo_ai_asr_validation():
    """演示 AI_ASR 字幕验证"""
    print("=" * 70)
    print("📋 演示 2: AI_ASR 自动字幕验证")
    print("=" * 70)
    print()

    # 带 AI_ASR 的 Timeline
    ai_asr_timeline = {
        "VideoTracks": [{
            "VideoTrackClips": [{
                "MediaURL": "$main_video",
                "MainTrack": True,
                "Effects": [{
                    "Type": "AI_ASR",
                    "Font": "AlibabaPuHuiTi",
                    "FontSize": 60,
                    "FontColor": "#000079",
                    "Alignment": "BottomCenter",
                    "Y": 600,
                    "Outline": 10,
                    "OutlineColour": "#ffffff"
                }]
            }]
        }]
    }

    timeline_json = json.dumps(ai_asr_timeline, ensure_ascii=False)
    is_valid, error_msg = validate_timeline_json(timeline_json)

    print(f"Timeline JSON (带 AI_ASR):")
    print(json.dumps(ai_asr_timeline, indent=2, ensure_ascii=False))
    print()
    print(f"验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
    if not is_valid:
        print(f"错误信息: {error_msg}")
    print()


def demo_invalid_timeline():
    """演示无效 Timeline 的错误检测"""
    print("=" * 70)
    print("📋 演示 3: 无效 Timeline 的错误检测")
    print("=" * 70)
    print()

    # 缺少必需字段的 Timeline
    invalid_timeline = {
        "VideoTracks": [{
            "VideoTrackClips": [{
                "MainTrack": True
                # 缺少 MediaURL
            }]
        }]
    }

    timeline_json = json.dumps(invalid_timeline, ensure_ascii=False)
    is_valid, error_msg = validate_timeline_json(timeline_json)

    print(f"Timeline JSON (缺少 MediaURL):")
    print(json.dumps(invalid_timeline, indent=2, ensure_ascii=False))
    print()
    print(f"验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
    if not is_valid:
        print(f"错误信息: {error_msg}")
    print()


def demo_subtitle_tracks():
    """演示 SubtitleTracks 字幕验证"""
    print("=" * 70)
    print("📋 演示 4: SubtitleTracks 自定义字幕验证")
    print("=" * 70)
    print()

    # 带自定义字幕的 Timeline
    subtitle_timeline = {
        "VideoTracks": [{
            "VideoTrackClips": [{
                "MediaURL": "$main_video",
                "MainTrack": True,
                "ClipId": "main-video"
            }]
        }],
        "SubtitleTracks": [{
            "SubtitleTrackClips": [{
                "Type": "Text",
                "Content": "这是字幕内容",
                "X": 80,
                "Y": 100,
                "FontSize": 45,
                "FontColor": "#ffffff",
                "TimelineIn": 0,
                "TimelineOut": 5
            }]
        }]
    }

    timeline_json = json.dumps(subtitle_timeline, ensure_ascii=False)
    is_valid, error_msg = validate_timeline_json(timeline_json)

    print(f"Timeline JSON (带自定义字幕):")
    print(json.dumps(subtitle_timeline, indent=2, ensure_ascii=False))
    print()
    print(f"验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
    if not is_valid:
        print(f"错误信息: {error_msg}")
    print()


def demo_placeholder_replacement():
    """演示占位符替换功能"""
    print("=" * 70)
    print("📋 演示 5: Timeline 占位符替换")
    print("=" * 70)
    print()

    from services.timeline_formatter import DefaultTimelineFormatter

    # 带占位符的 Timeline
    timeline_with_placeholders = {
        "VideoTracks": [{
            "VideoTrackClips": [{
                "MediaURL": "$main_video",
                "MainTrack": True
            }]
        }],
        "SubtitleTracks": [{
            "SubtitleTrackClips": [{
                "Type": "Text",
                "Content": "$mainSubtitleDepart",
                "X": 80,
                "Y": 100,
                "FontSize": 45
            }]
        }]
    }

    # 测试数据
    test_data = {
        'main_video_url': 'https://oss.example.com/video.mp4',
        'hospital': '青岛大学附属医院',
        'department': '心内科'
    }

    timeline_json = json.dumps(timeline_with_placeholders, ensure_ascii=False)

    print("原始 Timeline (带占位符):")
    print(json.dumps(timeline_with_placeholders, indent=2, ensure_ascii=False))
    print()
    print("测试数据:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    print()

    # 替换占位符
    formatter = DefaultTimelineFormatter()
    formatted_timeline = formatter.format(timeline_json, test_data)

    print("替换后的 Timeline:")
    parsed = json.loads(formatted_timeline)
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
    print()


def demo_medical_template():
    """演示完整医疗模板验证"""
    print("=" * 70)
    print("📋 演示 6: 完整医疗模板验证")
    print("=" * 70)
    print()

    # 完整的医疗模板
    medical_timeline = {
        "VideoTracks": [{
            "VideoTrackClips": [
                {
                    "MediaURL": "https://oss.example.com/intro.mp4",
                    "Duration": 3
                },
                {
                    "MediaURL": "$main_video",
                    "MainTrack": True,
                    "ClipId": "main-2",
                    "Effects": [{
                        "Type": "AI_ASR",
                        "Font": "AlibabaPuHuiTi",
                        "Alignment": "TopCenter",
                        "Y": 600,
                        "FontSize": 60
                    }]
                }
            ]
        }],
        "SubtitleTracks": [{
            "SubtitleTrackClips": [
                {
                    "Type": "Text",
                    "X": 80,
                    "Y": 100,
                    "Content": "$mainSubtitleDepart",
                    "FontSize": 45,
                    "ReferenceClipId": "main-2"
                },
                {
                    "Type": "Text",
                    "X": 640,
                    "Y": 100,
                    "Content": "$beginingSubtitleTitle",
                    "Alignment": "TopCenter",
                    "FontSize": 50
                }
            ]
        }]
    }

    timeline_json = json.dumps(medical_timeline, ensure_ascii=False)
    is_valid, error_msg = validate_timeline_json(timeline_json)

    print(f"医疗模板 Timeline:")
    print(json.dumps(medical_timeline, indent=2, ensure_ascii=False))
    print()
    print(f"验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
    if not is_valid:
        print(f"错误信息: {error_msg}")
    print()


def main():
    """运行所有演示"""
    print("\n" + "=" * 70)
    print("🎬 Timeline 功能演示")
    print("=" * 70)
    print()

    demo_basic_validation()
    demo_ai_asr_validation()
    demo_invalid_timeline()
    demo_subtitle_tracks()
    demo_placeholder_replacement()
    demo_medical_template()

    print("=" * 70)
    print("✅ 所有演示完成！")
    print("=" * 70)
    print()
    print("💡 提示:")
    print("  1. 运行完整测试: python test_timeline_validation.py")
    print("  2. 查看详细文档: TIMELINE_TEST_GUIDE.md")
    print("  3. 在代码中导入: from services.json_validator import validate_timeline_json")
    print()


if __name__ == "__main__":
    main()
