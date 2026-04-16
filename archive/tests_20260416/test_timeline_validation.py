#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Timeline 功能测试脚本

测试内容包括：
1. JSON Schema 格式验证
2. 各种 Timeline 配置场景
3. AI_ASR 字幕功能
4. SubtitleTracks 自定义字幕
5. 阿里云 ICE API 集成测试
"""

import sys
import os
import json
from typing import Dict, List, Tuple
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


class TimelineTester:
    """Timeline 功能测试类"""

    def __init__(self):
        """初始化测试器"""
        self.test_results = []
        self.passed = 0
        self.failed = 0

        # 导入验证器
        from services.json_validator import validate_timeline_json
        self.validate_timeline = validate_timeline_json

        print("=" * 70)
        print("🧪 Timeline 功能测试")
        print("=" * 70)
        print()

    def test_case(self, name: str, timeline_json: str, should_pass: bool = True):
        """
        执行单个测试用例

        Args:
            name: 测试用例名称
            timeline_json: Timeline JSON 字符串
            should_pass: 是否应该通过验证
        """
        print(f"测试: {name}")
        is_valid, error_msg = self.validate_timeline(timeline_json)

        if should_pass:
            if is_valid:
                print(f"  ✅ 通过 - Timeline 格式正确")
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
                print(f"  ✅ 通过 - 正确识别了无效格式")
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
        """运行基础格式测试"""
        print("=" * 70)
        print("📋 第一部分: 基础格式验证")
        print("=" * 70)
        print()

        # 测试 1: 最简单的有效 Timeline
        self.test_case(
            "最简单的有效 Timeline",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [{
                        "MediaURL": "$main_video"
                    }]
                }]
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 2: 包含 HTTP URL 的 Timeline
        self.test_case(
            "包含 HTTP URL 的 Timeline",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [{
                        "MediaURL": "https://oss.example.com/video.mp4"
                    }]
                }]
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 3: 缺少 VideoTracks（应该失败）
        self.test_case(
            "缺少 VideoTracks 的 Timeline",
            json.dumps({
                "AudioTracks": []
            }, ensure_ascii=False),
            should_pass=False
        )

        # 测试 4: VideoTrackClips 为空（应该失败）
        self.test_case(
            "VideoTrackClips 为空的 Timeline",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": []
                }]
            }, ensure_ascii=False),
            should_pass=False
        )

        # 测试 5: 缺少 MediaURL（应该失败）
        self.test_case(
            "缺少 MediaURL 的 Timeline",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [{
                        "MainTrack": True
                    }]
                }]
            }, ensure_ascii=False),
            should_pass=False
        )

    def run_ai_asr_tests(self):
        """运行 AI_ASR 字幕测试"""
        print("=" * 70)
        print("📋 第二部分: AI_ASR 自动字幕功能")
        print("=" * 70)
        print()

        # 测试 1: 基础 AI_ASR 配置
        self.test_case(
            "基础 AI_ASR 字幕配置",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [{
                        "MediaURL": "$main_video",
                        "MainTrack": True,
                        "Effects": [{
                            "Type": "AI_ASR",
                            "Font": "AlibabaPuHuiTi",
                            "FontSize": 60,
                            "FontColor": "#000079",
                            "Alignment": "BottomCenter",
                            "Y": 600,
                            "Outline": 10,
                            "OutlineColour": "#ffffff"
                        }]
                    }]
                }]
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 2: AI_ASR 最小配置
        self.test_case(
            "AI_ASR 最小配置（仅必需参数）",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [{
                        "MediaURL": "$main_video",
                        "Effects": [{
                            "Type": "AI_ASR"
                        }]
                    }]
                }]
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 3: 完整的医疗场景 AI_ASR
        self.test_case(
            "完整医疗场景 AI_ASR 配置",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [
                        {
                            "MediaURL": "https://oss.example.com/intro.mp4",
                            "Duration": 3
                        },
                        {
                            "MediaURL": "$main_video",
                            "MainTrack": True,
                            "ClipId": "main-2",
                            "Effects": [{
                                "Type": "AI_ASR",
                                "Font": "AlibabaPuHuiTi",
                                "Alignment": "TopCenter",
                                "Y": 600,
                                "Outline": 10,
                                "OutlineColour": "#ffffff",
                                "FontSize": 60,
                                "FontColor": "#000079",
                                "FontFace": {
                                    "Bold": True,
                                    "Italic": False,
                                    "Underline": False
                                }
                            }]
                        }
                    ]
                }]
            }, ensure_ascii=False),
            should_pass=True
        )

    def run_subtitle_tracks_tests(self):
        """运行 SubtitleTracks 自定义字幕测试"""
        print("=" * 70)
        print("📋 第三部分: SubtitleTracks 自定义字幕")
        print("=" * 70)
        print()

        # 测试 1: 基础文本字幕
        self.test_case(
            "基础文本字幕配置",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [{
                        "MediaURL": "$main_video",
                        "MainTrack": True,
                        "ClipId": "main-video"
                    }]
                }],
                "SubtitleTracks": [{
                    "SubtitleTrackClips": [{
                        "Type": "Text",
                        "Content": "这是字幕内容",
                        "X": 80,
                        "Y": 100,
                        "FontSize": 45,
                        "FontColor": "#ffffff",
                        "TimelineIn": 0,
                        "TimelineOut": 5
                    }]
                }]
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 2: 使用占位符的字幕
        self.test_case(
            "使用占位符的字幕配置",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [{
                        "MediaURL": "$main_video",
                        "MainTrack": True
                    }]
                }],
                "SubtitleTracks": [{
                    "SubtitleTrackClips": [
                        {
                            "Type": "Text",
                            "Content": "$mainSubtitleDepart",
                            "X": 80,
                            "Y": 100,
                            "FontSize": 45
                        },
                        {
                            "Type": "Text",
                            "Content": "$mainSubtitleName",
                            "X": 140,
                            "Y": 150,
                            "FontSize": 38
                        }
                    ]
                }]
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 3: 字幕带参考剪辑
        self.test_case(
            "字幕带 ReferenceClipId",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [{
                        "MediaURL": "$main_video",
                        "MainTrack": True,
                        "ClipId": "main-video"
                    }]
                }],
                "SubtitleTracks": [{
                    "SubtitleTrackClips": [{
                        "Type": "Text",
                        "Content": "对齐字幕",
                        "ReferenceClipId": "main-video"
                    }]
                }]
            }, ensure_ascii=False),
            should_pass=True
        )

    def run_complex_scenarios(self):
        """运行复杂场景测试"""
        print("=" * 70)
        print("📋 第四部分: 复杂场景测试")
        print("=" * 70)
        print()

        # 测试 1: 完整的医疗模板（片头+主视频+片尾+字幕）
        self.test_case(
            "完整医疗模板配置",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [
                        {
                            "MediaURL": "https://oss.example.com/intro.mp4",
                            "Duration": 3
                        },
                        {
                            "Type": "Image",
                            "MediaURL": "https://oss.example.com/transition.png",
                            "Duration": 2,
                            "ClipId": "transition-1"
                        },
                        {
                            "MediaURL": "$main_video",
                            "MainTrack": True,
                            "ClipId": "main-2",
                            "Effects": [{
                                "Type": "AI_ASR",
                                "Font": "AlibabaPuHuiTi",
                                "Alignment": "TopCenter",
                                "Y": 600,
                                "FontSize": 60
                            }]
                        }
                    ]
                }],
                "SubtitleTracks": [{
                    "SubtitleTrackClips": [
                        {
                            "Type": "Text",
                            "X": 80,
                            "Y": 100,
                            "Content": "$mainSubtitleDepart",
                            "FontSize": 45,
                            "ReferenceClipId": "main-2"
                        },
                        {
                            "Type": "Text",
                            "X": 640,
                            "Y": 100,
                            "Content": "$beginingSubtitleTitle",
                            "Alignment": "TopCenter",
                            "FontSize": 50
                        }
                    ]
                }],
                "AudioTracks": [{
                    "AudioTrackClips": [{
                        "Type": "AI_TTS",
                        "Content": "$beginingAudioTitle",
                        "Voice": "zhimi_emo",
                        "TimelineIn": 3,
                        "TimelineOut": 8
                    }]
                }]
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 2: 多轨道字幕
        self.test_case(
            "多轨道字幕配置",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [{
                        "MediaURL": "$main_video",
                        "MainTrack": True
                    }]
                }],
                "SubtitleTracks": [
                    {
                        "SubtitleTrackClips": [{
                            "Type": "Text",
                            "Content": "第一条字幕",
                            "X": 100,
                            "Y": 100,
                            "FontSize": 40
                        }]
                    },
                    {
                        "SubtitleTrackClips": [{
                            "Type": "Text",
                            "Content": "第二条字幕",
                            "X": 100,
                            "Y": 200,
                            "FontSize": 40
                        }]
                    }
                ]
            }, ensure_ascii=False),
            should_pass=True
        )

        # 测试 3: 带特效的视频
        self.test_case(
            "带多种特效的视频配置",
            json.dumps({
                "VideoTracks": [{
                    "VideoTrackClips": [{
                        "MediaURL": "$main_video",
                        "MainTrack": True,
                        "Effects": [
                            {
                                "Type": "AI_ASR",
                                "Font": "SimHei",
                                "FontSize": 50
                            },
                            {
                                "Type": "Volume",
                                "Value": 0.5
                            }
                        ]
                    }]
                }]
            }, ensure_ascii=False),
            should_pass=True
        )

    def test_placeholder_replacement(self):
        """测试占位符替换功能"""
        print("=" * 70)
        print("📋 第五部分: 占位符替换测试")
        print("=" * 70)
        print()

        from services.timeline_formatter import DefaultTimelineFormatter

        formatter = DefaultTimelineFormatter()

        # 测试数据
        test_timeline = json.dumps({
            "VideoTracks": [{
                "VideoTrackClips": [{
                    "MediaURL": "$main_video",
                    "MainTrack": True
                }]
            }],
            "SubtitleTracks": [{
                "SubtitleTrackClips": [{
                    "Type": "Text",
                    "Content": "$mainSubtitleDepart"
                }]
            }]
        }, ensure_ascii=False)

        test_data = {
            'main_video_url': 'https://oss.example.com/video.mp4',
            'hospital': '青岛大学附属医院',
            'department': '心内科',
            'name': '张医生',
            'title': '主任医师',
            'video_title': '高血压健康宣教'
        }

        try:
            result = formatter.format(test_timeline, test_data)

            # 验证替换结果
            if 'https://oss.example.com/video.mp4' in result:
                print("✅ 主视频 URL 替换成功")
                self.passed += 1
            else:
                print("❌ 主视频 URL 替换失败")
                self.failed += 1

            # 验证竖排文本
            if '青\\n岛\\n大\\n学' in result:
                print("✅ 医院名称竖排转换成功")
                self.passed += 1
            else:
                print("❌ 医院名称竖排转换失败")
                self.failed += 1

            # 验证 JSON 格式
            json.loads(result)
            print("✅ 替换后的 JSON 格式有效")
            self.passed += 1

        except Exception as e:
            print(f"❌ 占位符替换失败: {str(e)}")
            self.failed += 1

        print()

    def test_ice_api_integration(self):
        """测试阿里云 ICE API 集成"""
        print("=" * 70)
        print("📋 第六部分: 阿里云 ICE API 集成测试")
        print("=" * 70)
        print()

        try:
            from services.ice_service import create_ice_client

            print("创建 ICE 客户端...")
            client = create_ice_client()
            print("✅ ICE 客户端创建成功")
            self.passed += 1

            # 测试 Timeline 生成方法
            print("\n测试 Timeline 生成方法...")

            # 创建模拟 VideoTemplate
            class MockTemplate:
                def __init__(self):
                    self.name = "测试模板"
                    self.timeline_json = json.dumps({
                        "VideoTracks": [{
                            "VideoTrackClips": [{
                                "MediaURL": "$main_video",
                                "MainTrack": True
                            }]
                        }]
                    }, ensure_ascii=False)

            template = MockTemplate()

            try:
                timeline = client.create_timeline_from_advanced_template(
                    template,
                    "https://oss.example.com/video.mp4",
                    None
                )
                print("✅ Timeline 生成成功")
                print(f"   生成的 Timeline: {timeline[:100]}...")
                self.passed += 1
            except Exception as e:
                print(f"❌ Timeline 生成失败: {str(e)}")
                self.failed += 1

        except ImportError as e:
            print(f"⚠️  ICE 服务模块未导入: {str(e)}")
            print("   （这是正常的，如果未配置阿里云凭证）")
        except Exception as e:
            print(f"❌ ICE API 测试失败: {str(e)}")
            self.failed += 1

        print()

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
        report = {
            'timestamp': datetime.now().isoformat(),
            'total': total,
            'passed': self.passed,
            'failed': self.failed,
            'pass_rate': f"{pass_rate:.1f}%",
            'results': self.test_results
        }

        report_file = 'timeline_test_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📄 详细测试报告已保存至: {report_file}")
        print()

        if pass_rate == 100:
            print("🎉 所有测试通过！Timeline 功能正常！")
        elif pass_rate >= 80:
            print("⚠️  大部分测试通过，但有少量失败，请检查上述错误。")
        else:
            print("❌ 测试失败率较高，请检查 Timeline 配置和验证逻辑。")

        print("=" * 70)

    def run_all_tests(self):
        """运行所有测试"""
        try:
            self.run_basic_tests()
            self.run_ai_asr_tests()
            self.run_subtitle_tracks_tests()
            self.run_complex_scenarios()
            self.test_placeholder_replacement()
            self.test_ice_api_integration()
            self.print_summary()
        except Exception as e:
            print(f"\n❌ 测试执行异常: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    tester = TimelineTester()
    tester.run_all_tests()

    # 返回退出码
    return 0 if tester.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
