"""Migrate TaskStyle to VideoTemplate

Revision ID: 9ebe54ae970b
Revises: 871c4edfd303
Create Date: 2026-04-12 20:07:27.996404

This migration:
1. Migrates all TaskStyle records to VideoTemplate with timeline_json format
2. Updates ProcessingTask references from task_style_id to video_template_id
3. Marks migrated templates with category='migrated'

"""
from typing import Sequence, Union
import json
import logging

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '9ebe54ae970b'
down_revision: Union[str, None] = '871c4edfd303'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

logger = logging.getLogger(__name__)


def upgrade() -> None:
    """Migrate TaskStyle records to VideoTemplate"""

    # Get database connection
    conn = op.get_bind()
    logger.info("Starting TaskStyle to VideoTemplate migration")

    # Step 1: Query existing TaskStyle records
    result = conn.execute(
        sa.text("""
            SELECT id, name, open_oss_url, close_oss_url,
                   title_picture_oss_url_1, title_picture_oss_url_2,
                   change_material_oss_url, description
            FROM task_style
        """)
    )

    taskstyle_records = result.fetchall()
    logger.info(f"Found {len(taskstyle_records)} TaskStyle records to migrate")

    # Step 2: Create a mapping table for task_style_id -> video_template_id
    id_mapping = {}

    for record in taskstyle_records:
        # Convert TaskStyle to VideoTemplate with timeline_json
        timeline = {
            "VideoTracks": [{
                "VideoTrackClips": []
            }]
        }

        # Add header video if exists
        if record.open_oss_url:
            timeline["VideoTracks"][0]["VideoTrackClips"].append({
                "MediaURL": record.open_oss_url,
                "Duration": 3
            })

        # Add main video placeholder
        timeline["VideoTracks"][0]["VideoTrackClips"].append({
            "MediaURL": "$main_video",
            "MainTrack": True
        })

        # Add footer video if exists
        if record.close_oss_url:
            timeline["VideoTracks"][0]["VideoTrackClips"].append({
                "MediaURL": record.close_oss_url,
                "Duration": 3
            })

        # Insert into video_template table
        insert_result = conn.execute(
            sa.text("""
                INSERT INTO video_template
                (name, header_video_url, footer_video_url,
                 timeline_json, is_advanced, category,
                 description, created_at, updated_at)
                VALUES (:name, :header, :footer, :timeline,
                        :is_advanced, :category, :description,
                        datetime('now'), datetime('now'))
                RETURNING id
            """),
            {
                "name": f"{record.name or 'TaskStyle'} (已迁移)",
                "header": record.open_oss_url,
                "footer": record.close_oss_url,
                "timeline": json.dumps(timeline, ensure_ascii=False),
                "is_advanced": 1,
                "category": "migrated",
                "description": f"从TaskStyle迁移: {record.description or ''}"
            }
        )

        new_template_id = insert_result.fetchone()[0]
        id_mapping[record.id] = new_template_id
        logger.info(f"Migrated TaskStyle {record.id} -> VideoTemplate {new_template_id}")

    # Step 3: Update processing_task references
    for task_style_id, video_template_id in id_mapping.items():
        conn.execute(
            sa.text("""
                UPDATE processing_task
                SET video_template_id = :video_template_id,
                    task_style_id = NULL,
                    use_advanced_timeline = 1
                WHERE task_style_id = :task_style_id
            """),
            {
                "video_template_id": video_template_id,
                "task_style_id": task_style_id
            }
        )
        logger.info(f"Updated tasks for TaskStyle {task_style_id} -> VideoTemplate {video_template_id}")

    logger.info(f"Migration completed: {len(id_mapping)} TaskStyle records migrated")


def downgrade() -> None:
    """Revert migration - delete migrated templates and restore task_style_id references"""

    conn = op.get_bind()
    logger.warning("Reverting TaskStyle migration")

    # Note: This is a simplified rollback.
    # In production, you would need to store the original task_style_id values
    # to properly restore them.

    # Delete migrated templates
    result = conn.execute(
        sa.text("""
            DELETE FROM video_template
            WHERE category = 'migrated'
        """)
    )

    logger.info(f"Deleted {result.rowcount} migrated VideoTemplate records")

    # Note: We cannot fully restore task_style_id without storing the mapping
    # This is a limitation of the rollback
    logger.warning("Cannot fully restore task_style_id references - manual intervention may be required")

