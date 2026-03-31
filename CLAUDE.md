# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask web application for uploading and managing video files and templates. It uses Alibaba Cloud OSS (Object Storage Service) for file storage and SQLite for metadata persistence.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
python app.py
```

The app runs on `http://127.0.0.1:5000` by default with debug mode enabled.

## Architecture

### Core Components

- **app.py** - Main Flask application with routes, OSS client, and file handlers
- **models.py** - SQLAlchemy ORM models (File, Template, TaskStyle)
- **config.py** - Configuration class loading from .env file
- **db/data.db** - SQLite database (auto-created on first run)

### Key Classes

- **OSSConfig** - Validates and constructs OSS URLs from environment variables
- **OSSClient** - Wrapper around `alibabacloud_oss_v2` for upload/delete operations
- **FileHandler** - Generates OSS paths (`uploads/{timestamp}_{filename}`) and validates video file extensions
- **TemplateHandler** - Same as FileHandler but uses `templates/{timestamp}_{filename}` path prefix

### Database Models

- **File** - Uploaded videos with filename, oss_url, upload_time, size
- **Template** - Template videos with same structure as File
- **TaskStyle** - Composite style templates combining multiple OSS URLs (open_oss_url, close_oss_url, title_picture_oss_url_1/2, change_material_oss_url)

### OSS Path Convention

Files are stored with specific prefixes:
- Video uploads: `uploads/{timestamp}_{filename}`
- Templates: `templates/{timestamp}_{filename}`

When deleting, the code extracts the filename from the full OSS URL and prepends the prefix back.

### Routes

| Route | Purpose |
|-------|---------|
| `/`, `/upload/video` | Video upload page |
| `/api/upload/video` | Video upload API (POST) |
| `/api/delete/<int:file_id>` | Delete video (POST) |
| `/templates` | Template management page |
| `/api/upload/template` | Template upload API (POST) |
| `/api/upload/templates/delete/<int:file_id>` | Delete template (POST) |
| `/taskstyles` | Task style composition page |
| `/api/save_taskstyle` | Save composed TaskStyle (POST) |
| `/api/delete_taskstyle/<int:taskstyle_id>` | Delete TaskStyle (POST) |
| `/files` | File list page |
| `/task_list` | Task list page |

## Environment Variables

Required in `.env`:
```
OSS_ACCESS_KEY_ID
OSS_ACCESS_KEY_SECRET
OSS_BUCKET_NAME
OSS_ENDPOINT (optional, defaults to oss-cn-shanghai.aliyuncs.com)
SECRET_KEY (optional, defaults to 'dev')
```

## Allowed File Extensions

Videos: `mp4`, `avi`, `mov`, `wmv`, `flv`, `mkv`

Max upload size: 500MB
