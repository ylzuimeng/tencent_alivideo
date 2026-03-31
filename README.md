# 视频处理平台

一个基于Flask的智能视频处理系统，集成阿里云OSS和ICE服务，提供视频上传、模板编辑、异步处理等功能。

## ✨ 功能特性

### 📤 文件管理
- 支持多种视频格式上传（MP4、AVI、MOV、WMV、FLV、MKV）
- 阿里云OSS对象存储
- 文件列表查看与管理
- 支持文件删除功能

### 🎨 模板系统
- **模板素材管理** - 上传和管理视频、图片素材
- **模板组合配置** - 将片头、片尾、转场、背景等素材组合成完整模板
- **可视化选择** - 下拉列表选择模板，无需记忆ID
- **模板预览** - 实时查看模板包含的组件

### 🎬 视频处理
- **异步任务处理** - 基于线程池的并发处理
- **阿里云ICE集成** - 专业级视频剪辑能力
- **实时进度追踪** - 任务状态实时更新
- **成品下载** - 处理完成后一键下载

### 🎯 用户体验
- **响应式设计** - 支持多设备访问
- **统一UI风格** - Bootstrap 5 + 自定义样式
- **智能筛选** - 任务列表支持按状态筛选
- **友好提示** - 完善的错误处理和用户引导

## 🛠 技术栈

### 后端
- **Flask 2.3.0** - Web框架
- **SQLAlchemy** - ORM数据库操作
- **SQLite** - 轻量级数据库
- **Alibaba Cloud OSS** - 对象存储服务
- **Alibaba Cloud ICE** - 智能视频制作服务

### 前端
- **Bootstrap 5.2.3** - UI框架
- **Font Awesome 5.15.4** - 图标库
- **原生JavaScript** - 无额外依赖

### 开发工具
- **Python 3.x** - 开发语言
- **ThreadPoolExecutor** - 并发处理
- **Logging** - 日志系统

## 📦 安装部署

### 环境要求
- Python 3.7+
- pip 包管理器
- 阿里云OSS账号
- 阿里云ICE账号

### 1. 克隆项目
```bash
git clone https://github.com/ylzuimeng/tencent_alivideo.git
cd tencent_alivideo
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
创建 `.env` 文件并配置以下变量：

```bash
# 阿里云OSS配置
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=your_bucket_name
OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com

# Flask配置
SECRET_KEY=your_secret_key
```

### 4. 初始化数据库
```bash
python app.py
```

首次运行会自动创建 `db/data.db` 数据库文件。

### 5. 启动应用
```bash
# 开发环境
python app.py

# 生产环境（建议使用gunicorn）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

应用启动后访问：`http://127.0.0.1:5000`

## 📖 使用指南

### 工作流程

```
1. 上传素材视频
   ↓
2. 配置处理模板（可选）
   - 上传片头/片尾/转场素材
   - 组合模板配置
   ↓
3. 创建处理任务
   - 选择源视频
   - 选择处理模板
   - 命名任务
   ↓
4. 查看任务进度
   - 实时进度更新
   - 任务状态筛选
   ↓
5. 下载成品视频
```

### 页面说明

#### 📤 上传素材 (`/upload/video`)
- 拖拽或选择视频文件上传
- 自动显示上传进度
- 上传成功后直接创建处理任务
- 支持批量上传

#### 🎨 模板管理 (`/taskstyles`)
- 上传模板素材（片头、片尾、转场、背景）
- 组合多个素材创建完整模板
- 可视化下拉选择素材
- 删除和管理模板

#### 📁 文件管理 (`/files`)
- 查看所有上传的文件
- 文件大小、上传时间信息
- 删除不需要的文件

#### 📋 任务列表 (`/task_list`)
- 查看所有处理任务
- 筛选任务状态（全部/等待中/处理中/已完成/失败）
- 实时进度条显示
- 下载成品视频
- 删除任务记录

## 📁 项目结构

```
tencent_alivideo/
├── app.py                      # Flask主应用
├── models.py                   # 数据库模型
├── config.py                   # 配置类
├── requirements.txt            # Python依赖
├── .env                        # 环境变量（不提交）
├── .gitignore                 # Git忽略规则
├── CLAUDE.md                  # AI助手指南
├── README.md                  # 项目文档
│
├── db/                         # 数据库目录
│   └── data.db                # SQLite数据库
│
├── services/                   # 业务服务
│   ├── __init__.py
│   ├── ice_service.py         # 阿里云ICE集成
│   └── task_processor.py      # 任务处理器
│
├── static/                     # 静态资源
│   └── css/
│       ├── style.css          # 自定义样式
│       └── app.css            # 全局设计规范
│
├── templates/                  # HTML模板
│   ├── base.html              # 基础模板
│   ├── upload_videos.html     # 上传页面
│   ├── taskstyles.html        # 模板管理
│   ├── templates.html         # 模板素材
│   ├── files.html             # 文件列表
│   └── task_list.html         # 任务列表
│
└── example/                    # 示例代码
    ├── cut.py                 # 剪辑示例
    ├── subtitle.py            # 字幕示例
    └── ...
```

## 🔌 API文档

### 文件上传

**上传视频文件**
```
POST /api/upload/video
Content-Type: multipart/form-data

参数:
  file: 视频文件
  template: 模板ID（可选）

返回:
{
  "message": "文件上传成功",
  "file_id": 1,
  "file_url": "https://...",
  "filename": "video.mp4"
}
```

**上传模板素材**
```
POST /api/upload/template
Content-Type: multipart/form-data

参数:
  file: 视频文件

返回: 同上
```

### 文件删除

```
POST /api/delete/<int:file_id>
POST /api/upload/templates/delete/<int:file_id>

返回: 重定向到文件列表页面
```

### 模板管理

**获取模板列表**
```
GET /api/templates

返回:
{
  "taskstyles": [
    {
      "id": 1,
      "name": "模板名称",
      "open_oss_url": "片头URL",
      "close_oss_url": "片尾URL",
      ...
    }
  ]
}
```

**保存模板配置**
```
POST /api/save_taskstyle
Content-Type: application/json

Body:
{
  "name": "模板名称",
  "header_file": "片头URL",
  "footer_file": "片尾URL",
  "transition_file": "转场URL",
  "background_file": "背景1URL",
  "background2_file": "背景2URL",
  "description": "描述"
}
```

**删除模板**
```
POST /api/delete_taskstyle/<int:taskstyle_id>
```

### 任务管理

**创建处理任务**
```
POST /api/tasks/create
Content-Type: application/json

Body:
{
  "source_file_id": 1,
  "task_style_id": 2,
  "task_name": "我的视频处理"
}

返回:
{
  "message": "任务创建成功",
  "task_id": 1,
  "task_name": "我的视频处理",
  "status": "pending"
}
```

**获取任务列表**
```
GET /api/tasks

返回: 任务对象数组
```

**获取任务详情**
```
GET /api/tasks/<int:task_id>

返回: 任务详细信息
```

**获取任务进度**
```
GET /api/tasks/<int:task_id>/progress

返回:
{
  "task_id": 1,
  "status": "processing",
  "progress": 45,
  "error_message": null
}
```

**下载成品**
```
GET /api/tasks/<int:task_id>/download

返回:
{
  "download_url": "https://...",
  "task_name": "我的视频处理",
  "completed_at": "2025-03-31T22:00:00"
}
```

**删除任务**
```
DELETE /api/tasks/<int:task_id>
```

## 🔧 配置说明

### OSS配置
- `OSS_ACCESS_KEY_ID` - 阿里云AccessKey ID
- `OSS_ACCESS_KEY_SECRET` - 阿里云AccessKey Secret
- `OSS_BUCKET_NAME` - OSS存储桶名称
- `OSS_ENDPOINT` - OSS访问域名（可选，默认：oss-cn-shanghai）

### Flask配置
- `SECRET_KEY` - Flask会话密钥
- `UPLOAD_FOLDER` - 上传目录（默认：uploads）
- `MAX_CONTENT_LENGTH` - 最大上传大小（默认：500MB）

### 数据库配置
- 默认使用SQLite，无需额外配置
- 数据库文件：`db/data.db`
- 首次运行自动创建表结构

## 🐛 常见问题

### 1. OSS上传失败
**问题**: 上传文件时报错"OSS配置不完整"

**解决**:
- 检查 `.env` 文件是否正确配置
- 确认OSS AccessKey有足够权限
- 检查bucket名称和endpoint是否正确

### 2. 任务处理卡在pending状态
**问题**: 任务创建后状态一直是"等待中"

**解决**:
- 检查ICE服务配置是否正确
- 查看应用日志：`tail -f app.log`
- 确认ThreadPoolExecutor正常运行

### 3. 无法下载成品视频
**问题**: 点击下载没有反应或404错误

**解决**:
- 确认任务状态为"已完成"
- 检查OSS中成品文件是否存在
- 查看浏览器控制台是否有错误

### 4. 数据库错误
**问题**: 启动时报数据库相关错误

**解决**:
- 删除 `db/data.db` 文件
- 重启应用让它重新创建数据库
- 或运行：`python -c "from app import app, db; from models import *; app.app_context().push(); db.create_all()"`

## 📝 更新日志

### v1.0.0 (2025-03-31)
- ✅ 实现完整的视频处理工作流
- ✅ 集成阿里云ICE视频编辑服务
- ✅ 添加异步任务处理和进度追踪
- ✅ 优化前端用户体验（模板下拉选择、任务筛选）
- ✅ 修复多个bug（模板选择、下载链接、file_id传递）
- ✅ 统一设计规范（app.css）
- ✅ 添加项目文档（CLAUDE.md、README.md）

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👥 作者

- **yanglei** - [GitHub](https://github.com/ylzuimeng)

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)
- [阿里云OSS](https://www.aliyun.com/product/oss)
- [阿里云ICE](https://www.aliyun.com/product/ice)

---

🔗 **项目地址**: [https://github.com/ylzuimeng/tencent_alivideo](https://github.com/ylzuimeng/tencent_alivideo)

⭐ 如果这个项目对你有帮助，请给个Star！
