#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI_ASR 字幕问题诊断工具

分析 Timeline 配置，找出 AI_ASR 字幕不生成的原因
"""

import json
from services.json_validator import validate_timeline_json


def analyze_timeline_issue():
    """分析 Timeline 配置问题"""
    print("=" * 70)
    print("🔍 AI_ASR 字幕问题诊断")
    print("=" * 70)
    print()

    # 用户的 Timeline 配置
    timeline = {
        "VideoTracks": [
            {
                "VideoTrackClips": [
                    {
                        "MediaURL": "https://krillin-3.oss-cn-shanghai.aliyuncs.com/uploads/20260411_054117_start.mp4",
                        "Duration": 3
                    },
                    {
                        "MediaURL": "$main_video",
                        "MainTrack": True,
                        "Effects": [
                            {
                                "Type": "AI_ASR",
                                "Font": "AlibabaPuHuiTi",
                                "Alignment": "BottomCenter",
                                "Y": 1700,
                                "Outline": 3,
                                "OutlineColour": "#000000",
                                "FontSize": 50,
                                "FontColor": "#FFFFFF",
                                "FontFace": {
                                    "Bold": False,
                                    "Italic": False,
                                    "Underline": False
                                }
                            }
                        ]
                    },
                    {
                        "MediaURL": "https://krillin-3.oss-cn-shanghai.aliyuncs.com/uploads/20260411_054117_start.mp4",
                        "Duration": 3
                    }
                ]
            }
        ]
    }

    print("📋 你的 Timeline 配置:")
    print(json.dumps(timeline, indent=2, ensure_ascii=False))
    print()

    # 验证格式
    timeline_json = json.dumps(timeline, ensure_ascii=False)
    is_valid, error_msg = validate_timeline_json(timeline_json)

    if is_valid:
        print("✅ Timeline 格式验证通过")
    else:
        print(f"❌ Timeline 格式错误: {error_msg}")
        return

    print()

    # 问题诊断
    print("=" * 70)
    print("⚠️  发现的问题")
    print("=" * 70)
    print()

    # 问题 1: Y 值过大
    print("❌ 问题 1: 字幕位置 Y 值超出视频范围")
    print("-" * 70)
    print(f"当前 Y 值: {timeline['VideoTracks'][0]['VideoTrackClips'][1]['Effects'][0]['Y']}")
    print()
    print("问题分析:")
    print("  - 你的视频是 720p (高度 720px)")
    print("  - 字幕 Y 位置设置为 1700")
    print("  - 字幕会显示在视频下方（视频外），看不到！")
    print()
    print("修复方案:")
    print("  对于 720p 视频，Y 值应该在 0-650 之间")
    print("  推荐值: Y = 600 (底部留出边距)")
    print()

    # 问题 2: 可能缺少音频
    print("⚠️  问题 2: 主视频可能没有音频")
    print("-" * 70)
    print("AI_ASR 需要主视频包含音频才能识别语音")
    print()
    print("检查方法:")
    print("  1. 确认主视频文件有音频轨道")
    print("  2. 播放主视频，确认有声音")
    print("  3. 检查音频是否清晰（无杂音、无静音）")
    print()

    # 问题 3: 字幕颜色对比度
    print("⚠️  问题 3: 字幕颜色对比度可能不够")
    print("-" * 70)
    font_color = timeline['VideoTracks'][0]['VideoTrackClips'][1]['Effects'][0]['FontColor']
    outline_color = timeline['VideoTracks'][0]['VideoTrackClips'][1]['Effects'][0]['OutlineColour']
    print(f"字体颜色: {font_color} (白色)")
    print(f"描边颜色: {outline_color} (黑色)")
    print(f"描边宽度: 3")
    print()
    print("分析:")
    print("  - 白色字幕 + 黑色描边 = 对比度好 ✅")
    print("  - 但如果视频背景也是白色，就看不清了")
    print()
    print("建议:")
    print("  - 保持白色字体 + 黑色描边")
    print("  - 或者使用黄色字体 + 黑色描边 (更醒目)")
    print()

    # 问题 4: 字体大小
    print("⚠️  问题 4: 字体大小")
    print("-" * 70)
    font_size = timeline['VideoTracks'][0]['VideoTrackClips'][1]['Effects'][0]['FontSize']
    print(f"当前字号: {font_size}")
    print()
    print("分析:")
    print("  - 对于 720p 视频，字号 50 是合适的")
    print("  - 但如果视频很小，字号 50 可能会太大")
    print()

    # 正确的配置示例
    print("=" * 70)
    print("✅ 推荐的配置（修复后）")
    print("=" * 70)
    print()

    fixed_timeline = {
        "VideoTracks": [
            {
                "VideoTrackClips": [
                    {
                        "MediaURL": "https://krillin-3.oss-cn-shanghai.aliyuncs.com/uploads/20260411_054117_start.mp4",
                        "Duration": 3
                    },
                    {
                        "MediaURL": "$main_video",
                        "MainTrack": True,
                        "Effects": [
                            {
                                "Type": "AI_ASR",
                                "Font": "AlibabaPuHuiTi",
                                "Alignment": "BottomCenter",
                                "Y": 600,  # 🔧 修复：从 1700 改为 600
                                "Outline": 3,
                                "OutlineColour": "#000000",
                                "FontSize": 50,
                                "FontColor": "#FFFFFF"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    print("修复后的 Timeline:")
    print(json.dumps(fixed_timeline, indent=2, ensure_ascii=False))
    print()

    print("主要修改:")
    print("  - Y 值从 1700 改为 600")
    print("  - 移除了第三个重复的片头视频")
    print()

    # 不同分辨率的 Y 值参考
    print("=" * 70)
    print("📏 不同分辨率的字幕 Y 值参考")
    print("=" * 70)
    print()

    resolutions = [
        ("480p", 640, 480, 430),
        ("720p", 1280, 720, 600),
        ("1080p", 1920, 1080, 950),
    ]

    print(f"{'分辨率':<10} {'宽度':<10} {'高度':<10} {'推荐 Y 值'}")
    print("-" * 70)
    for name, width, height, y in resolutions:
        print(f"{name:<10} {width:<10} {height:<10} {y}")
    print()

    # 其他可能的原因
    print("=" * 70)
    print("🔎 其他可能导致字幕不生成的原因")
    print("=" * 70)
    print()

    reasons = [
        "主视频没有音频轨道",
        "主视频音频是静音",
        "主视频音频质量太差（杂音、回声）",
        "主视频语言不是中文（AI_ASR 默认识别中文）",
        "主视频时长太短（小于 1 秒）",
        "阿里云 ICE 配额已用完",
        "占位符 $main_video 没有正确替换",
        "视频文件损坏或格式不支持"
    ]

    for i, reason in enumerate(reasons, 1):
        print(f"{i}. {reason}")
    print()

    # 调试建议
    print("=" * 70)
    print("💡 调试建议")
    print("=" * 70)
    print()
    print("1. 先使用简单的 Timeline 测试:")
    print()
    print(json.dumps({
        "VideoTracks": [{
            "VideoTrackClips": [{
                "MediaURL": "$main_video",
                "MainTrack": True,
                "Effects": [{
                    "Type": "AI_ASR",
                    "Font": "AlibabaPuHuiTi",
                    "FontSize": 50
                }]
            }]
        }]
    }, indent=2, ensure_ascii=False))
    print()
    print("2. 检查阿里云 ICE 日志，确认作业状态")
    print("3. 确认主视频文件有音频且清晰")
    print("4. 尝试使用不同的 Y 值（600, 500, 400）")
    print()


if __name__ == "__main__":
    analyze_timeline_issue()
