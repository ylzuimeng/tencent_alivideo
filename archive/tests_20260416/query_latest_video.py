#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查询最新生成的视频信息

查看：
1. 最新的视频任务
2. 阿里云返回的信息
3. 日志记录情况
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
from models import db, ProcessingTask


def query_latest_video():
    """查询最新视频信息"""
    with app.app_context():
        print("=" * 70)
        print("🎬 最新生成的视频信息")
        print("=" * 70)
        print()

        # 查询最新的任务（按创建时间倒序）
        latest_task = ProcessingTask.query.order_by(
            ProcessingTask.created_at.desc()
        ).first()

        if not latest_task:
            print("❌ 没有找到任何任务")
            return

        print("📋 任务基本信息")
        print("-" * 70)
        print(f"任务 ID: {latest_task.id}")
        print(f"任务名称: {latest_task.task_name}")
        print(f"状态: {latest_task.status}")
        print(f"进度: {latest_task.progress}%")
        print(f"创建时间: {latest_task.created_at}")
        if latest_task.completed_at:
            print(f"完成时间: {latest_task.completed_at}")
        print()

        print("🔗 阿里云 ICE 信息")
        print("-" * 70)
        print(f"作业 ID (job_id): {latest_task.ice_job_id or '未设置'}")
        print(f"工程 ID (project_id): {latest_task.ice_project_id or '未设置'}")
        print()

        print("📹 输出信息")
        print("-" * 70)
        print(f"输出 OSS URL: {latest_task.output_oss_url or '未生成'}")
        print()

        if latest_task.error_message:
            print("⚠️  错误信息")
            print("-" * 70)
            print(latest_task.error_message)
            print()

        print("📄 完整任务信息")
        print("-" * 70)
        print(f"源文件 ID: {latest_task.source_file_id}")
        print(f"模板 ID: {latest_task.video_template_id}")
        print(f"医生信息 ID: {latest_task.doctor_info_id}")
        print(f"使用高级 Timeline: {latest_task.use_advanced_timeline}")
        print()

        # 查询最近 5 个任务
        print("=" * 70)
        print("📊 最近 5 个任务")
        print("=" * 70)
        print()

        recent_tasks = ProcessingTask.query.order_by(
            ProcessingTask.created_at.desc()
        ).limit(5).all()

        print(f"{'ID':<5} {'任务名称':<25} {'状态':<12} {'进度':<8} {'作业 ID'}")
        print("-" * 70)

        for task in recent_tasks:
            status_emoji = {
                'pending': '⏳',
                'processing': '🔄',
                'completed': '✅',
                'failed': '❌'
            }.get(task.status, '')

            print(f"{task.id:<5} {task.task_name:<25} {status_emoji + ' ' + task.status:<11} {task.progress:<8} {task.ice_job_id or 'N/A':<20}")

        print()


def check_ice_response_structure():
    """显示阿里云 ICE 返回的信息结构"""
    print("=" * 70)
    print("📋 阿里云 ICE 返回信息结构")
    print("=" * 70)
    print()

    print("1. 提交作业时返回 (submit_editing_job):")
    print("-" * 70)
    print("""
    返回字典包含:
    {
        'project_id': '工程ID',
        'job_id': '作业ID',
        'request_id': '请求ID'
    }
    """)
    print("记录位置: services/ice_service.py:403-407")
    print()

    print("2. 查询作业状态时返回 (query_job_status):")
    print("-" * 70)
    print("""
    返回字典包含:
    {
        'status': '状态 (pending/processing/completed/failed)',
        'progress': '进度 (0-100)',
        'output_url': '输出视频URL'
    }
    """)
    print("记录位置: services/ice_service.py:461-465")
    print()

    print("3. 阿里云完整响应 (GetMediaProducingJob):")
    print("-" * 70)
    print("""
    response.body.media_producing_job 包含:
    {
        'JobId': '作业ID',
        'Status': '状态码 (Created/Queued/Processing/Success/Failed)',
        'MediaURL': '输出视频URL',
        'CreateTime': '创建时间',
        'FinishTime': '完成时间',
        'Code': '错误码',
        'Message': '错误信息',
        ...
    }
    """)
    print("解析位置: services/ice_service.py:430-465")
    print()


def show_logged_info():
    """显示已记录的日志信息"""
    print("=" * 70)
    print("📝 已记录的日志信息")
    print("=" * 70)
    print()

    print("1. ICE 服务日志 (services/ice_service.py):")
    print("-" * 70)
    print("""
    ✅ logger.info(f"创建ICE客户端成功，Region: {self.region}")
    ✅ logger.info(f"创建剪辑工程成功: {create_response.body.request_id}")
    ✅ logger.info(f"提取的 Project ID: {project_id}")
    ✅ logger.info(f"提交剪辑作业成功: {submit_response.body.job_id}")
    ❌ logger.error(f"提交剪辑作业失败: {str(e)}")
    ❌ logger.error(f"查询作业状态失败: {str(e)}")
    """)
    print()

    print("2. 任务处理器日志 (services/task_processor.py):")
    print("-" * 70)
    print("""
    ✅ logger.info(f"创建任务成功: {task_name} (ID: {task.id})")
    ✅ logger.info(f"提交ICE作业: 任务ID={task_id}")
    ✅ logger.info(f"任务进度更新: {task.task_name} - {task.progress}%")
    ✅ logger.info(f"任务完成: {task.task_name}")
    ❌ logger.error(f"任务失败: {task.task_name}")
    ❌ logger.error(f"处理任务失败: {str(e)}")
    """)
    print()

    print("3. 数据库记录 (ProcessingTask 表):")
    print("-" * 70)
    print("""
    ✅ ice_job_id - 阿里云作业ID
    ✅ ice_project_id - 阿里云工程ID
    ✅ output_oss_url - 成品视频URL
    ✅ status - 任务状态
    ✅ progress - 处理进度
    ✅ error_message - 错误信息
    ✅ created_at / updated_at / completed_at - 时间戳
    """)
    print()


def main():
    """主函数"""
    query_latest_video()
    print()
    check_ice_response_structure()
    print()
    show_logged_info()

    print("=" * 70)
    print("💡 查看日志文件")
    print("=" * 70)
    print()
    print("日志位置:")
    print("  - 开发环境: 控制台输出")
    print("  - 生产环境: 检查日志配置 (config.py)")
    print()
    print("查看方式:")
    print("  python app.py  # 运行应用查看实时日志")
    print("  tail -f logs/app.log  # 查看日志文件（如果配置了文件日志）")
    print()


if __name__ == "__main__":
    main()
