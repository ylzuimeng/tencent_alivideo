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
- **models.py** - SQLAlchemy ORM models (File, Template, VideoTemplate, TaskStyle, ProcessingTask)
- **config.py** - Configuration class loading from .env file
- **db/data.db** - SQLite database (auto-created on first run)

### Key Classes

- **OSSConfig** - Validates and constructs OSS URLs from environment variables
- **OSSClient** - Wrapper around `alibabacloud_oss_v2` for upload/delete operations
- **FileHandler** - Generates OSS paths (`uploads/{timestamp}_{filename}`) and validates video file extensions
- **TemplateHandler** - Same as FileHandler but uses `templates/{timestamp}_{filename}` path prefix
- **JSONValidator** - Validates JSON fields against schemas (services/json_validator.py)

### Database Models

- **File** - Uploaded videos with filename, oss_url, upload_time, size
- **Template** - Template videos with same structure as File
- **VideoTemplate** - Unified template system (current) - see Template Models section below
- **TaskStyle** - Legacy template system (deprecated) - see Template Models section below
- **ProcessingTask** - Video processing jobs with template references
- **DoctorInfo** - Doctor information for medical video templates
- **TaskMaterial** - Task material associations

### OSS Path Convention

Files are stored with specific prefixes:
- Video uploads: `uploads/{timestamp}_{filename}`
- Templates: `templates/{timestamp}_{filename}`
- Processed videos: `processed_videos/`

When deleting, the code extracts the filename from the full OSS URL and prepends the prefix back.

### Routes

| Route | Purpose |
|-------|---------|
| `/`, `/upload/video` | Video upload page |
| `/api/upload/video` | Video upload API (POST) |
| `/api/delete/<int:file_id>` | Delete video (POST) |
| `/templates` | Template management page |
| `/templates/unified` | Unified template management (simple + advanced modes) |
| `/api/upload/template` | Template upload API (POST) |
| `/api/upload/templates/delete/<int:file_id>` | Delete template (POST) |
| `/api/video_templates` | Create/list simple templates (REST API) |
| `/api/video_templates/advanced` | Create/list advanced templates (REST API) |
| `/api/video_templates/validate-timeline` | Validate Timeline JSON (POST) |
| `/taskstyles` | Task style composition page (legacy) |
| `/api/save_taskstyle` | Save composed TaskStyle (POST, deprecated) |
| `/api/delete_taskstyle/<int:taskstyle_id>` | Delete TaskStyle (POST, deprecated) |
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

## Database Migrations

This project uses Alembic for database migrations.

### Running Migrations

```bash
# Check current migration version
alembic current

# Upgrade to latest migration
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "Description"
```

### Migration Management Scripts

The project provides convenience scripts for safe migration management:

- **`scripts/migrate_manager.py`** - High-level migration CLI
  - `python scripts/migrate_manager.py backup` - Create database backup
  - `python scripts/migrate_manager.py migrate` - Run migrations with auto-backup
  - `python scripts/migrate_manager.py rollback` - Rollback to previous version
  - `python scripts/migrate_manager.py status` - Show migration status

- **`scripts/pre_migration_check.py`** - Pre-migration validation
  - Counts TaskStyle and VideoTemplate records
  - Checks ProcessingTask references
  - Shows migration preview
  - Asks for confirmation

- **`scripts/post_migration_check.py`** - Post-migration validation
  - Validates migrated templates
  - Checks timeline_json consistency
  - Verifies ProcessingTask references
  - Confirms no data loss

### Migration Workflow

```bash
# Step 1: Pre-migration check
python scripts/pre_migration_check.py

# Step 2: Run migration (auto-backups included)
python scripts/migrate_manager.py migrate

# Step 3: Post-migration validation
python scripts/post_migration_check.py

# Step 4: Test application
python app.py  # Verify functionality
```

### Rollback

If issues occur:

```bash
# Automatic rollback (migration manager)
python scripts/migrate_manager.py rollback

# Manual database restore
cp db/backups/data_YYYYMMDD_HHMMSS.db db/data.db
```

See `docs/MIGRATION_GUIDE.md` for detailed migration instructions.

## JSON Validation

All JSON fields in templates are validated using structured schemas.

### Validation Infrastructure

- **Schema Definitions**: `schemas/timeline_schemas.py`
  - `TIMELINE_SCHEMA` - VideoTracks structure validation
  - `OUTPUT_MEDIA_SCHEMA` - Output configuration (Width/Height ranges)
  - `TEXT_OVERLAY_SCHEMA` - Text overlay structure validation
  - `EDITING_PRODUCE_SCHEMA` - Production configuration validation

- **Validator Service**: `services/json_validator.py`
  - `JSONValidator` class with caching
  - `validate_json(json_str, schema_type)` method
  - Convenience functions: `validate_timeline_json()`, `validate_output_media_config()`, etc.

### Validated Fields

VideoTemplate JSON fields are automatically validated on API endpoints:

1. **timeline_json** (advanced mode)
   - Required: `VideoTracks` array
   - Each track needs: `VideoTrackClips` array
   - Each clip needs: `MediaURL` field
   - Supports placeholders: `$main_video`, `$mainSubtitleDepart`, etc.

2. **output_media_config** (optional)
   - Width: 240-3840 pixels
   - Height: 240-2160 pixels
   - Optional: Bitrate, Fps, Format

3. **text_overlay_config** (optional)
   - Array of overlay objects
   - Each object needs: text, x, y coordinates
   - Optional: font_size, font_color, duration, alignment

4. **editing_produce_config** (optional)
   - Optional: CoverUrl, CoverMode, Title, Description, Tags

### Validation API

Test JSON validation via API:

```bash
curl -X POST http://127.0.0.1:5000/api/video_templates/validate-timeline \
  -H "Content-Type: application/json" \
  -d '{
    "timeline_json": "{\"VideoTracks\": [{\"VideoTrackClips\": []}]}"
  }'
```

### Model Validation Methods

VideoTemplate model provides validation methods:

```python
template = VideoTemplate(...)

# Validate specific field
is_valid, error = template.validate_timeline_json()

# Validate all JSON fields
results = template.validate_all_json_fields()
# Returns: {'timeline_json': (True, ''), 'output_media_config': (False, 'Width out of range'), ...}
```

## Template Models

### VideoTemplate (Current - Recommended)

The unified template system supporting two modes:

**Simple Mode** (`is_advanced=False`):
- Form-based configuration for basic use cases
- Fields: `name`, `header_video_url`, `footer_video_url`
- Subtitle settings: `enable_subtitle`, `subtitle_position`, `subtitle_extract_audio`
- Text overlay: `text_overlay_config` (JSON array)

**Advanced Mode** (`is_advanced=True`):
- Full JSON-based configuration for complex scenarios
- `timeline_json` - Complete ICE Timeline with placeholders
- `output_media_config` - Video output settings
- `editing_produce_config` - Production settings (cover, metadata)
- `formatter_type` - Custom formatter implementation
- `category` - Template classification: medical/education/general/migrated
- `thumbnail_url` - Preview image

**Placeholders Supported:**
- `$main_video` - Main video URL
- `$mainSubtitleDepart` - Hospital + department (vertical text)
- `$mainSubtitleName` - Doctor name + title (vertical text)
- `$beginingSubtitleTitle` - Video title
- `$beginingAudioTitle` - Video title (for TTS)

**Usage:**

```python
# Simple mode
template = VideoTemplate(
    name="Basic Template",
    header_video_url="https://oss.example.com/header.mp4",
    footer_video_url="https://oss.example.com/footer.mp4",
    enable_subtitle=True,
    subtitle_position="bottom"
)

# Advanced mode
template = VideoTemplate(
    name="Medical Template",
    timeline_json='{"VideoTracks": [{"VideoTrackClips": [...]}]}',
    output_media_config='{"Width": 1280, "Height": 720}',
    category="medical",
    is_advanced=True,
    formatter_type="medical"
)
```

### TaskStyle (Legacy - Deprecated)

**Status**: Deprecated, frozen schema, emits DeprecationWarning when used

The original template system with fixed fields:
- `open_oss_url` - Header video
- `close_oss_url` - Footer video
- `title_picture_oss_url_1` - Background image 1
- `title_picture_oss_url_2` - Background image 2
- `change_material_oss_url` - Transition effect

**Migration Required**: Use `scripts/migrate_manager.py` to migrate to VideoTemplate

See `docs/MIGRATION_GUIDE.md` for migration instructions.

### Template Priority System

Task processing uses a 3-tier priority system (services/task_processor.py:177-180):

1. **VideoTemplate with `is_advanced=True`** (new system with placeholders)
2. **VideoTemplate with `is_advanced=False`** (compatibility mode)
3. **TaskStyle** (legacy fallback, deprecated)

When creating tasks, the system selects the template according to this priority.

### Template Conversion

The `services/template_converter.py` module provides bidirectional conversion:

```python
from services.template_converter import TemplateConverter

# Simple → Advanced
timeline_json = TemplateConverter.simple_to_advanced(template)

# Advanced → Simple
simple_fields = TemplateConverter.advanced_to_simple(timeline_json)
```

This allows seamless conversion between template modes.
