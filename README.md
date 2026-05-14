# 视频处理平台

基于 Flask 的智能视频处理系统，集成阿里云 OSS 和 ICE 服务，提供视频上传、模板管理、异步处理等功能。

## 功能特性

### 文件管理
- 多格式视频上传（MP4、AVI、MOV、WMV、FLV、MKV），最大 500MB
- 阿里云 OSS 对象存储，支持 STS 临时凭证直传
- 文件列表查看与管理

### 模板系统
- **VideoTemplate 统一模板** — 支持简单模式和高级模式
  - **简单模式** — 表单化配置片头/片尾、字幕、文字叠加
  - **高级模式** — 基于 Timeline JSON 的完整配置，支持占位符（`$main_video`、`$mainSubtitleDepart` 等）
- **模板模式转换** — 简单模式与高级模式双向转换 API
- **JSON 验证** — Timeline、输出配置、文字叠加等 JSON 字段自动校验
- **TaskStyle（已弃用）** — 旧版模板系统保留兼容，提供迁移工具

### 视频处理
- 异步任务处理（ThreadPoolExecutor）
- 阿里云 ICE 智能视频剪辑
- 实时进度追踪与状态筛选
- 成品视频下载

### 医疗视频
- 医生信息管理（姓名、医院、科室、职称）
- 医疗类模板（含科室+姓名竖排文字占位符）
- Excel 批量导入医生信息

## 技术栈

| 层级 | 技术 |
|------|------|
| Web 框架 | Flask 2.3.0（应用工厂模式） |
| ORM | Flask-SQLAlchemy |
| 数据库 | SQLite + Alembic 迁移 |
| 对象存储 | 阿里云 OSS（alibabacloud-oss-v2） |
| 视频剪辑 | 阿里云 ICE |
| 前端 | Bootstrap 5 + Font Awesome + 原生 JS |
| 数据处理 | Pandas + openpyxl |
| JSON 校验 | jsonschema |

## 安装部署

### 环境要求
- Python 3.7+
- 阿里云 OSS 账号
- 阿里云 ICE 账号（可选）

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
创建 `.env` 文件：

```bash
# 阿里云 OSS
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=your_bucket_name
OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com
OSS_STS_ROLE_ARN=your_sts_role_arn    # STS 直传需要

# Flask
SECRET_KEY=your_secret_key
```

### 4. 启动应用
```bash
python app.py
```

首次运行自动创建 `db/data.db`，访问 http://127.0.0.1:5000

## 项目结构

```
tencent_alivideo/
├── app.py                      # 应用工厂 + 启动入口
├── config.py                   # 配置类
├── models.py                   # SQLAlchemy 模型
│
├── blueprints/                 # 路由模块
│   ├── pages.py                # 页面路由
│   ├── upload_api.py           # 上传 API（STS 直传）
│   ├── file_api.py             # 文件管理 API
│   ├── template_api.py         # 模板 CRUD + 转换 API
│   ├── task_api.py             # 任务管理 API
│   ├── doctor_api.py           # 医生信息 API
│   └── legacy_api.py           # 旧版 API 兼容
│
├── services/                   # 业务服务
│   ├── oss_service.py          # OSS 客户端封装
│   ├── sts_service.py          # STS 临时凭证服务
│   ├── ice_service.py          # 阿里云 ICE 集成
│   ├── upload_service.py       # 上传处理
│   ├── task_processor.py       # 任务处理器
│   ├── template_converter.py   # 模板模式转换
│   ├── timeline_formatter.py   # Timeline 格式化
│   ├── json_validator.py       # JSON 校验服务
│   └── doctor_service.py       # 医生信息服务
│
├── schemas/                    # JSON Schema 定义
│   └── timeline_schemas.py     # Timeline/Output/Overlay Schema
│
├── utils/                      # 工具函数
│   ├── file_handler.py         # 文件路径生成与校验
│   └── time_helpers.py         # 北京时间格式化
│
├── migrations/                 # Alembic 数据库迁移
├── scripts/                    # 运维脚本
│   ├── migrate_manager.py      # 迁移管理（备份/迁移/回滚）
│   ├── pre_migration_check.py  # 迁移前检查
│   └── post_migration_check.py # 迁移后验证
│
├── static/                     # 静态资源
│   ├── css/                    # 样式文件
│   └── js/                     # JS 脚本（OSS 直传、模板管理等）
│
├── templates/                  # HTML 模板
│   ├── base.html
│   ├── upload_enhanced.html    # 增强上传页
│   ├── unified_templates.html  # 统一模板管理页
│   ├── task_list.html
│   ├── files.html
│   └── doctors.html
│
└── docs/                       # 文档
    ├── MIGRATION_GUIDE.md      # 迁移指南
    └── UNIFIED_TEMPLATES_GUIDE.md
```

## API 概览

### 文件上传
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/upload/video` | POST | 上传视频文件 |
| `/api/upload/template` | POST | 上传模板素材 |
| `/api/upload/sts-token` | GET | 获取 STS 临时凭证（直传 OSS） |
| `/api/delete/<file_id>` | POST | 删除文件 |

### 模板管理
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/video_templates` | GET/POST | 简单模板列表/创建 |
| `/api/video_templates/<id>` | GET/PUT/DELETE | 模板详情/更新/删除 |
| `/api/video_templates/advanced` | GET/POST | 高级模板列表/创建 |
| `/api/video_templates/convert` | POST | 模板模式转换（简单↔高级） |
| `/api/video_templates/validate-timeline` | POST | 验证 Timeline JSON |

### 任务管理
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/tasks/create` | POST | 创建处理任务 |
| `/api/tasks` | GET | 任务列表 |
| `/api/tasks/<id>` | GET | 任务详情 |
| `/api/tasks/<id>/progress` | GET | 任务进度 |
| `/api/tasks/<id>/download` | GET | 下载成品 |
| `/api/tasks/<id>` | DELETE | 删除任务 |

### 医生信息
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/doctors` | GET/POST | 医生列表/新增 |
| `/api/doctors/<id>` | GET/PUT/DELETE | 医生详情/更新/删除 |
| `/api/doctors/import` | POST | Excel 批量导入 |

## 数据库迁移

```bash
# 查看当前版本
alembic current

# 执行迁移（含自动备份）
python scripts/migrate_manager.py migrate

# 回滚
python scripts/migrate_manager.py rollback

# 迁移状态
python scripts/migrate_manager.py status
```

详见 [迁移指南](docs/MIGRATION_GUIDE.md)。

## 配置说明

| 变量 | 必填 | 说明 |
|------|------|------|
| `OSS_ACCESS_KEY_ID` | 是 | 阿里云 AccessKey ID |
| `OSS_ACCESS_KEY_SECRET` | 是 | 阿里云 AccessKey Secret |
| `OSS_BUCKET_NAME` | 是 | OSS 存储桶名称 |
| `OSS_ENDPOINT` | 否 | OSS 域名（默认 oss-cn-shanghai.aliyuncs.com） |
| `OSS_STS_ROLE_ARN` | 否 | STS 角色 ARN（直传模式需要） |
| `SECRET_KEY` | 否 | Flask 会话密钥（默认 dev） |

## 许可证

MIT License

## 作者

- **yanglei** - [GitHub](https://github.com/ylzuimeng)

---

项目地址: https://github.com/ylzuimeng/tencent_alivideo
