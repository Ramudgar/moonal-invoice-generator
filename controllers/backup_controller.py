import shutil
import os
import glob
from datetime import datetime
from config.database import DB_NAME
from controllers.audit_controller import AuditLogger

class BackupController:
    BACKUP_DIR = os.path.join(os.path.dirname(DB_NAME), "backups")
    MAX_BACKUPS = 10

    @staticmethod
    def ensure_backup_dir():
        if not os.path.exists(BackupController.BACKUP_DIR):
            os.makedirs(BackupController.BACKUP_DIR)

    @staticmethod
    def create_backup(trigger="MANUAL", user="SYSTEM"):
        """
        Create a backup of the current database.
        trigger: 'MANUAL', 'AUTO', 'PRE_RESTORE'
        """
        try:
            BackupController.ensure_backup_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{timestamp}.sqlite"
            dest = os.path.join(BackupController.BACKUP_DIR, filename)
            
            # Using copy2 to preserve metadata
            shutil.copy2(DB_NAME, dest)
            
            AuditLogger.log_action("BACKUP_CREATE", user, f"Trigger: {trigger} | File: {filename}")
            BackupController.cleanup_old_backups()
            return True, filename
        except Exception as e:
            AuditLogger.log_action("BACKUP_FAILED", user, str(e))
            return False, str(e)

    @staticmethod
    def cleanup_old_backups():
        """Keep only the latest MAX_BACKUPS files."""
        try:
            pattern = os.path.join(BackupController.BACKUP_DIR, "backup_*.sqlite")
            files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
            
            if len(files) > BackupController.MAX_BACKUPS:
                for f in files[BackupController.MAX_BACKUPS:]:
                    os.remove(f)
                    print(f"Deleted old backup: {os.path.basename(f)}")
        except Exception as e:
            print(f"Cleanup error: {e}")

    @staticmethod
    def get_available_backups():
        """Return list of backup files sorted by newest first."""
        BackupController.ensure_backup_dir()
        pattern = os.path.join(BackupController.BACKUP_DIR, "backup_*.sqlite")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        return [os.path.basename(f) for f in files]

    @staticmethod
    def list_backups():
        """Return backup info as tuples (filename, date, size) for the admin UI."""
        BackupController.ensure_backup_dir()
        pattern = os.path.join(BackupController.BACKUP_DIR, "backup_*.sqlite")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        result = []
        for f in files:
            filename = os.path.basename(f)
            # Parse date from filename: backup_YYYYMMDD_HHMMSS.sqlite
            try:
                parts = filename.replace("backup_", "").replace(".sqlite", "")
                dt = datetime.strptime(parts, "%Y%m%d_%H%M%S")
                date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                date_str = "Unknown"
            # File size
            try:
                size_bytes = os.path.getsize(f)
                if size_bytes > 1024 * 1024:
                    size_str = f"{size_bytes / (1024*1024):.1f} MB"
                else:
                    size_str = f"{size_bytes / 1024:.0f} KB"
            except Exception:
                size_str = "?"
            result.append((filename, date_str, size_str))
        return result

    @staticmethod
    def restore_backup(filename, user):
        """
        Restore the database from a backup file.
        WARNING: This overwrites the current database.
        """
        backup_path = os.path.join(BackupController.BACKUP_DIR, filename)
        if not os.path.exists(backup_path):
            return False, "Backup file not found."

        try:
            # 1. Create a safety backup of current state
            BackupController.create_backup("PRE_RESTORE", user)
            
            # 2. Restore (Copy backup to DB_NAME)
            # Assuming all connections are closed by caller or transient
            shutil.copy2(backup_path, DB_NAME)
            
            AuditLogger.log_action("RESTORE_SUCCESS", user, f"Restored from {filename}")
            return True, "Database restored successfully. Please restart the application."
        except Exception as e:
            AuditLogger.log_action("RESTORE_FAILED", user, str(e))
            return False, f"Restore failed: {e}"
