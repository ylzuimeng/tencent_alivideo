#!/usr/bin/env python3
"""
使用 requests + BeautifulSoup 测试模板编辑功能
模拟浏览器操作流程
"""

import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

class TemplateEditTester:
    def __init__(self):
        self.session = requests.Session()
        self.template_id = None

    def log(self, message, emoji="📌"):
        print(f"{emoji} {message}")

    def test_load_page(self):
        """测试1: 加载模板管理页面"""
        self.log("测试1: 加载模板管理页面", "🌐")
        response = self.session.get(f"{BASE_URL}/templates/unified")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            self.log(f"✓ 页面加载成功: {title.text if title else 'Unknown'}", "✅")
            return True
        else:
            self.log(f"✗ 页面加载失败: {response.status_code}", "❌")
            return False

    def test_get_templates_list(self):
        """测试2: 获取模板列表"""
        self.log("\n测试2: 获取模板列表", "📋")
        response = self.session.get(f"{BASE_URL}/api/video_templates")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                templates = data.get('templates', [])
                self.log(f"✓ 获取到 {len(templates)} 个模板", "✅")

                for t in templates:
                    type_str = "高级" if t.get('is_advanced') else "简单"
                    self.log(f"  - {t['name']} ({type_str}, ID: {t['id']})", "  ")

                # 查找目标模板
                target = None
                for t in templates:
                    if '片头片尾' in t['name'] and t.get('is_advanced'):
                        target = t
                        break

                if target:
                    self.template_id = target['id']
                    self.log(f"✓ 找到目标模板: {target['name']} (ID: {target['id']})", "🎯")
                    return True
                else:
                    self.log("✗ 未找到'片头片尾'模板", "❌")
                    return False
            else:
                self.log(f"✗ API返回失败: {data.get('message')}", "❌")
                return False
        else:
            self.log(f"✗ 请求失败: {response.status_code}", "❌")
            return False

    def test_get_template_detail(self):
        """测试3: 获取模板详情"""
        if not self.template_id:
            self.log("✗ 没有有效的模板ID", "❌")
            return False

        self.log(f"\n测试3: 获取模板详情 (ID: {self.template_id})", "📄")
        response = self.session.get(f"{BASE_URL}/api/video_templates/{self.template_id}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                template = data.get('template', {})
                self.log(f"✓ 获取模板详情成功", "✅")
                self.log(f"  名称: {template.get('name')}", "  ")
                self.log(f"  类型: {'高级' if template.get('is_advanced') else '简单'}", "  ")
                self.log(f"  分类: {template.get('category', '-')}", "  ")
                self.log(f"  格式化器: {template.get('formatter_type', '-')}", "  ")

                # 验证 Timeline JSON
                if template.get('timeline_json'):
                    try:
                        timeline = json.loads(template['timeline_json'])
                        tracks = len(timeline.get('VideoTracks', []))
                        self.log(f"  Timeline: {tracks} 个视频轨道", "  ")
                    except:
                        self.log("  Timeline: JSON解析失败", "  ")

                return template
            else:
                self.log(f"✗ API返回失败: {data.get('message')}", "❌")
                return None
        else:
            self.log(f"✗ 请求失败: {response.status_code}", "❌")
            return None

    def test_edit_template(self, template):
        """测试4: 编辑模板"""
        if not template:
            self.log("✗ 没有有效的模板数据", "❌")
            return False

        self.log("\n测试4: 编辑模板", "✏️")

        # 准备更新数据（模拟表单提交）
        update_data = {
            "name": "实际文件模板-片头片尾（自动化测试）",
            "category": template.get('category', 'general'),
            "description": template.get('description', '') + " - 已通过自动化测试编辑",
            "is_advanced": True,
            "formatter_type": template.get('formatter_type', 'default'),
            "thumbnail_url": template.get('thumbnail_url', ''),
            "timeline_json": template.get('timeline_json', '{}'),
            "output_media_config": template.get('output_media_config', ''),
            "editing_produce_config": template.get('editing_produce_config', ''),
            "enable_subtitle": template.get('enable_subtitle', False),
            "subtitle_position": template.get('subtitle_position', 'bottom'),
            "subtitle_extract_audio": template.get('subtitle_extract_audio', True)
        }

        self.log(f"正在更新模板: {update_data['name']}", "  ")

        response = self.session.put(
            f"{BASE_URL}/api/video_templates/{self.template_id}",
            json=update_data
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                self.log("✓ 模板更新成功", "✅")
                return True
            else:
                self.log(f"✗ 更新失败: {data.get('message')}", "❌")
                return False
        else:
            self.log(f"✗ 请求失败: {response.status_code}", "❌")
            return False

    def test_verify_update(self):
        """测试5: 验证更新结果"""
        self.log("\n测试5: 验证更新结果", "🔍")
        response = self.session.get(f"{BASE_URL}/api/video_templates/{self.template_id}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                template = data.get('template', {})

                # 验证名称
                if '自动化测试' in template.get('name', ''):
                    self.log("✓ 名称已更新", "✅")
                else:
                    self.log("✗ 名称未正确更新", "❌")
                    return False

                # 验证描述
                if '自动化测试' in template.get('description', ''):
                    self.log("✓ 描述已更新", "✅")
                else:
                    self.log("✗ 描述未正确更新", "❌")
                    return False

                # 验证类型
                if template.get('is_advanced'):
                    self.log("✓ 模板类型保持为高级", "✅")
                else:
                    self.log("✗ 模板类型不正确", "❌")
                    return False

                return True
            else:
                self.log(f"✗ API返回失败: {data.get('message')}", "❌")
                return False
        else:
            self.log(f"✗ 请求失败: {response.status_code}", "❌")
            return False

    def test_restore_template(self, template):
        """恢复原始模板数据"""
        self.log("\n恢复原始模板数据", "🔄")

        restore_data = {
            "name": "实际文件模板-片头片尾",
            "category": template.get('category', 'general'),
            "description": "使用实际OSS文件的视频模板：片头(start.mp4) + 主视频 + 片尾(start.mp4)",
            "is_advanced": True,
            "formatter_type": template.get('formatter_type', 'default'),
            "timeline_json": template.get('timeline_json', '{}'),
            "enable_subtitle": template.get('enable_subtitle', False),
            "subtitle_position": template.get('subtitle_position', 'bottom'),
            "subtitle_extract_audio": template.get('subtitle_extract_audio', False)
        }

        response = self.session.put(
            f"{BASE_URL}/api/video_templates/{self.template_id}",
            json=restore_data
        )

        if response.status_code == 200:
            self.log("✓ 原始数据已恢复", "✅")
            return True
        else:
            self.log("✗ 恢复失败", "❌")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("🧪 模板编辑功能自动化测试")
        print("=" * 70)

        results = []

        # 测试1: 加载页面
        results.append(("加载页面", self.test_load_page()))

        # 测试2: 获取模板列表
        results.append(("获取模板列表", self.test_get_templates_list()))

        # 测试3: 获取模板详情
        template = self.test_get_template_detail()
        results.append(("获取模板详情", template is not None))

        # 测试4: 编辑模板
        if template:
            edit_result = self.test_edit_template(template)
            results.append(("编辑模板", edit_result))

            # 测试5: 验证更新
            if edit_result:
                verify_result = self.test_verify_update()
                results.append(("验证更新", verify_result))

                # 恢复原始数据
                self.test_restore_template(template)
            else:
                results.append(("验证更新", False))
        else:
            results.append(("编辑模板", False))
            results.append(("验证更新", False))

        # 打印测试结果汇总
        print("\n" + "=" * 70)
        print("📊 测试结果汇总")
        print("=" * 70)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name:.<50} {status}")

        print("=" * 70)
        print(f"总计: {passed}/{total} 测试通过")
        print("=" * 70)

        return passed == total

if __name__ == "__main__":
    try:
        tester = TemplateEditTester()
        success = tester.run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
