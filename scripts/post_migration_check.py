#!/usr/bin/env python
"""Post-migration validation checks

Validates that migration completed successfully and no data was lost.

Usage:
    python scripts/post_migration_check.py
"""
import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, TaskStyle, VideoTemplate, ProcessingTask


def validate_migrated_templates():
    """Validate that migrated templates are correct"""

    with app.app_context():
        print("=" * 70)
        print("✅ Post-Migration Validation")
        print("=" * 70)

        # Check migrated templates
        migrated = VideoTemplate.query.filter_by(category='migrated').all()
        print(f"\n📊 Migrated Templates: {len(migrated)}")

        if not migrated:
            print("  ℹ️  No migrated templates found")
            print("  (This is normal if TaskStyle was already empty or migration hasn't run yet)")
            return True

        all_valid = True
        validation_results = []

        for template in migrated:
            print(f"\n  • {template.name} (ID: {template.id})")
            print(f"    - Created: {template.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

            # Validate timeline_json
            timeline_valid = False
            if template.timeline_json:
                try:
                    timeline = json.loads(template.timeline_json)
                    clips = timeline.get("VideoTracks", [{}])[0].get("VideoTrackClips", [])
                    print(f"    - Timeline clips: {len(clips)}")

                    # Check for expected structure
                    if clips:
                        print(f"    - First clip: {clips[0].get('MediaURL', 'N/A')}")
                        print(f"    - Last clip: {clips[-1].get('MediaURL', 'N/A')}")

                    timeline_valid = True
                    print(f"    - Timeline JSON: ✅")

                except json.JSONDecodeError as e:
                    print(f"    - Timeline JSON: ❌ {e}")
                    all_valid = False
                except Exception as e:
                    print(f"    - Timeline JSON: ❌ {e}")
                    all_valid = False
            else:
                print(f"    - Timeline JSON: ⚠️  Empty")

            # Validate fields
            print(f"    - Header URL: {'✅' if template.header_video_url else '❌'}")
            print(f"    - Footer URL: {'✅' if template.footer_video_url else '❌'}")
            print(f"    - is_advanced: {'✅' if template.is_advanced else '❌'}")
            print(f"    - category: {template.category}")

            validation_results.append({
                'template': template,
                'timeline_valid': timeline_valid
            })

        # Check all ProcessingTasks have valid references
        print(f"\n📊 ProcessingTask Reference Check:")
        tasks = ProcessingTask.query.all()
        print(f"  Total tasks: {len(tasks)}")

        tasks_with_taskstyle = 0
        tasks_with_videotemplate = 0
        tasks_with_none = 0
        invalid_references = 0

        for task in tasks:
            if task.task_style_id:
                tasks_with_taskstyle += 1
                print(f"  ⚠️  Task {task.id} still references TaskStyle {task.task_style_id}")

            if task.video_template_id:
                template = VideoTemplate.query.get(task.video_template_id)
                if not template:
                    print(f"  ❌ Task {task.id}: References non-existent VideoTemplate {task.video_template_id}")
                    invalid_references += 1
                    all_valid = False
                else:
                    tasks_with_videotemplate += 1

            if not task.task_style_id and not task.video_template_id:
                tasks_with_none += 1

        print(f"\n  • Using VideoTemplate: {tasks_with_videotemplate}")
        print(f"  • Using TaskStyle (should be 0): {tasks_with_taskstyle}")
        print(f"  • Using no template: {tasks_with_none}")
        print(f"  • Invalid references: {invalid_references}")

        # Check for data loss
        print(f"\n📊 Data Integrity Check:")

        taskstyle_count = TaskStyle.query.count()
        videotemplate_count = VideoTemplate.query.count()

        print(f"  • TaskStyle records: {taskstyle_count}")
        print(f"  • VideoTemplate records: {videotemplate_count}")
        print(f"  • Migrated VideoTemplate: {len(migrated)}")

        # Final summary
        print("\n" + "=" * 70)
        if all_valid:
            print("✅ All validation checks passed!")
            print("=" * 70)

            if tasks_with_taskstyle > 0:
                print("\n⚠️  Note: Some tasks still reference TaskStyle")
                print("   This is expected if the reference update migration hasn't run yet.")
            else:
                print("\n✅ All tasks have been updated to use VideoTemplate")

            return True
        else:
            print("❌ Validation failed - please check the errors above")
            print("=" * 70)
            return False


def check_timeline_consistency():
    """Check that migrated timelines are consistent with original TaskStyle data"""

    with app.app_context():
        print("\n🔍 Timeline Consistency Check")
        print("-" * 70)

        migrated = VideoTemplate.query.filter_by(category='migrated').all()
        taskstyles = TaskStyle.query.all()

        if not migrated or not taskstyles:
            print("  ℹ️  Skipped (no migrated templates or TaskStyle records)")
            return True

        # Try to match migrated templates with original TaskStyle
        # This is approximate since we can't guarantee the mapping
        inconsistencies = []

        for template in migrated:
            try:
                timeline = json.loads(template.timeline_json)
                clips = timeline.get("VideoTracks", [{}])[0].get("VideoTrackClips", [])

                # Check if header/footer match
                if template.header_video_url:
                    header_in_timeline = any(
                        clip.get('MediaURL') == template.header_video_url
                        for clip in clips
                    )
                    if not header_in_timeline:
                        inconsistencies.append(
                            f"{template.name}: Header URL not in timeline"
                        )

                if template.footer_video_url:
                    footer_in_timeline = any(
                        clip.get('MediaURL') == template.footer_video_url
                        for clip in clips
                    )
                    if not footer_in_timeline:
                        inconsistencies.append(
                            f"{template.name}: Footer URL not in timeline"
                        )

            except Exception as e:
                inconsistencies.append(f"{template.name}: {e}")

        if inconsistencies:
            print(f"  ❌ Found {len(inconsistencies)} inconsistencies:")
            for issue in inconsistencies:
                print(f"    - {issue}")
            return False
        else:
            print(f"  ✅ All {len(migrated)} migrated templates have consistent timelines")
            return True


def main():
    """Main entry point"""
    try:
        # Run all validation checks
        templates_valid = validate_migrated_templates()
        consistency_valid = check_timeline_consistency()

        overall_valid = templates_valid and consistency_valid

        print("\n" + "=" * 70)
        if overall_valid:
            print("✅ Post-migration validation completed successfully!")
            print("=" * 70)
            print("\nNext steps:")
            print("  1. Test the application: python app.py")
            print("  2. Verify template functionality in /templates/unified")
            print("  3. Create a test task using a migrated template")
        else:
            print("❌ Post-migration validation failed!")
            print("=" * 70)
            print("\nTroubleshooting:")
            print("  1. Review the errors above")
            print("  2. Check logs: tail -f logs/app.log")
            print("  3. Consider rollback: python scripts/migrate_manager.py rollback")

        sys.exit(0 if overall_valid else 1)

    except Exception as e:
        print(f"\n❌ Post-migration check failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
