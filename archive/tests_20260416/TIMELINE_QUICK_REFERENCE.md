# Timeline 配置快速参考

## AI_ASR 自动字幕配置

### 最小配置（推荐新手）

```json
{
  "VideoTracks": [{
    "VideoTrackClips": [{
      "MediaURL": "$main_video",
      "MainTrack": true,
      "Effects": [{
        "Type": "AI_ASR"
      }]
    }]
  }]
}
```

### 推荐配置（医疗场景）

```json
{
  "VideoTracks": [{
    "VideoTrackClips": [{
      "MediaURL": "$main_video",
      "MainTrack": true,
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
}
```

### AI_ASR 参数说明

| 参数 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| Type | String | 固定值 "AI_ASR" | "AI_ASR" |
| Font | String | 字体名称 | "AlibabaPuHuiTi", "SimHei" |
| FontSize | Integer | 字号（8-5000） | 60 |
| FontColor | String | 字体颜色（16进制） | "#000079" |
| Alignment | String | 对齐方式 | "BottomCenter", "TopCenter" |
| Y | Integer | 垂直位置（像素） | 600 |
| Outline | Integer | 描边宽度 | 10 |
| OutlineColour | String | 描边颜色 | "#ffffff" |

## SubtitleTracks 自定义字幕

### 基础文本字幕

```json
{
  "VideoTracks": [{
    "VideoTrackClips": [{
      "MediaURL": "$main_video",
      "MainTrack": true
    }]
  }],
  "SubtitleTracks": [{
    "SubtitleTrackClips": [{
      "Type": "Text",
      "Content": "这是字幕内容",
      "X": 80,
      "Y": 100,
      "FontSize": 45,
      "FontColor": "#ffffff"
    }]
  }]
}
```

### 使用占位符

```json
{
  "VideoTracks": [{
    "VideoTrackClips": [{
      "MediaURL": "$main_video",
      "MainTrack": true
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
}
```

### 支持的占位符

| 占位符 | 说明 | 示例 |
|--------|------|------|
| $main_video | 主视频 URL | https://oss.com/video.mp4 |
| $mainSubtitleDepart | 医院+科室（自动竖排） | 青岛\n大学\n附属\n医院 |
| $mainSubtitleName | 医生姓名+职称（自动竖排） | 张\n医\n生 |
| $beginingSubtitleTitle | 视频标题 | 高血压健康宣教 |
| $beginingAudioTitle | TTS 语音内容 | 高血压健康宣教 |

## 完整医疗模板

### 片头 + 主视频 + AI_ASR + 自定义字幕

```json
{
  "VideoTracks": [{
    "VideoTrackClips": [
      {
        "MediaURL": "https://oss.example.com/intro.mp4",
        "Duration": 3
      },
      {
        "MediaURL": "$main_video",
        "MainTrack": true,
        "ClipId": "main-2",
        "Effects": [{
          "Type": "AI_ASR",
          "Font": "AlibabaPuHuiTi",
          "FontSize": 60,
          "FontColor": "#000079",
          "Alignment": "BottomCenter",
          "Y": 600
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
  }]
}
```

## 外挂字幕文件

### SRT 字幕

```json
{
  "VideoTracks": [{
    "VideoTrackClips": [{
      "MediaURL": "$main_video",
      "MainTrack": true
    }]
  }],
  "SubtitleTracks": [{
    "SubtitleTrackClips": [{
      "Type": "Subtitle",
      "SubType": "srt",
      "FileURL": "https://oss.example.com/subtitle.srt"
    }]
  }]
}
```

### ASS 字幕

```json
{
  "VideoTracks": [{
    "VideoTrackClips": [{
      "MediaURL": "$main_video",
      "MainTrack": true
    }]
  }],
  "SubtitleTracks": [{
    "SubtitleTrackClips": [{
      "Type": "Subtitle",
      "SubType": "ass",
      "FileURL": "https://oss.example.com/subtitle.ass"
    }]
  }]
}
```

## 常用字体列表

| 中文名称 | 英文名称 | 适用场景 |
|---------|---------|---------|
| 阿里巴巴普惠体 | AlibabaPuHuiTi | 推荐，AI_ASR 默认 |
| 黑体 | SimHei | 通用，清晰 |
| 宋体 | SimSun | 正式，传统 |
| 微软雅黑 | Microsoft YaHei | 现代，易读 |
| 思源黑体 | SiYuan Heiti | 设计感 |

## 颜色参考

| 用途 | 颜色代码 | 说明 |
|------|---------|------|
| 白色 | #FFFFFF | 通用 |
| 黑色 | #000000 | 深色背景 |
| 深蓝色 | #000079 | 医疗场景推荐 |
| 红色 | #FF0000 | 警告、强调 |
| 黄色 | #FFFF00 | 高亮 |

## 对齐方式

| 值 | 说明 |
|---|---|
| TopLeft | 左上角 |
| TopCenter | 顶部居中 |
| TopRight | 右上角 |
| CenterLeft | 左侧居中 |
| CenterCenter | 正中心 |
| CenterRight | 右侧居中 |
| BottomLeft | 左下角 |
| BottomCenter | 底部居中 |
| BottomRight | 右下角 |

## 快速测试

### 测试 Timeline 格式

```bash
# 方式 1: 运行测试脚本
python test_timeline_validation.py

# 方式 2: 运行演示
python test_timeline_demo.py

# 方式 3: 在 Python 中测试
python -c "from services.json_validator import validate_timeline_json; print(validate_timeline_json('{\"VideoTracks\": [{\"VideoTrackClips\": [{\"MediaURL\": \"test\"}]}]}'))"
```

### 在线验证

访问阿里云 API Explorer：
https://api.aliyun.com/api/ICE/2020-11-09/CreateEditingProject

## 常见错误

### 错误 1: 缺少 MediaURL
```
❌ Schema验证失败: 'MediaURL' is a required property
```
**解决**: 确保 VideoTrackClips 中每个元素都有 MediaURL

### 错误 2: VideoTrackClips 为空
```
❌ Schema验证失败: [] should be non-empty
```
**解决**: VideoTrackClips 数组不能为空

### 错误 3: 缺少 VideoTracks
```
❌ Schema验证失败: 'VideoTracks' is a required property
```
**解决**: Timeline 必须包含 VideoTracks 字段

## 相关文件

- `test_timeline_validation.py` - 完整测试脚本
- `test_timeline_demo.py` - 演示脚本
- `TIMELINE_TEST_GUIDE.md` - 详细使用指南
- `schemas/timeline_schemas.py` - Schema 定义

## 参考文档

- [阿里云 IMS Timeline 配置说明](https://help.aliyun.com/zh/ims/developer-reference/timeline-configuration-description)
- [通过 Timeline 参数为视频添加和自定义字幕](https://help.aliyun.com/zh/ims/use-cases/subtitles-and-subtitle-templates)
