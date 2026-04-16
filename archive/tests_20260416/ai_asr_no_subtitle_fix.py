#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI_ASR 字幕问题 - 精确诊断和解决方案

根据用户提供的信息：
1. ✅ 主视频有清晰的中文语音
2. ✅ ICE 作业状态是 Success
3. ✅ 生成的视频可以正常播放
4. ❌ 但没有字幕

结论：AI_ASR 配置没有生效！
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def diagnose_with_audio():
    """有音频但无字幕的诊断"""
    print("=" * 70)
    print("🔬 精确诊断：有音频但无字幕")
    print("=" * 70)
    print()

    print("根据你的情况：")
    print("  ✅ 主视频有清晰的中文语音")
    print("  ✅ ICE 作业状态是 Success")
    print("  ✅ 生成的视频可以正常播放")
    print("  ❌ 但没有字幕")
    print()

    print("结论：AI_ASR 配置没有生效！")
    print()

    print("=" * 70)
    print("🔍 可能的根本原因")
    print("=" * 70)
    print()

    causes = [
        {
            "priority": 1,
            "reason": "Timeline 中的 AI_ASR 配置没有正确提交",
            "description": "虽然模板中有 AI_ASR，但提交给 ICE 时丢失了",
            "possibility": "⭐⭐⭐⭐⭐"
        },
        {
            "priority": 2,
            "reason": "占位符 $main_video 替换后没有 AI_ASR",
            "description": "Timeline 占位符替换时，Effects 被忽略了",
            "possibility": "⭐⭐⭐⭐"
        },
        {
            "priority": 3,
            "reason": "OutputMediaConfig 覆盖了 AI_ASR 设置",
            "description": "硬编码的配置可能与 AI_ASR 冲突",
            "possibility": "⭐⭐⭐"
        },
        {
            "priority": 4,
            "reason": "字幕生成了但看不见",
            "description": "字体颜色、大小、透明度问题",
            "possibility": "⭐⭐"
        }
    ]

    print(f"{'优先级':<8} {'原因':<40} {'可能性'}")
    print("-" * 100)
    for cause in causes:
        print(f"{cause['priority']:<8} {cause['reason']:<40} {cause['possibility']}")
        print(f"         {cause['description']}")
        print()

    return causes


def show_verification_steps():
    """显示验证步骤"""
    print("=" * 70)
    print("🛠️  验证步骤（找出问题）")
    print("=" * 70)
    print()

    print("步骤 1: 查看应用日志（最重要！）")
    print("-" * 70)
    print("我已经添加了详细的日志，现在重新运行应用并提交任务：")
    print()
    print("  python app.py")
    print()
    print("然后查找日志中的关键信息：")
    print("  🔍 提交的 Timeline: { ... }")
    print("  🔍 提交的 OutputMediaConfig: { ... }")
    print("  🔍 阿里云完整响应: { ... }")
    print()
    print("确认：Timeline 中是否包含 AI_ASR Effects？")
    print()

    print("步骤 2: 检查实际提交的配置")
    print("-" * 70)
    print("在日志中搜索 'AI_ASR'，确认：")
    print("  ✅ Timeline JSON 中有 'Type': 'AI_ASR'")
    print("  ✅ Effects 数组不为空")
    print("  ✅ Y 值在合理范围内（不是 1700）")
    print()

    print("步骤 3: 查看阿里云控制台")
    print("-" * 70)
    print("1. 登录阿里云控制台")
    print("2. 进入 ICE 服务")
    print("3. 找到你的作业")
    print("4. 查看作业详情")
    print("5. 确认 Timeline 配置")
    print()

    print("步骤 4: 验证生成的视频")
    print("-" * 70)
    print("1. 下载生成的视频")
    print("2. 用播放器打开")
    print("3. 逐帧查看（检查每一帧）")
    print("4. 确认完全没有字幕（而不是位置不对）")
    print()


def show_solutions():
    """显示解决方案"""
    print("=" * 70)
    print("🔧 解决方案")
    print("=" * 70)
    print()

    print("方案 1: 使用直接的视频 URL 测试（推荐）")
    print("-" * 70)
    print("不要使用占位符，直接用实际 URL：")
    print()

    test_timeline = {
        "VideoTracks": [
            {
                "VideoTrackClips": [
                    {
                        "MediaURL": "https://krillin-3.oss-cn-shanghai.aliyuncs.com/uploads/20260411_054117_start.mp4",
                        "MainTrack": True,
                        "Effects": [
                            {
                                "Type": "AI_ASR",
                                "Font": "AlibabaPuHuiTi",
                                "Alignment": "BottomCenter",
                                "Y": 600,
                                "FontSize": 60,
                                "FontColor": "#FFFFFF",
                                "Outline": 5,
                                "OutlineColour": "#000000"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    print(json.dumps(test_timeline, indent=2, ensure_ascii=False))
    print()

    print("方案 2: 检查任务处理器代码")
    print("-" * 70)
    print("查看 services/task_processor.py 中的 _build_timeline 方法")
    print("确认：")
    print("  1. Timeline 是否正确构建")
    print("  2. 占位符是否正确替换")
    print("  3. AI_ASR Effects 是否被保留")
    print()

    print("方案 3: 添加调试日志")
    print("-" * 70)
    print("我已经在 services/ice_service.py 中添加了详细日志：")
    print("  - 记录提交的 Timeline")
    print("  - 记录提交的 OutputMediaConfig")
    print("  - 记录阿里云完整响应")
    print()
    print("重启应用后查看日志：")
    print("  python app.py")
    print()

    print("方案 4: 使用阿里云控制台测试")
    print("-" * 70)
    print("1. 登录 https://oss.console.aliyun.com")
    print("2. 进入 ICE 服务")
    print("3. 手动创建剪辑工程")
    print("4. 使用你的 Timeline 配置")
    print("5. 提交作业并查看结果")
    print()


def show_investigation_questions():
    """显示调查问题"""
    print("=" * 70)
    print("📝 请回答以下问题帮助进一步诊断")
    print("=" * 70)
    print()

    questions = [
        {
            "q": "查看应用日志，'提交的 Timeline' 中是否包含 'AI_ASR'？",
            "options": [
                "A. 包含 'Type': 'AI_ASR'",
                "B. 不包含 AI_ASR"
            ]
        },
        {
            "q": "Timeline 中的 Effects 数组是否为空？",
            "options": [
                "A. Effects 数组有内容",
                "B. Effects 数组为空"
            ]
        },
        {
            "q": "MediaURL 是实际的 URL 还是占位符？",
            "options": [
                "A. 是实际的 https:// URL",
                "B. 还是 $main_video 占位符"
            ]
        },
        {
            "q": "阿里云控制台显示的 Timeline 配置是什么？",
            "options": [
                "A. 包含 AI_ASR 配置",
                "B. 不包含 AI_ASR 配置"
            ]
        },
        {
            "q": "生成的视频文件大小是多少？",
            "options": [
                "A. 和原视频大小差不多（可能没有重新编码）",
                "B. 比原视频大（已重新编码，应该有字幕）"
            ]
        }
    ]

    for i, item in enumerate(questions, 1):
        print(f"问题 {i}: {item['q']}")
        for j, option in enumerate(item['options'], 1):
            print(f"  {j}. {option}")
        print()

    print()
    print("请回答这些问题，帮助我精确定位问题！")
    print()


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🎯 AI_ASR 字幕问题 - 精确诊断")
    print("=" * 70)
    print()

    print("你的情况总结：")
    print("  ✅ 有清晰的中文语音")
    print("  ✅ ICE 作业状态是 Success")
    print("  ✅ 视频可以正常播放")
    print("  ❌ 没有字幕")
    print()

    diagnose_with_audio()
    print()

    show_verification_steps()
    print()

    show_solutions()
    print()

    show_investigation_questions()
    print()

    print("=" * 70)
    print("🚀 立即执行的操作")
    print("=" * 70)
    print()
    print("1. 重启应用（加载新日志）：")
    print("   python app.py")
    print()
    print("2. 重新提交一个视频处理任务")
    print()
    print("3. 查看控制台日志，搜索：")
    print("   - '提交的 Timeline'")
    print("   - 'AI_ASR'")
    print("   - '阿里云完整响应'")
    print()
    print("4. 把日志中的这些信息发给我")
    print()


if __name__ == "__main__":
    main()
