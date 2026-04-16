# Timeline 功能测试脚本使用指南

## 概述

`test_timeline_validation.py` 是一个综合测试脚本，用于验证 Timeline JSON 格式的有效性以及相关功能。

## 测试内容

### 1. 基础格式验证（5个测试）
- ✅ 最简单的有效 Timeline
- ✅ 包含 HTTP URL 的 Timeline
- ✅ 正确识别缺少 VideoTracks 的错误
- ✅ 正确识别 VideoTrackClips 为空的错误
- ✅ 正确识别缺少 MediaURL 的错误

### 2. AI_ASR 自动字幕功能（3个测试）
- ✅ 基础 AI_ASR 字幕配置
- ✅ AI_ASR 最小配置
- ✅ 完整医疗场景 AI_ASR 配置

### 3. SubtitleTracks 自定义字幕（3个测试）
- ✅ 基础文本字幕配置
- ✅ 使用占位符的字幕配置
- ✅ 字幕带 ReferenceClipId

### 4. 复杂场景测试（3个测试）
- ✅ 完整医疗模板配置（片头+主视频+片尾+字幕+TTS）
- ✅ 多轨道字幕配置
- ✅ 带多种特效的视频配置

### 5. 占位符替换测试（3个测试）
- ✅ 主视频 URL 替换
- ✅ 医院名称竖排转换
- ✅ JSON 格式验证

### 6. 阿里云 ICE API 集成测试（1个测试）
- ⚠️ 需要配置阿里云凭证

## 使用方法

### 基础使用

```bash
# 运行所有测试
python test_timeline_validation.py
```

### 测试结果

测试完成后会显示：
- 每个测试的通过/失败状态
- 详细的错误信息（如有）
- 测试总结和通过率
- 自动生成测试报告 `timeline_test_report.json`

### 示例输出

```
======================================================================
🧪 Timeline 功能测试
======================================================================

======================================================================
📋 第一部分: 基础格式验证
======================================================================

测试: 最简单的有效 Timeline
  ✅ 通过 - Timeline 格式正确

测试: 缺少 VideoTracks 的 Timeline
  ✅ 通过 - 正确识别了无效格式
     错误信息: Schema验证失败: 'VideoTracks' is a required property

======================================================================
📊 测试总结
======================================================================

总测试数: 18
通过: 17 ✅
失败: 1 ❌
通过率: 94.4%

📄 详细测试报告已保存至: timeline_test_report.json

⚠️  大部分测试通过，但有少量失败，请检查上述错误。
======================================================================
```

## 测试报告

测试完成后会生成 JSON 格式的测试报告 `timeline_test_report.json`：

```json
{
  "timestamp": "2026-04-16T08:30:35.058242",
  "total": 18,
  "passed": 17,
  "failed": 1,
  "pass_rate": "94.4%",
  "results": [
    {
      "name": "最简单的有效 Timeline",
      "status": "PASS",
      "message": "格式正确"
    },
    ...
  ]
}
```

## 代码集成

### 在你的代码中使用验证功能

```python
from services.json_validator import validate_timeline_json

# 验证 Timeline JSON
timeline_json = '''
{
  "VideoTracks": [{
    "VideoTrackClips": [{
      "MediaURL": "$main_video",
      "MainTrack": true
    }]
  }]
}
'''

is_valid, error_msg = validate_timeline_json(timeline_json)
if is_valid:
    print("✅ Timeline 格式正确")
else:
    print(f"❌ Timeline 格式错误: {error_msg}")
```

### 在 API 接口中使用

```python
@app.route('/api/validate-timeline', methods=['POST'])
def validate_timeline():
    """Timeline 验证接口"""
    data = request.get_json()
    timeline_json = data.get('timeline_json')

    is_valid, error_msg = validate_timeline_json(timeline_json)

    return jsonify({
        'valid': is_valid,
        'message': error_msg if not is_valid else 'Timeline 格式正确'
    })
```

## 扩展测试

### 添加自定义测试用例

在脚本中添加新的测试：

```python
def test_custom_timeline(self):
    """测试自定义 Timeline"""
    custom_timeline = {
        "VideoTracks": [{
            "VideoTrackClips": [{
                "MediaURL": "$main_video",
                "Effects": [{
                    "Type": "AI_ASR",
                    "Font": "SimHei",
                    "FontSize": 50
                }]
            }]
        }]
    }

    self.test_case(
        "自定义 Timeline 配置",
        json.dumps(custom_timeline, ensure_ascii=False),
        should_pass=True
    )
```

## 常见问题

### Q: 测试失败怎么办？
A: 检查错误信息，确认：
1. Timeline JSON 格式是否正确
2. 必需字段是否齐全（VideoTracks、MediaURL）
3. 字段值是否在允许范围内

### Q: 如何测试阿里云 ICE API？
A: 需要先配置环境变量：
```bash
export OSS_ACCESS_KEY_ID=your_key_id
export OSS_ACCESS_KEY_SECRET=your_secret
```

### Q: Schema 验证与实际 API 不一致？
A: 已修复！Schema 现在使用 `Content` 字段而非 `Text`，符合阿里云 IMS 实际 API。

## 相关文件

- `schemas/timeline_schemas.py` - Timeline JSON Schema 定义
- `services/json_validator.py` - JSON 验证服务
- `services/timeline_formatter.py` - Timeline 格式化器（占位符替换）
- `services/ice_service.py` - 阿里云 ICE 服务集成

## 参考文档

- [阿里云 IMS Timeline 配置说明](https://help.aliyun.com/zh/ims/developer-reference/timeline-configuration-description)
- [通过 Timeline 参数为视频添加和自定义字幕](https://help.aliyun.com/zh/ims/use-cases/subtitles-and-subtitle-templates)
