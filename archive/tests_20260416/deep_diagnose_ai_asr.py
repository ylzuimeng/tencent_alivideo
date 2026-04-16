#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI_ASR 字幕问题深度诊断

系统性分析字幕不生成的所有可能原因
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def analyze_all_possible_causes():
    """分析所有可能的原因"""
    print("=" * 70)
    print("🔬 AI_ASR 字幕不生成 - 深度分析")
    print("=" * 70)
    print()

    causes = {
        "1. 核心问题（最可能）": {
            "原因": "主视频没有音频轨道",
            "可能性": "⭐⭐⭐⭐⭐",
            "检查方法": "播放主视频，确认是否有声音",
            "解决方案": "使用有音频的视频文件"
        },
        "2. 音频质量问题": {
            "原因": "音频是静音或质量太差",
            "可能性": "⭐⭐⭐⭐",
            "检查方法": "检查音频是否清晰、有无杂音",
            "解决方案": "使用高质量的音频源"
        },
        "3. ICE 服务配置": {
            "原因": "OutputMediaConfig 配置不完整",
            "可能性": "⭐⭐⭐⭐",
            "检查方法": "查看提交的完整配置",
            "解决方案": "添加完整的 OutputMediaConfig"
        },
        "4. 占位符替换问题": {
            "原因": "$main_video 没有正确替换",
            "可能性": "⭐⭐⭐",
            "检查方法": "查看日志中的实际 Timeline",
            "解决方案": "确认占位符替换逻辑"
        },
        "5. 视频格式不支持": {
            "原因": "视频格式不支持 AI_ASR",
            "可能性": "⭐⭐⭐",
            "检查方法": "确认视频格式（mp4/avi/mov）",
            "解决方案": "转换为支持的格式"
        },
        "6. 语言识别问题": {
            "原因": "视频语言不是中文",
            "可能性": "⭐⭐",
            "检查方法": "确认视频语音语言",
            "解决方案": "配置语言参数"
        },
        "7. 阿里云服务问题": {
            "原因": "ICE 配额不足或服务异常",
            "可能性": "⭐⭐",
            "检查方法": "查看阿里云控制台",
            "解决方案": "检查账户状态和配额"
        },
        "8. 作业状态问题": {
            "原因": "作业实际失败但状态显示成功",
            "可能性": "⭐⭐",
            "检查方法": "查看完整的 ICE 响应",
            "解决方案": "检查作业日志"
        }
    }

    print("📋 可能原因分析（按可能性排序）:")
    print()
    print(f"{'优先级':<10} {'原因':<30} {'可能性':<15} {'检查方法'}")
    print("-" * 100)

    for i, (key, info) in enumerate(causes.items(), 1):
        print(f"{key:<10} {info['原因']:<30} {info['可能性']:<15} {info['检查方法']}")
        print()

    return causes


def check_current_task_status():
    """检查当前任务状态"""
    print("=" * 70)
    print("🔍 检查当前任务状态")
    print("=" * 70)
    print()

    from app import app
    from models import db, ProcessingTask

    with app.app_context():
        # 查询最新的任务
        latest_task = ProcessingTask.query.order_by(
            ProcessingTask.created_at.desc()
        ).first()

        if not latest_task:
            print("❌ 没有找到任何任务")
            return

        print(f"任务 ID: {latest_task.id}")
        print(f"任务名称: {latest_task.task_name}")
        print(f"状态: {latest_task.status}")
        print(f"进度: {latest_task.progress}%")
        print()

        print("📋 阿里云 ICE 信息:")
        print(f"  作业 ID: {latest_task.ice_job_id or '未设置'}")
        print(f"  工程 ID: {latest_task.ice_project_id or '未设置'}")
        print()

        print("📹 视频信息:")
        print(f"  输出 URL: {latest_task.output_oss_url or '未生成'}")
        print()

        if latest_task.error_message:
            print(f"⚠️  错误信息: {latest_task.error_message}")
            print()

        return latest_task


def show_diagnostic_steps():
    """显示诊断步骤"""
    print("=" * 70)
    print("🛠️  诊断步骤（按顺序执行）")
    print("=" * 70)
    print()

    steps = [
        {
            "step": 1,
            "title": "验证主视频文件",
            "actions": [
                "下载主视频文件",
                "使用播放器播放，确认有声音",
                "检查音频是否清晰",
                "确认语音是中文"
            ]
        },
        {
            "step": 2,
            "title": "检查 ICE 作业日志",
            "actions": [
                "登录阿里云控制台",
                "进入 ICE 服务",
                "查看作业详情",
                "确认作业状态是 Success（不是 Failed）"
            ]
        },
        {
            "step": 3,
            "title": "验证 Timeline 配置",
            "actions": [
                "查看提交的完整 Timeline",
                "确认 AI_ASR 配置存在",
                "确认 Y 值在合理范围",
                "确认占位符已正确替换"
            ]
        },
        {
            "step": 4,
            "title": "检查视频输出",
            "actions": [
                "播放生成的视频",
                "检查视频底部是否有字幕",
                "如果字幕位置不对，调整 Y 值",
                "尝试不同的 Y 值（400, 500, 600）"
            ]
        },
        {
            "step": 5,
            "title": "测试最小配置",
            "actions": [
                "使用最简单的 Timeline 测试",
                "只有主视频 + AI_ASR",
                "不要片头片尾",
                "确认能识别语音"
            ]
        }
    ]

    for item in steps:
        print(f"步骤 {item['step']}: {item['title']}")
        print("-" * 70)
        for i, action in enumerate(item['actions'], 1):
            print(f"  {i}. {action}")
        print()


def show_common_fixes():
    """显示常见修复方案"""
    print("=" * 70)
    print("🔧 常见修复方案")
    print("=" * 70)
    print()

    fixes = [
        {
            "问题": "视频没有音频",
            "修复": "使用有音频的视频，或添加音频轨道"
        },
        {
            "问题": "字幕位置不对",
            "修复": "调整 Y 值：720p 用 600，1080p 用 950"
        },
        {
            "问题": "AI_ASR 未生效",
            "修复": "检查 Timeline 是否正确提交到 ICE"
        },
        {
            "问题": "语言不支持",
            "修复": "确认视频是中文，或配置语言参数"
        },
        {
            "问题": "视频格式不支持",
            "修复": "转换为 MP4 格式（H.264 编码）"
        },
        {
            "问题": "音频质量差",
            "修复": "使用高质量音频源，降低噪音"
        }
    ]

    print(f"{'问题':<25} {'修复方案'}")
    print("-" * 70)

    for fix in fixes:
        print(f"{fix['问题']:<25} {fix['修复']}")
        print()

    print()


def show_minimal_test_timeline():
    """显示最小测试配置"""
    print("=" * 70)
    print("🧪 最小测试配置（推荐先测试这个）")
    print("=" * 70)
    print()

    minimal_timeline = {
        "VideoTracks": [
            {
                "VideoTrackClips": [
                    {
                        "MediaURL": "你的视频URL.mp4",  # 直接用实际 URL 测试
                        "MainTrack": True,
                        "Effects": [
                            {
                                "Type": "AI_ASR",
                                "Font": "AlibabaPuHuiTi",
                                "FontSize": 50
                            }
                        ]
                    }
                ]
            }
        ]
    }

    print("测试步骤:")
    print("1. 将上面的 '你的视频URL.mp4' 替换为实际的视频 URL")
    print("2. 不要使用占位符，直接用实际 URL")
    print("3. 不要片头片尾，只有主视频")
    print("4. 提交作业，查看是否有字幕")
    print()
    print("最小测试 Timeline:")
    print(json.dumps(minimal_timeline, indent=2, ensure_ascii=False))
    print()


def show_ice_request_checklist():
    """显示 ICE 请求检查清单"""
    print("=" * 70)
    print("📋 ICE 请求检查清单")
    print("=" * 70)
    print()

    checklist = [
        ("Timeline JSON", "✅ 是否包含 AI_ASR 配置"),
        ("", "✅ Y 值是否在合理范围（720p: 0-650）"),
        ("", "✅ MediaURL 是否正确替换"),
        ("OutputMediaConfig", "✅ 是否配置了 Width 和 Height"),
        ("", "✅ mediaURL 是否正确设置"),
        ("视频文件", "✅ 是否有音频轨道"),
        ("", "✅ 音频是否清晰"),
        ("", "✅ 文件格式是否支持（MP4 推荐）"),
        ("", "✅ 文件是否可以正常访问"),
        ("阿里云账户", "✅ ICE 配额是否充足"),
        ("", "✅ 账户余额是否充足"),
        ("", "✅ 区域是否支持 AI_ASR 功能")
    ]

    current_category = ""
    for item in checklist:
        if item[0] != current_category:
            current_category = item[0]
            print(f"\n{current_category}:")
        print(f"  {item[1]}")

    print()


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🔬 AI_ASR 字幕问题 - 全面诊断")
    print("=" * 70)
    print()

    # 分析所有可能原因
    analyze_all_possible_causes()
    print()

    # 检查当前任务状态
    # check_current_task_status()
    # print()

    # 显示诊断步骤
    show_diagnostic_steps()
    print()

    # 显示修复方案
    show_common_fixes()
    print()

    # 显示最小测试配置
    show_minimal_test_timeline()
    print()

    # 显示检查清单
    show_ice_request_checklist()
    print()

    print("=" * 70)
    print("🎯 最可能的原因（按优先级）")
    print("=" * 70)
    print()
    print("1. ⭐⭐⭐⭐⭐ 主视频没有音频轨道或音频是静音")
    print("2. ⭐⭐⭐⭐   AI_ASR 配置没有正确提交到 ICE")
    print("3. ⭐⭐⭐⭐   视频格式不支持或编码问题")
    print("4. ⭐⭐⭐     占位符替换失败，URL 无效")
    print("5. ⭐⭐       语言不支持或音频质量差")
    print()

    print("=" * 70)
    print("💡 建议的排查顺序")
    print("=" * 70)
    print()
    print("第一步：验证主视频")
    print("  - 播放主视频，确认有清晰的声音")
    print("  - 检查音频是否是中文语音")
    print()
    print("第二步：查看 ICE 日志")
    print("  - 登录阿里云控制台")
    print("  - 查看 ICE 作业的详细信息")
    print("  - 确认作业状态是 Success")
    print()
    print("第三步：测试最小配置")
    print("  - 使用只有主视频的 Timeline")
    print("  - 不要片头片尾")
    print("  - 直接用实际 URL，不要占位符")
    print()
    print("第四步：检查完整响应")
    print("  - 查看 ICE 返回的完整 JSON")
    print("  - 确认 AI_ASR 是否生效")
    print("  - 检查是否有错误信息")
    print()


if __name__ == "__main__":
    main()
