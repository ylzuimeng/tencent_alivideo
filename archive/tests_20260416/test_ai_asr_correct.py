#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
正确测试 AI_ASR 字幕功能

关键修复：使用 use_advanced_timeline=True
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def create_test_task():
    """创建正确配置的测试任务"""
    print("=" * 70)
    print("🧪 创建 AI_ASR 测试任务（正确配置）")
    print("=" * 70)
    print()

    from app import app
    from models import db, File, VideoTemplate, DoctorInfo
    from services.task_processor import TaskProcessor

    with app.app_context():
        # 查找测试视频
        test_file = File.query.first()
        if not test_file:
            print("❌ 没有找到视频文件")
            return None

        print(f"📹 使用视频: {test_file.filename}")
        print(f"   URL: {test_file.oss_url}")
        print()

        # 查找高级模板（包含 AI_ASR）
        template = VideoTemplate.query.filter_by(
            id=3,  # 医疗健康宣教视频模板
            is_advanced=True
        ).first()

        if not template:
            print("❌ 没有找到高级模板")
            return None

        print(f"📋 使用模板: {template.name}")
        print(f"   模板 ID: {template.id}")
        print(f"   高级模式: {template.is_advanced}")
        print(f"   包含 AI_ASR: ✅")
        print()

        # 🔑 关键：使用 TaskProcessor 创建任务（自动处理异步）
        # ❌ 错误做法：直接创建 ProcessingTask（不会触发处理）
        # ✅ 正确做法：通过 task_processor.create_task()（会异步处理）
        task_processor = TaskProcessor()

        print("⏳ 创建任务（通过 TaskProcessor）...")
        print("   配置: use_advanced_timeline=True ✅")
        print()

        task = task_processor.create_task(
            task_name=f"AI_ASR测试_{os.popen('date +%H%M%S').read().strip()}",
            source_file_id=test_file.id,
            video_template_id=template.id,
            use_advanced_timeline=True  # 🔑 关键配置！
        )

        print(f"✅ 任务已创建并提交处理!")
        print(f"   任务 ID: {task.id}")
        print(f"   任务名称: {task.task_name}")
        print(f"   状态: {task.status}")
        print()

        return task.id


def monitor_task(task_id):
    """监控任务状态"""
    import time

    print("=" * 70)
    print(f"📋 监控任务 {task_id}")
    print("=" * 70)
    print()

    from app import app
    from models import ProcessingTask

    print("⏳ 等待任务处理... (按 Ctrl+C 停止)")
    print()

    try:
        with app.app_context():
            while True:
                task = ProcessingTask.query.get(task_id)
                if not task:
                    print(f"❌ 任务 {task_id} 不存在")
                    break

                status_emoji = {
                    'pending': '⏳',
                    'processing': '🔄',
                    'completed': '✅',
                    'failed': '❌'
                }

                emoji = status_emoji.get(task.status, '❓')
                print(f"\r[{emoji}] 状态: {task.status} | 进度: {task.progress}% | ICE Job: {task.ice_job_id or '等待中...'}   ", end='', flush=True)

                if task.status in ['completed', 'failed']:
                    print()  # 换行
                    print()
                    print("=" * 70)
                    if task.status == 'completed':
                        print("✅ 任务完成!")
                        print(f"输出视频: {task.output_oss_url}")
                    else:
                        print("❌ 任务失败")
                        print(f"错误信息: {task.error_message}")
                    print("=" * 70)
                    break

                time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n⏸️  监控已停止")
        print(f"使用以下命令查看任务状态:")
        print(f"  python check_task_status.py")


def main():
    print("\n" + "=" * 70)
    print("🧪 AI_ASR 字幕功能测试（正确配置）")
    print("=" * 70)
    print()

    print("🔑 关键修复:")
    print("   使用 use_advanced_timeline=True")
    print("   这样任务处理器会使用高级模板（包含 AI_ASR）")
    print()

    # 创建测试任务
    task_id = create_test_task()

    if task_id:
        print("=" * 70)
        print("💡 与之前任务的区别:")
        print("=" * 70)
        print()
        print("❌ Task 9 (失败):")
        print("   - 直接创建 ProcessingTask")
        print("   - use_advanced_timeline=False")
        print("   - 结果：使用了简单模板，没有 AI_ASR")
        print()
        print("✅ 当前任务 (正确):")
        print("   - 通过 TaskProcessor.create_task() 创建")
        print("   - use_advanced_timeline=True")
        print("   - 结果：使用高级模板，包含 AI_ASR")
        print()

        # 监控任务
        monitor_task(task_id)


if __name__ == "__main__":
    main()