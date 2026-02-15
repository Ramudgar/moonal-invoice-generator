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
