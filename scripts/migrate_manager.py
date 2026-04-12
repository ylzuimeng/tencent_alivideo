#!/usr/bin/env python
"""Migration management script

Provides CLI for managing database migrations with automatic backups and rollback capabilities.

Usage:
    python scripts/migrate_manager.py backup       # Create database backup
    python scripts/migrate_manager.py migrate      # Run migrations with backup
    python scripts/migrate_manager.py rollback     # Rollback to previous version
    python scripts/migrate_manager.py status       # Show current migration status
"""
import sys
import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class MigrationManager:
    """Manages database migrations with backup and rollback"""

    def __init__(self):
        self.db_path = project_root / 'db' / 'data.db'
        self.backup_dir = project_root / 'db' / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def backup_database(self) -> str:
        """Create timestamped database backup

        Returns:
            Path to backup file
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f'data_{timestamp}.db'

        shutil.copy2(self.db_path, backup_path)
        print(f"✅ Database backup created: {backup_path}")

        # Also create a symlink to the latest backup
        latest_backup = self.backup_dir / 'data_latest.db'
        if latest_backup.exists():
            latest_backup.unlink()
        try:
            latest_backup.symlink_to(backup_path.name)
        except OSError:
            # Symlink creation might fail on Windows
            pass

        return str(backup_path)

    def restore_backup(self, backup_path: str = None):
        """Restore database from backup

        Args:
            backup_path: Path to backup file. If None, uses latest backup.
        """
        if backup_path is None:
            # Find latest backup
            backups = sorted(self.backup_dir.glob('data_*.db'))
            if not backups:
                raise FileNotFoundError("No backup files found")
            backup_path = str(backups[-1])

        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        shutil.copy2(backup_path, self.db_path)
        print(f"✅ Database restored from: {backup_path}")

    def run_migration(self):
        """Run Alembic migration with automatic backup"""
        print("🚀 Starting database migration...")

        # Create backup first
        try:
            backup_path = self.backup_database()
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            print("Migration aborted for safety")
            return False

        try:
            # Run Alembic upgrade
            result = subprocess.run(
                ['alembic', 'upgrade', 'head'],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                check=True
            )

            print("✅ Migration completed successfully")
            if result.stdout:
                print(result.stdout)

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Migration failed: {e.stderr}")
            print(f"⏪ Restoring backup: {backup_path}")

            try:
                self.restore_backup(backup_path)
                print("✅ Backup restored successfully")
            except Exception as restore_error:
                print(f"❌ Backup restoration failed: {restore_error}")
                print(f"⚠️  Manual restore needed: cp {backup_path} {self.db_path}")

            return False

        except Exception as e:
            print(f"❌ Migration error: {e}")
            return False

    def rollback_migration(self):
        """Rollback to previous migration version"""
        print("⏪ Rolling back database migration...")

        # Create backup before rollback
        try:
            backup_path = self.backup_database()
        except Exception as e:
            print(f"⚠️  Backup failed: {e}")
            print("Attempting rollback without backup...")
            backup_path = None

        try:
            # Run Alembic downgrade
            result = subprocess.run(
                ['alembic', 'downgrade', '-1'],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                check=True
            )

            print("✅ Rollback completed successfully")
            if result.stdout:
                print(result.stdout)

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Rollback failed: {e.stderr}")

            if backup_path:
                print(f"⏪ Restoring backup: {backup_path}")
                try:
                    self.restore_backup(backup_path)
                    print("✅ Backup restored successfully")
                except Exception as restore_error:
                    print(f"❌ Backup restoration failed: {restore_error}")

            return False

        except Exception as e:
            print(f"❌ Rollback error: {e}")
            return False

    def show_status(self):
        """Show current migration status"""
        print("📊 Migration Status")
        print("=" * 70)

        try:
            # Get current version
            result = subprocess.run(
                ['alembic', 'current'],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get status: {e.stderr}")

        # Show database info
        if self.db_path.exists():
            size_mb = self.db_path.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(self.db_path.stat().st_mtime)
            print(f"Database: {self.db_path}")
            print(f"Size: {size_mb:.2f} MB")
            print(f"Last modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"⚠️  Database file not found: {self.db_path}")

        # Show backups
        backups = sorted(self.backup_dir.glob('data_*.db'))
        if backups:
            print(f"\nBackups: {len(backups)} files")
            print(f"Latest: {backups[-1].name}")
        else:
            print("\n⚠️  No backups found")


def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Database migration management tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s backup              Create database backup
  %(prog)s migrate             Run migrations with automatic backup
  %(prog)s rollback            Rollback to previous version
  %(prog)s status              Show migration status
        """
    )

    parser.add_argument(
        'command',
        choices=['backup', 'migrate', 'rollback', 'status'],
        help='Command to execute'
    )

    args = parser.parse_args()
    manager = MigrationManager()

    if args.command == 'backup':
        try:
            manager.backup_database()
            return 0
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return 1

    elif args.command == 'migrate':
        success = manager.run_migration()
        return 0 if success else 1

    elif args.command == 'rollback':
        success = manager.rollback_migration()
        return 0 if success else 1

    elif args.command == 'status':
        manager.show_status()
        return 0

    return 0


if __name__ == '__main__':
    sys.exit(main())
