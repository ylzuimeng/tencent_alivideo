#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化医疗健康宣教视频模板

从 ali_ice_timeline_template.md 创建默认的医疗模板
"""
import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, VideoTemplate


def create_medical_template():
    """创建医疗健康宣教视频模板"""

    with app.app_context():
        # 检查是否已存在
        existing = VideoTemplate.query.filter_by(name='医疗健康宣教视频模板').first()
        if existing:
            print(f"✅ 模板已存在: {existing.name} (ID: {existing.id})")
            print(f"   如需重新创建，请先删除现有模板")
            return

        # Timeline模板（来自文档）
        timeline = {
            "VideoTracks": [
                {
                    "VideoTrackClips": [
                        {
                            "MediaURL": "https://your-oss.oss-cn-shanghai.aliyuncs.com/intro.mp4",
                            "AdaptMode": "Cover",
                            "Width": 1,
                            "Height": 1
                        },
                        {
                            "Type": "Image",
                            "MediaURL": "https://your-oss.oss-cn-shanghai.aliyuncs.com/transition.png",
                            "AdaptMode": "Cover",
                            "Width": 1,
                            "Height": 1,
                            "Duration": 2,
                            "ClipId": "transition-1"
                        },
                        {
                            "MediaURL": "$main_video",
                            "MainTrack": True,
                            "AdaptMode": "Contain",
                            "ClipId": "main-2",
                            "Effects": [
                                {
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
                                }
                            ]
                        }
                    ]
                }
            ],
            "SubtitleTracks": [
                {
                    "SubtitleTrackClips": [
                        {
                            "Type": "Text",
                            "X": 80,
                            "Y": 100,
                            "Content": "$mainSubtitleDepart",
                            "LineSpacing": -5,
                            "FontSize": 45,
                            "FontColorOpacity": 1,
                            "EffectColorStyle": "SiYuan Heiti",
                            "ReferenceClipId": "main-2",
                            "FontFace": {
                                "Bold": True
                            },
                            "SubtitleEffects": [
                                {
                                    "Type": "Box",
                                    "ImageUrl": "https://your-oss.oss-cn-shanghai.aliyuncs.com/hospital_bg.png",
                                    "XShift": -6,
                                    "YBord": 20
                                }
                            ]
                        },
                        {
                            "Type": "Text",
                            "X": 140,
                            "Y": 150,
                            "Content": "$mainSubtitleName",
                            "LineSpacing": -5,
                            "FontSize": 38,
                            "FontColorOpacity": 1,
                            "EffectColorStyle": "SiYuan Heiti",
                            "ReferenceClipId": "main-2",
                            "FontFace": {
                                "Bold": True
                            },
                            "SubtitleEffects": [
                                {
                                    "Type": "Box",
                                    "ImageUrl": "https://your-oss.oss-cn-shanghai.aliyuncs.com/doctor_bg.png",
                                    "XShift": -6,
                                    "YBord": 40,
                                    "XBord": 8
                                },
                                {
                                    "Type": "Outline",
                                    "Bord": 2,
                                    "Color": "#325ad7"
                                }
                            ]
                        },
                        {
                            "Type": "Text",
                            "X": 640,
                            "Y": 100,
                            "Content": "$beginingSubtitleTitle",
                            "Alignment": "TopCenter",
                            "FontSize": 50,
                            "FontColor": "#ffffff",
                            "FontFace": {
                                "Bold": True
                            },
                            "SubtitleEffects": [
                                {
                                    "Type": "Box",
                                    "Color": "0x000000AA",
                                    "YBord": 30,
                                    "XBord": 40
                                }
                            ]
                        }
                    ]
                }
            ],
            "AudioTracks": [
                {
                    "AudioTrackClips": [
                        {
                            "Type": "AI_TTS",
                            "Content": "$beginingAudioTitle",
                            "Voice": "zhimi_emo",
                            "TimelineIn": 3,
                            "TimelineOut": 8
                        }
                    ]
                }
            ]
        }

        # 输出配置
        output_media_config = {
            "mediaURL": "http://your-oss.oss-cn-shanghai.aliyuncs.com/ice/$videoId_video.mp4",
            "Width": 1280,
            "Height": 720
        }

        # 制作配置
        editing_produce_config = {
            "CoverConfig": {
                "StartTime": 2.8
            }
        }

        # 创建模板
        template = VideoTemplate(
            name='医疗健康宣教视频模板',
            description='完整的医疗健康宣教视频制作模板，支持片头、过渡、主视频、医生信息叠加、AI字幕和AI语音。使用前请修改Timeline中的OSS URL为您自己的资源地址。',
            timeline_json=json.dumps(timeline, ensure_ascii=False),
            output_media_config=json.dumps(output_media_config, ensure_ascii=False),
            editing_produce_config=json.dumps(editing_produce_config, ensure_ascii=False),
            formatter_type='default',
            category='medical',
            is_advanced=True,
            thumbnail_url=''  # 可以添加缩略图URL
        )

        db.session.add(template)
        db.session.commit()

        print("=" * 70)
        print("✅ 医疗健康宣教视频模板创建成功!")
        print("=" * 70)
        print(f"   ID: {template.id}")
        print(f"   名称: {template.name}")
        print(f"   分类: {template.category}")
        print(f"   格式化器: {template.formatter_type}")
        print()
        print("📋 支持的占位符:")
        print("   • $main_video          - 主视频URL")
        print("   • $mainSubtitleDepart  - 医院名称+科室（自动竖排）")
        print("   • $mainSubtitleName    - 医生姓名+职称（自动竖排）")
        print("   • $beginingSubtitleTitle - 视频标题（字幕）")
        print("   • $beginingAudioTitle  - 视频标题（TTS语音）")
        print()
        print("📝 使用前注意事项:")
        print("   1. 修改Timeline中的OSS资源URL为您自己的资源地址")
        print("   2. 确保片头视频、过渡图片、背景图片等资源已上传到OSS")
        print("   3. 创建任务时需要提供医生信息和主视频URL")
        print("=" * 70)


if __name__ == '__main__':
    create_medical_template()
