#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
打印 OutputMediaConfig 配置
"""

import json

# 常用配置
configs = {
    "720p 标准配置（推荐）": {
        "Width": 1280,
        "Height": 720
    },
    "1080p 高清配置": {
        "Width": 1920,
        "Height": 1080
    },
    "完整配置": {
        "Width": 1280,
        "Height": 720,
        "Bitrate": 2000,
        "Fps": 30,
        "Format": "mp4"
    },
    "移动端优化": {
        "Width": 854,
        "Height": 480,
        "Bitrate": 800,
        "Fps": 24
    },
    "快速预览": {
        "Width": 640,
        "Height": 360,
        "Bitrate": 500,
        "Fps": 15
    },
    "4K 超高清": {
        "Width": 3840,
        "Height": 2160,
        "Bitrate": 15000,
        "Fps": 30
    }
}

print("=" * 70)
print("📋 OutputMediaConfig 配置清单")
print("=" * 70)
print()

for name, config in configs.items():
    print(f"🎯 {name}")
    print("-" * 70)
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print()

print("=" * 70)
print("✅ 配置打印完成！")
print("=" * 70)
