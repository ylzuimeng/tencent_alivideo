#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查模板中的 AI_ASR 配置
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def check_templates():
    """检查所有模板的AI_ASR配置"""
    print("=" * 70)
    print("🔍 检查所有模板的 AI_ASR 配置")
    print("=" * 70)
    print()

    from app import app
    from models import VideoTemplate

    with app.app_context():
        templates = VideoTemplate.query.all()

        if not templates:
            print("❌ 没有找到任何模板")
            return

        print(f"{'ID':<5} {'名称':<30} {'高级模式':<10} {'AI_ASR'}")
        print("-" * 70)

        templates_with_ai_asr = []

        for t in templates:
            has_ai_asr = "❌"
            if t.is_advanced and t.timeline_json:
                try:
                    timeline = json.loads(t.timeline_json)
                    timeline_str = json.dumps(timeline, ensure_ascii=False)
                    if "AI_ASR" in timeline_str:
                        has_ai_asr = "✅"
                        templates_with_ai_asr.append(t)
                except Exception as e:
                    print(f"解析失败: {e}")

            mode = "高级" if t.is_advanced else "简单"
            print(f"{t.id:<5} {t.name:<30} {mode:<10} {has_ai_asr}")

        print()
        print("=" * 70)
        print(f"📊 统计: 共 {len(templates)} 个模板，{len(templates_with_ai_asr)} 个包含 AI_ASR")
        print("=" * 70)
        print()

        if templates_with_ai_asr:
            print("✅ 包含 AI_ASR 的模板:")
            for t in templates_with_ai_asr:
                print(f"   - ID {t.id}: {t.name}")
                if t.timeline_json:
                    try:
                        timeline = json.loads(t.timeline_json)
                        print(f"     Timeline: {json.dumps(timeline, indent=2, ensure_ascii=False)[:200]}...")
                    except:
                        pass
                print()
        else:
            print("❌ 没有找到包含 AI_ASR 的模板!")
            print()
            print("需要创建一个包含 AI_ASR 的高级模板。")


def show_template_details(template_id):
    """显示模板详细信息"""
    print("=" * 70)
    print(f"📋 模板详情 (ID: {template_id})")
    print("=" * 70)
    print()

    from app import app
    from models import VideoTemplate

    with app.app_context():
        template = VideoTemplate.query.get(template_id)
        if not template:
            print(f"❌ 模板 {template_id} 不存在")
            return

        print(f"名称: {template.name}")
        print(f"高级模式: {template.is_advanced}")
        print()

        if template.timeline_json:
            print("Timeline JSON:")
            try:
                timeline = json.loads(template.timeline_json)
                print(json.dumps(timeline, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"解析失败: {e}")
        else:
            print("❌ 没有 Timeline JSON 配置")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        template_id = int(sys.argv[1])
        show_template_details(template_id)
    else:
        check_templates()