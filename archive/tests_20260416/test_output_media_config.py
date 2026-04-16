#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OutputMediaConfig 配置测试脚本

测试内容包括：
1. JSON Schema 格式验证
2. 各种分辨率配置
3. 完整参数配置
4. 无效配置检测
"""

import sys
import os
import json
from typing import Dict, List

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


class OutputMediaConfigTester:
    """OutputMediaConfig 配置测试类"""

    def __init__(self):
        """初始化测试器"""
        self.test_results = []
        self.passed = 0
        self.failed = 0

        # 导入验证器
        from services.json_validator import validate_output_media_config
        self.validate_config = validate_output_media_config

        print("=" * 70)
        print("🧪 OutputMediaConfig 配置测试")
        print("=" * 70)
        print()

    def test_case(self, name: str, config_json: str, should_pass: bool = True):
        """
        执行单个测试用例

        Args:
            name: 测试用例名称
            config_json: OutputMediaConfig JSON 字符串
            should_pass: 是否应该通过验证
        """
        print(f"测试: {name}")
        is_valid, error_msg = self.validate_config(config_json)

        if should_pass:
            if is_valid:
                print(f"  ✅ 通过 - 配置格式正确")
                self.passed += 1
                self.test_results.append({
                    'name': name,
                    'status': 'PASS',
                    'message': '格式正确'
                })
            else:
                print(f"  ❌ 失败 - 预期通过但验证失败")
                print(f"     错误: {error_msg}")
                self.failed += 1
                self.test_results.append({
                    'name': name,
                    'status': 'FAIL',
                    'message': error_msg
                })
        else:
            if not is_valid:
                print(f"  ✅ 通过 - 正确识别了无效配置")
                print(f"     错误信息: {error_msg}")
                self.passed += 1
                self.test_results.append({
                    'name': name,
                    'status': 'PASS',
                    'message': f'正确识别错误: {error_msg}'
                })
            else:
                print(f"  ❌ 失败 - 预期失败但验证通过")
                self.failed += 1
                self.test_results.append({
                    'name': name,
                    'status': 'FAIL',
                    'message': '应该验证失败但通过了'
                })
        print()

    def run_basic_tests(self):
        """运行基础配置测试"""
        print("=" * 70)
        print("📋 第一部分: 基础配置验证")
        print("=" * 70)
        print()

        # 测试 1: 最小配置（空配置也有效）
        self.test_case(
            "空配置（可选字段）",
            json.dumps({}, ensure_ascii=False),
            should_pass=True
        )

        # 测试 2: 仅配置分辨率
        self.test_case(
            "仅配置分辨率",
            json.dumps({
                "Width": 1280,
                "Height": 720
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 3: 720p 配置
        self.test_case(
            "720p 标准配置",
            json.dumps({
                "Width": 1280,
                "Height": 720
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 4: 1080p 配置
        self.test_case(
            "1080p 标准配置",
            json.dumps({
                "Width": 1920,
                "Height": 1080
            }, ensure_ascii=False),
            should_pass=True
        )

    def run_resolution_tests(self):
        """运行分辨率配置测试"""
        print("=" * 70)
        print("📋 第二部分: 分辨率配置测试")
        print("=" * 70)
        print()

        # 常用分辨率
        resolutions = [
            ("480p", 640, 480),
            ("480p 宽屏", 854, 480),
            ("720p", 1280, 720),
            ("1080p", 1920, 1080),
            ("1440p (2K)", 2560, 1440),
            ("2160p (4K)", 3840, 2160),
        ]

        for name, width, height in resolutions:
            self.test_case(
                f"{name} 分辨率配置",
                json.dumps({
                    "Width": width,
                    "Height": height
                }, ensure_ascii=False),
                should_pass=True
            )

    def run_advanced_tests(self):
        """运行高级参数测试"""
        print("=" * 70)
        print("📋 第三部分: 高级参数配置")
        print("=" * 70)
        print()

        # 测试 1: 完整配置
        self.test_case(
            "完整配置（所有参数）",
            json.dumps({
                "Width": 1280,
                "Height": 720,
                "Bitrate": 2000,
                "Fps": 25,
                "Format": "mp4"
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 2: 带码率配置
        self.test_case(
            "720p + 码率配置",
            json.dumps({
                "Width": 1280,
                "Height": 720,
                "Bitrate": 2000
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 3: 带帧率配置
        self.test_case(
            "720p + 帧率配置",
            json.dumps({
                "Width": 1280,
                "Height": 720,
                "Fps": 30
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 4: 不同格式
        formats = ["mp4", "mov", "flv", "mkv"]
        for fmt in formats:
            self.test_case(
                f"{fmt.upper()} 格式配置",
                json.dumps({
                    "Width": 1280,
                    "Height": 720,
                    "Format": fmt
                }, ensure_ascii=False),
                should_pass=True
            )

    def run_boundary_tests(self):
        """运行边界值测试"""
        print("=" * 70)
        print("📋 第四部分: 边界值测试")
        print("=" * 70)
        print()

        # 测试 1: 最小宽度
        self.test_case(
            "最小宽度 (240px)",
            json.dumps({
                "Width": 240,
                "Height": 240
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 2: 最大宽度
        self.test_case(
            "最大宽度 (3840px)",
            json.dumps({
                "Width": 3840,
                "Height": 2160
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 3: 最小高度
        self.test_case(
            "最小高度 (240px)",
            json.dumps({
                "Width": 240,
                "Height": 240
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 4: 最大高度
        self.test_case(
            "最大高度 (2160px)",
            json.dumps({
                "Width": 3840,
                "Height": 2160
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 5: 宽度超出范围（应该失败）
        self.test_case(
            "宽度超出范围 (3841px)",
            json.dumps({
                "Width": 3841,
                "Height": 2160
            }, ensure_ascii=False),
            should_pass=False
        )

        # 测试 6: 高度超出范围（应该失败）
        self.test_case(
            "高度超出范围 (2161px)",
            json.dumps({
                "Width": 3840,
                "Height": 2161
            }, ensure_ascii=False),
            should_pass=False
        )

        # 测试 7: 最小码率
        self.test_case(
            "最小码率 (100 kbps)",
            json.dumps({
                "Width": 1280,
                "Height": 720,
                "Bitrate": 100
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 8: 最大码率
        self.test_case(
            "最大码率 (50000 kbps)",
            json.dumps({
                "Width": 1280,
                "Height": 720,
                "Bitrate": 50000
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 9: 最小帧率
        self.test_case(
            "最小帧率 (1 fps)",
            json.dumps({
                "Width": 1280,
                "Height": 720,
                "Fps": 1
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 10: 最大帧率
        self.test_case(
            "最大帧率 (120 fps)",
            json.dumps({
                "Width": 1280,
                "Height": 720,
                "Fps": 120
            }, ensure_ascii=False),
            should_pass=True
        )

    def run_invalid_tests(self):
        """运行无效配置测试"""
        print("=" * 70)
        print("📋 第五部分: 无效配置检测")
        print("=" * 70)
        print()

        # 测试 1: 宽度为负数（应该失败）
        self.test_case(
            "宽度为负数",
            json.dumps({
                "Width": -1280,
                "Height": 720
            }, ensure_ascii=False),
            should_pass=False
        )

        # 测试 2: 高度为负数（应该失败）
        self.test_case(
            "高度为负数",
            json.dumps({
                "Width": 1280,
                "Height": -720
            }, ensure_ascii=False),
            should_pass=False
        )

        # 测试 3: 无效格式（应该失败）
        self.test_case(
            "无效的视频格式",
            json.dumps({
                "Width": 1280,
                "Height": 720,
                "Format": "avi"
            }, ensure_ascii=False),
            should_pass=False
        )

        # 测试 4: 码率过低（应该失败）
        self.test_case(
            "码率过低 (99 kbps)",
            json.dumps({
                "Width": 1280,
                "Height": 720,
                "Bitrate": 99
            }, ensure_ascii=False),
            should_pass=False
        )

        # 测试 5: 帧率过低（应该失败）
        self.test_case(
            "帧率过低 (0.5 fps)",
            json.dumps({
                "Width": 1280,
                "Height": 720,
                "Fps": 0.5
            }, ensure_ascii=False),
            should_pass=False
        )

    def test_real_world_configs(self):
        """测试真实场景配置"""
        print("=" * 70)
        print("📋 第六部分: 真实场景配置")
        print("=" * 70)
        print()

        # 测试 1: 医疗视频配置（项目中实际使用）
        self.test_case(
            "医疗视频标准配置",
            json.dumps({
                "Width": 1280,
                "Height": 720
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 2: 教育视频配置
        self.test_case(
            "教育视频高清配置",
            json.dumps({
                "Width": 1920,
                "Height": 1080,
                "Bitrate": 3000,
                "Fps": 30
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 3: 移动端优化配置
        self.test_case(
            "移动端低码率配置",
            json.dumps({
                "Width": 854,
                "Height": 480,
                "Bitrate": 800,
                "Fps": 24
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 4: 快速预览配置
        self.test_case(
            "快速预览低质量配置",
            json.dumps({
                "Width": 640,
                "Height": 360,
                "Bitrate": 500,
                "Fps": 15
            }, ensure_ascii=False),
            should_pass=True
        )

    def print_summary(self):
        """打印测试总结"""
        print("=" * 70)
        print("📊 测试总结")
        print("=" * 70)
        print()

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"总测试数: {total}")
        print(f"通过: {self.passed} ✅")
        print(f"失败: {self.failed} ❌")
        print(f"通过率: {pass_rate:.1f}%")
        print()

        if self.failed > 0:
            print("失败的测试:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  ❌ {result['name']}")
                    print(f"     {result['message']}")
            print()

        # 保存测试报告
        from datetime import datetime
        report = {
            'timestamp': datetime.now().isoformat(),
            'total': total,
            'passed': self.passed,
            'failed': self.failed,
            'pass_rate': f"{pass_rate:.1f}%",
            'results': self.test_results
        }

        report_file = 'output_media_config_test_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📄 详细测试报告已保存至: {report_file}")
        print()

        if pass_rate == 100:
            print("🎉 所有测试通过！OutputMediaConfig 配置功能正常！")
        elif pass_rate >= 80:
            print("⚠️  大部分测试通过，但有少量失败，请检查上述错误。")
        else:
            print("❌ 测试失败率较高，请检查配置和验证逻辑。")

        print("=" * 70)

    def run_all_tests(self):
        """运行所有测试"""
        try:
            self.run_basic_tests()
            self.run_resolution_tests()
            self.run_advanced_tests()
            self.run_boundary_tests()
            self.run_invalid_tests()
            self.test_real_world_configs()
            self.print_summary()
        except Exception as e:
            print(f"\n❌ 测试执行异常: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    tester = OutputMediaConfigTester()
    tester.run_all_tests()

    # 返回退出码
    return 0 if tester.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
