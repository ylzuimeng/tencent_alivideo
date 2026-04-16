#!/usr/bin/env python3
"""
测试统一模板管理页面的编辑功能

测试场景：
1. 获取模板列表
2. 获取单个模板详情
3. 更新模板信息
4. 验证更新结果
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_template_edit():
    print("=" * 60)
    print("测试模板编辑功能")
    print("=" * 60)

    # 测试1: 获取模板列表
    print("\n[测试1] 获取模板列表...")
    response = requests.get(f"{BASE_URL}/api/video_templates")
    result = response.json()

    if result['success']:
        templates = result['templates']
        print(f"✓ 成功获取 {len(templates)} 个模板")

        # 查找"片头片尾"模板
        target_template = None
        for t in templates:
            if '片头片尾' in t['name'] and t['is_advanced']:
                target_template = t
                break

        if not target_template:
            print("✗ 未找到目标模板")
            return False

        print(f"✓ 找到目标模板: {target_template['name']} (ID: {target_template['id']})")
    else:
        print("✗ 获取模板列表失败")
        return False

    template_id = target_template['id']

    # 测试2: 获取模板详情
    print(f"\n[测试2] 获取模板详情 (ID: {template_id})...")
    response = requests.get(f"{BASE_URL}/api/video_templates/{template_id}")
    result = response.json()

    if result['success']:
        template = result['template']
        print(f"✓ 模板名称: {template['name']}")
        print(f"✓ 模板类型: {'高级' if template['is_advanced'] else '简单'}")
        print(f"✓ 分类: {template['category']}")
        print(f"✓ 描述: {template['description'][:50]}...")

        # 验证高级模板字段
        if template['is_advanced']:
            if template.get('timeline_json'):
                timeline = json.loads(template['timeline_json'])
                print(f"✓ Timeline 包含 {len(timeline['VideoTracks'])} 个视频轨道")
            if template.get('formatter_type'):
                print(f"✓ 格式化器类型: {template['formatter_type']}")
    else:
        print("✗ 获取模板详情失败")
        return False

    # 测试3: 更新模板
    print(f"\n[测试3] 更新模板...")

    # 准备更新数据
    update_data = {
        "name": "实际文件模板-片头片尾",
        "category": "general",
        "description": "使用实际OSS文件的视频模板：片头 + 主视频 + 片尾 (已测试编辑)",
        "is_advanced": True,
        "formatter_type": "default",
        "timeline_json": template['timeline_json'],
        "enable_subtitle": template['enable_subtitle'],
        "subtitle_position": template['subtitle_position']
    }

    response = requests.put(
        f"{BASE_URL}/api/video_templates/{template_id}",
        json=update_data
    )
    result = response.json()

    if result['success']:
        print("✓ 模板更新成功")
    else:
        print(f"✗ 模板更新失败: {result.get('message', '未知错误')}")
        return False

    # 测试4: 验证更新结果
    print(f"\n[测试4] 验证更新结果...")
    response = requests.get(f"{BASE_URL}/api/video_templates/{template_id}")
    result = response.json()

    if result['success']:
        updated_template = result['template']
        if updated_template['description'] == update_data['description']:
            print("✓ 描述已更新")
        else:
            print("✗ 描述未正确更新")
            return False

        if updated_template['name'] == update_data['name']:
            print("✓ 名称已更新")
        else:
            print("✗ 名称未正确更新")
            return False

        if updated_template['is_advanced'] == update_data['is_advanced']:
            print("✓ 模板类型已保持")
        else:
            print("✗ 模板类型未正确保持")
            return False
    else:
        print("✗ 无法获取更新后的模板")
        return False

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_template_edit()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
