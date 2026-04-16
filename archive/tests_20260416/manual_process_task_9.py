#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动处理卡住的任务

Task 9 被直接创建在数据库中，但没有通过 TaskProcessor 提交，
所以没有被实际处理。这个脚本会手动触发任务处理。
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def manual_process_task(task_id):
    """手动处理指定的任务"""
    print("=" * 70)
    print(f"🔧 手动处理任务 {task_id}")
    print("=" * 70)
    print()

    from app import app
    from services.task_processor import TaskProcessor
    from models import ProcessingTask

    # 创建应用上下文
    with app.app_context():
        # 创建任务处理器实例
        processor = TaskProcessor()

        # 获取任务
        task = ProcessingTask.query.get(task_id)
        if not task:
            print(f"❌ 任务 {task_id} 不存在")
            return False

        print(f"✅ 找到任务: {task.task_name}")
        print(f"   状态: {task.status}")
        print(f"   源文件 ID: {task.source_file_id}")
        print(f"   模板 ID: {task.video_template_id}")
        print()

        if task.status != 'pending':
            print(f"⚠️  任务状态不是 'pending'，当前状态: {task.status}")
            response = input("是否仍然尝试处理？(y/n): ")
            if response.lower() != 'y':
                print("取消操作")
                return False

        print("⏳ 开始处理任务...")
        print()

        try:
            # 直接调用处理方法
            processor._process_task(task_id)
            print("✅ 任务处理完成")
            return True
        except Exception as e:
            print(f"❌ 任务处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    print("\n" + "=" * 70)
    print("🔧 手动任务处理工具")
    print("=" * 70)
    print()

    # 处理 Task 9
    task_id = 9
    success = manual_process_task(task_id)

    print()
    if success:
        print("✅ 操作成功")
        print("请使用 check_task_status.py 查看任务状态")
    else:
        print("❌ 操作失败")


if __name__ == "__main__":
    main()