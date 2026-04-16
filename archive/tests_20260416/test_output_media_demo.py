#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OutputMediaConfig 配置演示脚本

展示如何使用 OutputMediaConfig 配置功能
"""

import json
from services.json_validator import validate_output_media_config


def demo_basic_validation():
    """演示基础验证功能"""
    print("=" * 70)
    print("📋 演示 1: 基础配置验证")
    print("=" * 70)
    print()

    # 标准配置
    config = {
        "Width": 1280,
        "Height": 720
    }

    config_json = json.dumps(config, ensure_ascii=False)
    is_valid, error_msg = validate_output_media_config(config_json)

    print(f"OutputMediaConfig:")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print()
    print(f"验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
    if not is_valid:
        print(f"错误信息: {error_msg}")
    print()


def demo_full_config():
    """演示完整配置验证"""
    print("=" * 70)
    print("📋 演示 2: 完整参数配置")
    print("=" * 70)
    print()

    # 完整配置
    config = {
        "Width": 1280,
        "Height": 720,
        "Bitrate": 2000,
        "Fps": 30,
        "Format": "mp4"
    }

    config_json = json.dumps(config, ensure_ascii=False)
    is_valid, error_msg = validate_output_media_config(config_json)

    print(f"完整 OutputMediaConfig:")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print()
    print(f"验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
    if not is_valid:
        print(f"错误信息: {error_msg}")
    print()


def demo_invalid_config():
    """演示无效配置的错误检测"""
    print("=" * 70)
    print("📋 演示 3: 无效配置检测")
    print("=" * 70)
    print()

    # 无效配置
    invalid_configs = [
        {
            "name": "分辨率超出范围",
            "config": {
                "Width": 5000,  # 超过最大值 3840
                "Height": 2160
            }
        },
        {
            "name": "不支持的格式",
            "config": {
                "Width": 1280,
                "Height": 720,
                "Format": "avi"  # 不支持的格式
            }
        },
        {
            "name": "码率过低",
            "config": {
                "Width": 1280,
                "Height": 720,
                "Bitrate": 50  # 低于最小值 100
            }
        }
    ]

    for item in invalid_configs:
        print(f"测试: {item['name']}")
        config_json = json.dumps(item['config'], ensure_ascii=False)
        is_valid, error_msg = validate_output_media_config(config_json)

        print(f"配置: {json.dumps(item['config'], ensure_ascii=False)}")
        print(f"验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
        if not is_valid:
            print(f"错误信息: {error_msg}")
        print()


def demo_resolution_comparison():
    """演示不同分辨率配置"""
    print("=" * 70)
    print("📋 演示 4: 常用分辨率对比")
    print("=" * 70)
    print()

    resolutions = [
        ("480p (移动端)", 640, 480),
        ("720p (标准)", 1280, 720),
        ("1080p (高清)", 1920, 1080),
        ("4K (超高清)", 3840, 2160)
    ]

    print(f"{'名称':<20} {'宽度':<10} {'高度':<10} {'验证结果'}")
    print("-" * 70)

    for name, width, height in resolutions:
        config = {"Width": width, "Height": height}
        config_json = json.dumps(config, ensure_ascii=False)
        is_valid, _ = validate_output_media_config(config_json)

        status = "✅ 通过" if is_valid else "❌ 失败"
        print(f"{name:<20} {width:<10} {height:<10} {status}")

    print()


def demo_real_world_scenarios():
    """演示真实场景配置"""
    print("=" * 70)
    print("📋 演示 5: 真实场景配置")
    print("=" * 70)
    print()

    scenarios = [
        {
            "name": "医疗视频（项目标准）",
            "config": {
                "Width": 1280,
                "Height": 720
            },
            "description": "标准清晰度，适合医疗健康宣教视频"
        },
        {
            "name": "教育视频（高清）",
            "config": {
                "Width": 1920,
                "Height": 1080,
                "Bitrate": 3000,
                "Fps": 30
            },
            "description": "全高清，高码率，适合教育课程"
        },
        {
            "name": "移动端优化",
            "config": {
                "Width": 854,
                "Height": 480,
                "Bitrate": 800,
                "Fps": 24
            },
            "description": "低分辨率，低码率，适合移动网络"
        },
        {
            "name": "快速预览",
            "config": {
                "Width": 640,
                "Height": 360,
                "Bitrate": 500,
                "Fps": 15
            },
            "description": "低质量，快速生成，适合预览"
        }
    ]

    for scenario in scenarios:
        print(f"场景: {scenario['name']}")
        print(f"说明: {scenario['description']}")
        print(f"配置:")
        print(json.dumps(scenario['config'], indent=2, ensure_ascii=False))

        config_json = json.dumps(scenario['config'], ensure_ascii=False)
        is_valid, _ = validate_output_media_config(config_json)
        print(f"验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
        print()


def demo_usage_in_template():
    """演示在模板中使用"""
    print("=" * 70)
    print("📋 演示 6: 在模板中使用 OutputMediaConfig")
    print("=" * 70)
    print()

    # 完整的模板配置
    template_config = {
        "name": "医疗健康宣教视频模板",
        "timeline_json": {
            "VideoTracks": [{
                "VideoTrackClips": [{
                    "MediaURL": "$main_video",
                    "MainTrack": True,
                    "Effects": [{
                        "Type": "AI_ASR",
                        "Font": "AlibabaPuHuiTi",
                        "FontSize": 60
                    }]
                }]
            }]
        },
        "output_media_config": {
            "Width": 1280,
            "Height": 720
        }
    }

    print("完整模板配置:")
    print(json.dumps(template_config, indent=2, ensure_ascii=False))
    print()

    # 验证 OutputMediaConfig
    config_json = json.dumps(template_config['output_media_config'], ensure_ascii=False)
    is_valid, error_msg = validate_output_media_config(config_json)

    print(f"OutputMediaConfig 验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
    if not is_valid:
        print(f"错误信息: {error_msg}")
    print()


def main():
    """运行所有演示"""
    print("\n" + "=" * 70)
    print("🎬 OutputMediaConfig 配置演示")
    print("=" * 70)
    print()

    demo_basic_validation()
    demo_full_config()
    demo_invalid_config()
    demo_resolution_comparison()
    demo_real_world_scenarios()
    demo_usage_in_template()

    print("=" * 70)
    print("✅ 所有演示完成！")
    print("=" * 70)
    print()
    print("💡 提示:")
    print("  1. 运行完整测试: python test_output_media_config.py")
    print("  2. 查看详细文档: OUTPUT_MEDIA_CONFIG_GUIDE.md")
    print("  3. 在代码中导入: from services.json_validator import validate_output_media_config")
    print()


if __name__ == "__main__":
    main()
