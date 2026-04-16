#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查任务状态
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def check_task_status():
    """检查任务状态"""
    print("=" * 70)
    print("🔍 检查任务状态")
    print("=" * 70)
    print()

    from app import app
    from models import db, ProcessingTask

    with app.app_context():
        # 查询最近的任务
        recent_tasks = ProcessingTask.query.order_by(
            ProcessingTask.created_at.desc()
        ).limit(5).all()

        if not recent_tasks:
            print("❌ 没有找到任何任务")
            return

        print(f"{'ID':<6} {'任务名称':<25} {'状态':<12} {'进度':<8} {'ICE 作业 ID':<40}")
        print("-" * 110)

        status_emoji = {
            'pending': '⏳',
            'processing': '🔄',
            'completed': '✅',
            'failed': '❌'
        }

        for task in recent_tasks:
            emoji = status_emoji.get(task.status, '❓')
            print(f"{task.id:<6} {task.task_name:<25} {emoji} {task.status:<10} {task.progress:<8} {task.ice_job_id or 'N/A':<40}")

        print()

        # 详细显示最新任务
        latest_task = recent_tasks[0]
        print("=" * 70)
        print(f"📋 最新任务详情 (ID: {latest_task.id})")
        print("=" * 70)
        print()

        print(f"任务名称: {latest_task.task_name}")
        print(f"状态: {status_emoji.get(latest_task.status, '❓')} {latest_task.status}")
        print(f"进度: {latest_task.progress}%")
        print()

        print("⏰ 时间信息:")
        print(f"  创建时间: {latest_task.created_at}")
        if latest_task.updated_at:
            print(f"  更新时间: {latest_task.updated_at}")
        if latest_task.completed_at:
            print(f"  完成时间: {latest_task.completed_at}")
        print()

        print("🔗 阿里云 ICE 信息:")
        print(f"  作业 ID: {latest_task.ice_job_id or '未设置'}")
        print(f"  工程 ID: {latest_task.ice_project_id or '未设置'}")
        print()

        print("📹 输出信息:")
        print(f"  输出 URL: {latest_task.output_oss_url or '未生成'}")
        print()

        if latest_task.error_message:
            print("⚠️  错误信息:")
            print(f"  {latest_task.error_message}")
            print()

        # 检查 ICE 服务状态
        if latest_task.ice_job_id:
            print("=" * 70)
            print("🔍 阿里云 ICE 作业状态")
            print("=" * 70)
            print()

            try:
                from services.ice_service import ICEClient

                client = ICEClient()
                status_info = client.query_job_status(latest_task.ice_job_id)

                if status_info:
                    print(f"作业状态: {status_emoji.get(status_info.get('status', 'unknown'), '❓')} {status_info.get('status', 'unknown')}")
                    print(f"作业进度: {status_info.get('progress', 0)}%")
                    print(f"输出 URL: {status_info.get('output_url', 'N/A')}")
                    print()

                    # 显示详细信息
                    print("详细信息:")
                    for key, value in status_info.items():
                        if key != 'raw_response':
                            print(f"  {key}: {value}")
                    print()

                    # 检查是否完成
                    if status_info.get('status') == 'completed':
                        print("✅ 任务已完成！请检查生成的视频")
                        print()
                        print(f"下载地址: {status_info.get('output_url')}")
                    elif status_info.get('status') == 'processing':
                        print("⏳ 任务正在处理中，请稍等...")
                    elif status_info.get('status') == 'failed':
                        print("❌ 任务处理失败")
                    else:
                        print(f"⏳ 任务状态: {status_info.get('status')}")
                else:
                    print("⚠️  无法获取作业状态")

            except Exception as e:
                print(f"❌ 查询作业状态失败: {str(e)}")
        else:
            print("⚠️  任务没有设置 ICE 作业 ID")

        print()


def show_recent_logs():
    """显示最近的日志"""
    print("=" * 70)
    print("📝 最近的日志")
    print("=" * 70)
    print()

    import subprocess

    # 获取最近的 50 行日志
    try:
        result = subprocess.run(
            ['tail', '-50', '/tmp/flask_app.log'],
            capture_output=True,
            text=True,
            timeout=5
        )

        print(result.stdout)
        print()

    except Exception as e:
        print(f"❌ 读取日志失败: {str(e)}")


def main():
    """主函数"""
    check_task_status()
    print()
    show_recent_logs()


if __name__ == "__main__":
    main()
