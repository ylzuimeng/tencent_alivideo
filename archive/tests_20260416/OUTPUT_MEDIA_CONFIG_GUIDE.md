# OutputMediaConfig 配置指南

## 📋 概述

`OutputMediaConfig` 用于配置视频输出的参数，包括分辨率、码率、帧率、格式等。

## ✅ 测试结果

```
总测试数: 36
通过: 36 ✅
失败: 0 ❌
通过率: 100.0%
```

## 🎯 基础配置

### 最小配置

```json
{}
```
所有字段都是可选的，不配置时使用默认值。

### 标准配置（推荐）

```json
{
  "Width": 1280,
  "Height": 720
}
```

## 📺 分辨率配置

### 常用分辨率

| 名称 | 宽度 | 高度 | 适用场景 |
|------|------|------|---------|
| 480p | 640 | 480 | 移动端、快速预览 |
| 480p 宽屏 | 854 | 480 | 移动端宽屏 |
| 720p | 1280 | 720 | 标准高清（推荐） |
| 1080p | 1920 | 1080 | 全高清 |
| 1440p (2K) | 2560 | 1440 | 2K 视频 |
| 2160p (4K) | 3840 | 2160 | 4K 超高清 |

### 示例

```json
{
  "Width": 1280,
  "Height": 720
}
```

## 🔧 高级参数

### 完整配置示例

```json
{
  "Width": 1280,
  "Height": 720,
  "Bitrate": 2000,
  "Fps": 25,
  "Format": "mp4"
}
```

### 参数说明

| 参数 | 类型 | 范围 | 说明 | 默认值 |
|------|------|------|------|--------|
| Width | Integer | 240-3840 | 视频宽度（像素） | 原视频宽度 |
| Height | Integer | 240-2160 | 视频高度（像素） | 原视频高度 |
| Bitrate | Integer | 100-50000 | 视频码率（kbps） | 自动计算 |
| Fps | Number | 1-120 | 帧率（fps） | 原视频帧率 |
| Format | String | - | 输出格式 | mp4 |

### 支持的输出格式

- `mp4` - MP4 格式（推荐）
- `mov` - QuickTime 格式
- `flv` - Flash Video 格式
- `mkv` - Matroska 格式

## 🎬 真实场景配置

### 1. 医疗视频（项目中实际使用）

```json
{
  "Width": 1280,
  "Height": 720
}
```

**特点**: 标准清晰度，适合医疗健康宣教视频

### 2. 教育视频（高清）

```json
{
  "Width": 1920,
  "Height": 1080,
  "Bitrate": 3000,
  "Fps": 30
}
```

**特点**: 全高清，高码率，适合教育课程

### 3. 移动端优化

```json
{
  "Width": 854,
  "Height": 480,
  "Bitrate": 800,
  "Fps": 24
}
```

**特点**: 低分辨率，低码率，适合移动网络

### 4. 快速预览

```json
{
  "Width": 640,
  "Height": 360,
  "Bitrate": 500,
  "Fps": 15
}
```

**特点**: 低质量，快速生成，适合预览

## ⚠️ 边界限制

### 分辨率限制

- **最小宽度**: 240px
- **最大宽度**: 3840px
- **最小高度**: 240px
- **最大高度**: 2160px

### 码率限制

- **最小码率**: 100 kbps
- **最大码率**: 50000 kbps

### 帧率限制

- **最小帧率**: 1 fps
- **最大帧率**: 120 fps

## 🔍 配置验证

### 在 Python 中验证

```python
from services.json_validator import validate_output_media_config

# 验证配置
config_json = '''
{
  "Width": 1280,
  "Height": 720,
  "Bitrate": 2000
}
'''

is_valid, error_msg = validate_output_media_config(config_json)
if is_valid:
    print("✅ 配置有效")
else:
    print(f"❌ 配置无效: {error_msg}")
```

### 运行测试脚本

```bash
# 运行完整测试
python test_output_media_config.py

# 查看测试报告
cat output_media_config_test_report.json
```

## 💡 使用建议

### 1. 选择合适的分辨率

- **移动端/快速预览**: 480p (854x480)
- **标准应用**: 720p (1280x720) ⭐ 推荐
- **高质量需求**: 1080p (1920x1080)
- **专业制作**: 4K (3840x2160)

### 2. 设置合理的码率

| 分辨率 | 推荐码率 (kbps) | 说明 |
|--------|----------------|------|
| 480p | 800-1200 | 移动端优化 |
| 720p | 1500-2500 | 标准配置 |
| 1080p | 2500-5000 | 高清配置 |
| 4K | 10000-20000 | 超高清配置 |

### 3. 选择合适的帧率

- **15 fps**: 快速预览、低带宽
- **24 fps**: 电影效果
- **25 fps**: PAL 制式（中国、欧洲）
- **30 fps**: NTSC 制式（美国、日本）⭐ 推荐
- **60 fps**: 高帧率、流畅运动

### 4. 格式选择

- **MP4**: 通用性最好，推荐 ⭐
- **MOV**: Apple 设备兼容性好
- **FLV**: 旧版 Flash 播放器
- **MKV**: 开源格式，支持多轨

## 🚀 在项目中使用

### 创建模板时配置

```python
from models import VideoTemplate
import json

template = VideoTemplate(
    name='医疗视频模板',
    timeline_json='{"VideoTracks": [...]}',
    output_media_config=json.dumps({
        "Width": 1280,
        "Height": 720
    }),
    is_advanced=True
)
```

### 通过 API 配置

```bash
curl -X POST http://127.0.0.1:5000/api/video_templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试模板",
    "timeline_json": "{\"VideoTracks\": [{\"VideoTrackClips\": [{\"MediaURL\": \"$main_video\"}]}]}",
    "output_media_config": "{\"Width\": 1280, \"Height\": 720}",
    "is_advanced": true
  }'
```

## ❌ 常见错误

### 错误 1: 分辨率超出范围

```
❌ Schema验证失败: 3841 is greater than the maximum of 3840
```

**解决**: 确保 Width 在 240-3840 范围内

### 错误 2: 格式不支持

```
❌ Schema验证失败: 'avi' is not one of ['mp4', 'mov', 'flv', 'mkv']
```

**解决**: 使用支持的格式（mp4/mov/flv/mkv）

### 错误 3: 码率过低

```
❌ Schema验证失败: 99 is less than the minimum of 100
```

**解决**: 确保 Bitrate ≥ 100

## 📊 性能参考

### 不同配置的文件大小对比

假设视频时长 1 分钟：

| 配置 | 码率 (kbps) | 文件大小 (MB) | 适用场景 |
|------|-------------|---------------|---------|
| 快速预览 | 500 | ~3.75 MB | 预览、审核 |
| 移动端 | 800 | ~6 MB | 移动设备 |
| 标准 | 2000 | ~15 MB | 一般应用 |
| 高清 | 3000 | ~22.5 MB | 高质量需求 |
| 4K | 15000 | ~112.5 MB | 专业制作 |

## 🔗 相关文件

- `test_output_media_config.py` - 测试脚本
- `schemas/timeline_schemas.py` - Schema 定义
- `services/json_validator.py` - 验证服务
- `models.py` - 数据库模型

## 📚 参考文档

- [阿里云 IMS - 剪辑合成参数说明](https://help.aliyun.com/zh/ims/developer-reference/clip-composition-parameter-description)
