#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加高级模板字段到 video_template 表

添加以下字段：
- timeline_json (TEXT)
- output_media_config (TEXT)
- editing_produce_config (TEXT)
- formatter_type (VARCHAR(50))
- category (VARCHAR(100))
- is_advanced (BOOLEAN)
- thumbnail_url (VARCHAR(255))

同时给 processing_task 表添加：
- use_advanced_timeline (BOOLEAN)
"""
import sys
import os
import sqlite3

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def migrate_database():
    """执行数据库迁移"""

    # 获取数据库路径
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'data.db')

    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("=" * 70)
        print("开始数据库迁移：添加高级模板字段")
        print("=" * 70)

        # 检查并添加 video_template 表的新字段
        video_template_columns = [
            ("timeline_json", "TEXT"),
            ("output_media_config", "TEXT"),
            ("editing_produce_config", "TEXT"),
            ("formatter_type", "VARCHAR(50) DEFAULT 'default'"),
            ("category", "VARCHAR(100) DEFAULT 'general'"),
            ("is_advanced", "BOOLEAN DEFAULT 0"),
            ("thumbnail_url", "VARCHAR(255)"),
        ]

        # 获取现有的列
        cursor.execute("PRAGMA table_info(video_template)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # 添加新列（如果不存在）
        for col_name, col_type in video_template_columns:
            if col_name not in existing_columns:
                sql = f"ALTER TABLE video_template ADD COLUMN {col_name} {col_type}"
                cursor.execute(sql)
                print(f"✅ 添加字段: video_template.{col_name}")
            else:
                print(f"⏭️  字段已存在: video_template.{col_name}")

        # 检查并添加 processing_task 表的新字段
        cursor.execute("PRAGMA table_info(processing_task)")
        existing_task_columns = {row[1] for row in cursor.fetchall()}

        if "use_advanced_timeline" not in existing_task_columns:
            cursor.execute("ALTER TABLE processing_task ADD COLUMN use_advanced_timeline BOOLEAN DEFAULT 0")
            print(f"✅ 添加字段: processing_task.use_advanced_timeline")
        else:
            print(f"⏭️  字段已存在: processing_task.use_advanced_timeline")

        # 提交更改
        conn.commit()

        print("=" * 70)
        print("✅ 数据库迁移完成！")
        print("=" * 70)

        # 显示更新后的表结构
        print("\n📋 video_template 表结构:")
        cursor.execute("PRAGMA table_info(video_template)")
        for row in cursor.fetchall():
            print(f"   • {row[1]} ({row[2]})")

        print("\n📋 processing_task 表结构:")
        cursor.execute("PRAGMA table_info(processing_task)")
        for row in cursor.fetchall():
            print(f"   • {row[1]} ({row[2]})")

        print()
        return True

    except sqlite3.Error as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
