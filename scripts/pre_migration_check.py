#!/usr/bin/env python
"""Pre-migration validation checks

Validates data integrity before running migrations and provides
a preview of what will be migrated.

Usage:
    python scripts/pre_migration_check.py
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, TaskStyle, VideoTemplate, ProcessingTask


def check_data_integrity():
    """Validate data before migration"""

    with app.app_context():
        print("=" * 70)
        print("🔍 Pre-Migration Data Check")
        print("=" * 70)

        # Check TaskStyle records
        taskstyles = TaskStyle.query.all()
        print(f"\n📊 TaskStyle Records: {len(taskstyles)}")

        if taskstyles:
            for ts in taskstyles:
                print(f"\n  • ID {ts.id}: {ts.name or 'Unnamed'}")
                print(f"    - Header: {'✅' if ts.open_oss_url else '❌'}")
                print(f"    - Footer: {'✅' if ts.close_oss_url else '❌'}")
                print(f"    - BG 1: {'✅' if ts.title_picture_oss_url_1 else '❌'}")
                print(f"    - BG 2: {'✅' if ts.title_picture_oss_url_2 else '❌'}")
                print(f"    - Transition: {'✅' if ts.change_material_oss_url else '❌'}")

                # Count associated tasks
                task_count = ts.processing_tasks.count()
                print(f"    - Associated tasks: {task_count}")
        else:
            print("  ✅ No TaskStyle records found (already migrated or never used)")

        # Check VideoTemplate records
        templates = VideoTemplate.query.all()
        print(f"\n📊 VideoTemplate Records: {len(templates)}")

        if templates:
            simple_count = sum(1 for t in templates if not t.is_advanced)
            advanced_count = sum(1 for t in templates if t.is_advanced)
            migrated_count = sum(1 for t in templates if t.category == 'migrated')

            print(f"  • Simple mode (is_advanced=False): {simple_count}")
            print(f"  • Advanced mode (is_advanced=True): {advanced_count}")
            print(f"  • Migrated (category='migrated'): {migrated_count}")

            # Show templates by category
            categories = {}
            for t in templates:
                categories[t.category] = categories.get(t.category, 0) + 1

            if categories:
                print(f"\n  By category:")
                for category, count in sorted(categories.items()):
                    print(f"    - {category}: {count}")
        else:
            print("  ⚠️  No VideoTemplate records found")

        # Check ProcessingTask references
        tasks_using_taskstyle = ProcessingTask.query.filter(
            ProcessingTask.task_style_id.isnot(None)
        ).count()

        tasks_using_videotemplate = ProcessingTask.query.filter(
            ProcessingTask.video_template_id.isnot(None)
        ).count()

        tasks_with_none = ProcessingTask.query.filter(
            ProcessingTask.task_style_id.is_(None),
            ProcessingTask.video_template_id.is_(None)
        ).count()

        print(f"\n📊 ProcessingTask References:")
        print(f"  • Using TaskStyle: {tasks_using_taskstyle}")
        print(f"  • Using VideoTemplate: {tasks_using_videotemplate}")
        print(f"  • Using no template: {tasks_with_none}")
        print(f"  • Total tasks: {ProcessingTask.query.count()}")

        # Validation warnings and recommendations
        warnings = []
        recommendations = []

        if tasks_using_taskstyle > 0:
            warnings.append(
                f"⚠️  {tasks_using_taskstyle} tasks still reference TaskStyle. "
                f"These will be updated to use VideoTemplate after migration."
            )

        if len(taskstyles) > 0:
            recommendations.append(
                f"ℹ️  Migration will create {len(taskstyles)} new VideoTemplate records "
                f"with category='migrated'"
            )

        # Check for potential conflicts
        migrated_templates = VideoTemplate.query.filter_by(category='migrated').all()
        if migrated_templates:
            recommendations.append(
                f"ℹ️  Found {len(migrated_templates)} already-migrated templates. "
                f"New migrations will add duplicates."
            )

        # Print warnings
        if warnings:
            print(f"\n⚠️  Warnings:")
            for warning in warnings:
                print(f"  {warning}")

        # Print recommendations
        if recommendations:
            print(f"\n💡 Recommendations:")
            for recommendation in recommendations:
                print(f"  {recommendation}")

        # Summary
        print("\n" + "=" * 70)
        print("📋 Migration Summary:")
        print("=" * 70)
        print(f"TaskStyle records to migrate: {len(taskstyles)}")
        print(f"Tasks to update: {tasks_using_taskstyle}")
        print(f"Current VideoTemplate count: {len(templates)}")
        print(f"Expected VideoTemplate count after migration: {len(templates) + len(taskstyles)}")

        # Ask for confirmation
        print("\n" + "=" * 70)
        if taskstyles:
            response = input("\nDo you want to proceed with migration? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                print("\n✅ Proceeding with migration...")
                return True
            else:
                print("\n❌ Migration cancelled by user")
                return False
        else:
            print("\n✅ No TaskStyle records to migrate - system already migrated!")
            return True


def main():
    """Main entry point"""
    try:
        proceed = check_data_integrity()
        sys.exit(0 if proceed else 1)
    except Exception as e:
        print(f"\n❌ Pre-migration check failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
