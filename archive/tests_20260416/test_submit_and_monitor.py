#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
提交测试任务并查看详细日志
"""

import sys
import os
import json
import time
import subprocess

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def submit_test_task():
    """提交一个测试任务"""
    print("=" * 70)
    print("🧪 提交测试任务")
    print("=" * 70)
    print()

    from app import app
    from models import db, File, VideoTemplate, ProcessingTask, DoctorInfo

    with app.app_context():
        # 查找一个测试视频
        test_file = File.query.first()
        if not test_file:
            print("❌ 没有找到视频文件，请先上传视频")
            return

        print(f"📹 使用视频: {test_file.filename}")
        print(f"   URL: {test_file.oss_url}")
        print()

        # 查找一个模板
        template = VideoTemplate.query.filter_by(is_advanced=True).first()
        if not template:
            print("❌ 没有找到高级模板，请先创建模板")
            return

        print(f"📋 使用模板: {template.name}")
        print(f"   模板 ID: {template.id}")
        print()

        # 显示 Timeline 内容
        if template.timeline_json:
            try:
                timeline = json.loads(template.timeline_json)
                print("📝 Timeline 配置:")
                print(json.dumps(timeline, indent=2, ensure_ascii=False))
                print()

                # 检查是否包含 AI_ASR
                timeline_str = json.dumps(timeline, ensure_ascii=False)
                if "AI_ASR" in timeline_str:
                    print("✅ Timeline 包含 AI_ASR 配置")
                else:
                    print("❌ Timeline 不包含 AI_ASR 配置")
                print()

            except Exception as e:
                print(f"❌ 解析 Timeline 失败: {e}")
        print()

        # 创建任务
        print("⏳ 创建任务...")
        task = ProcessingTask(
            task_name=f"测试字幕任务_{time.strftime('%H%M%S')}",
            source_file_id=test_file.id,
            video_template_id=template.id,
            status='pending'
        )

        db.session.add(task)
        db.session.commit()

        print(f"✅ 任务创建成功!")
        print(f"   任务 ID: {task.id}")
        print(f"   任务名称: {task.task_name}")
        print()

        return task.id


def monitor_logs(task_id):
    """监控日志输出"""
    print("=" * 70)
    print(f"📋 监控任务 {task_id} 的日志")
    print("=" * 70)
    print()

    print("🔍 关键日志标记:")
    print("  - 提交的 Timeline")
    print("  - AI_ASR")
    print("  - 提交的 OutputMediaConfig")
    print("  - 阿里云完整响应")
    print()

    print("💡 提示:")
    print("  在另一个终端运行:")
    print(f"  tail -f /tmp/flask_app.log | grep -E '🔍|{task_id}|AI_ASR'")
    print()


def show_diagnostic_commands():
    """显示诊断命令"""
    print("=" * 70)
    print("🔧 诊断命令")
    print("=" * 70)
    print()

    commands = [
        {
            "name": "查看所有日志",
            "cmd": "tail -100 /tmp/flask_app.log"
        },
        {
            "name": "查看诊断日志",
            "cmd": "grep '🔍' /tmp/flask_app.log"
        },
        {
            "name": "查看 AI_ASR 相关",
            "cmd": "grep -i 'ai_asr' /tmp/flask_app.log"
        },
        {
            "name": "查看 Timeline 相关",
            "cmd": "grep -i 'timeline' /tmp/flask_app.log"
        },
        {
            "name": "实时监控日志",
            "cmd": "tail -f /tmp/flask_app.log"
        }
    ]

    print("可用命令:")
    for item in commands:
        print(f"\n{item['name']}:")
        print(f"  {item['cmd']}")
    print()


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🧪 AI_ASR 字幕诊断工具")
    print("=" * 70)
    print()

    # 提交测试任务
    task_id = submit_test_task()

    if task_id:
        # 显示监控信息
        monitor_logs(task_id)

        # 显示诊断命令
        show_diagnostic_commands()

        print("=" * 70)
        print("📝 下一步")
        print("=" * 70)
        print()
        print("1. 查看实时日志:")
        print("   tail -f /tmp/flask_app.log")
        print()
        print("2. 搜索关键字:")
        print("   grep '🔍' /tmp/flask_app.log")
        print()
        print("3. 等待任务完成后，把相关日志发给我")
        print()


if __name__ == "__main__":
    main()
