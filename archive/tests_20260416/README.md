# 测试文件归档 - 2026年4月16日

## 归档说明

本目录包含了项目开发过程中产生的所有测试相关文件，已从主目录清理并归档至此。

## 归档原因

- 清理主目录，保持项目结构清晰
- 保留测试历史记录，便于问题追溯
- 减少主目录中的临时文件干扰

## 归档内容

### 文件分类统计

- **Python测试脚本**: 28个
- **测试截图(PNG)**: 10个
- **测试文档(MD)**: 4个
- **测试报告(JSON)**: 3个
- **测试页面(HTML)**: 2个
- **测试视频(MP4)**: 1个
- **JavaScript文件**: 1个

**总计**: 49个文件

### 主要文件类型

#### 1. AI_ASR字幕相关测试（2026-04-16）
- `ai_asr_no_subtitle_fix.py` - AI_ASR字幕问题精确诊断
- `debug_ai_asr_issue.py` - AI_ASR字幕问题调试
- `deep_diagnose_ai_asr.py` - 深度诊断AI_ASR问题
- `test_ai_asr_subtitle.py` - AI_ASR字幕测试
- `test_ai_asr_correct.py` - AI_ASR正确配置测试

#### 2. 模板功能测试
- `test_template_edit.py` - 模板编辑功能测试
- `test_template_save.py` - 模板保存功能测试
- `test_template_save_v2.py` - 模板保存v2版本
- `test_template_edit_playwright.py` - Playwright模板编辑测试

#### 3. 上传和任务处理测试
- `test_enhanced_upload.py` - 增强上传功能测试
- `test_enhanced_workflow.py` - 增强工作流测试
- `test_direct_upload.py` - 直接上传测试
- `test_process_all.py` - 全流程处理测试
- `test_submit_and_monitor.py` - 提交和监控测试

#### 4. 输出配置测试
- `test_output_media_config.py` - 输出媒体配置测试
- `test_output_media_demo.py` - 输出媒体配置演示
- `output_media_config_test_report.json` - 配置测试报告
- `output_media_configs.json` - 输出配置文件

#### 5. Timeline配置测试
- `test_timeline_demo.py` - Timeline演示
- `test_timeline_validation.py` - Timeline验证测试
- `timeline_test_report.json` - Timeline测试报告

#### 6. 调试和诊断工具
- `check_task_status.py` - 任务状态检查工具
- `check_templates_ai_asr.py` - 模板AI_ASR检查
- `manual_process_task_9.py` - 手动处理任务9
- `query_latest_video.py` - 查询最新视频
- `inspect_upload.py` - 上传检查工具
- `print_output_media_config.py` - 打印输出配置

#### 7. 文档和指南
- `OUTPUT_MEDIA_CONFIG_GUIDE.md` - 输出媒体配置指南
- `TIMELINE_QUICK_REFERENCE.md` - Timeline快速参考
- `TIMELINE_TEST_GUIDE.md` - Timeline测试指南
- `TEST_REPORT_TEMPLATE_EDIT.md` - 模板编辑测试报告

#### 8. UI测试和截图
- `test_edit_in_browser.html` - 浏览器内编辑测试
- `test_results.html` - 测试结果页面
- 各种PNG截图文件（UI调试、按钮样式等）

#### 9. 其他测试文件
- `test_check_card.py` - 卡片检查测试
- `test_subtitle_task.py` - 字幕任务测试
- `test_time_display.py` - 时间显示测试
- `test_invalid_date_fix.py` - 无效日期修复测试
- `test_upload.mp4` - 测试视频文件

## 关键问题记录

### AI_ASR字幕问题

**问题**: Y值配置不当导致字幕不显示

**发现过程**:
1. 用户报告重启后字幕出现
2. 通过代码分析发现Y值是距离顶部的距离（官方文档确认）
3. 数据库显示：
   - 模板6: Y=1700（太大，超出720p视频范围）
   - 模板5: Y=300（正常）
   - 模板3: Y=600（正常）

**结论**:
- Y=1700 > 720px（视频高度）→ 字幕在视频外
- Y=300/600 < 720px → 字幕正常显示
- 重启本身不修复Y值，但可能切换了使用的模板

### 文件清理时机

- 日期: 2026年4月16日
- 原因: AI_ASR字幕问题已解决，清理临时测试文件
- 状态: 所有测试文件已归档，主目录已清理

## 使用说明

如需查看或复现测试，可以：

1. **查看测试代码**: 直接浏览相应的.py文件
2. **运行测试**: 从archive目录复制到主目录运行
3. **查看测试结果**: 查看JSON报告文件
4. **参考配置**: 查看output_media_configs.json等配置文件

## 重要提示

⚠️ **归档的文件仅供参考**，部分代码可能已过时或与当前代码库不兼容。

✅ **如需新的测试**，建议在当前代码库基础上编写新的测试脚本。

---

归档完成时间: 2026-04-16
归档负责人: Claude Code
