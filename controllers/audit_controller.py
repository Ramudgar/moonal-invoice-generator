import sqlite3
from datetime import datetime
from config.database import connect_db

class AuditLogger:
    @staticmethod
    def log_action(action, performed_by, details=""):
        """
        Log a critical action to the audit_log table.
        Args:
            action (str): The action performed (e.g., 'LOGIN', 'RESET_DB').
            performed_by (str): Username of the actor.
            details (str): Additional context.
        """
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (action, performed_by, details, timestamp)
                VALUES (?, ?, ?, ?)
            """, (action, performed_by, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            print(f"[AUDIT] {action} by {performed_by}")
        except Exception as e:
            print(f"[AUDIT ERROR] Failed to log action: {e}")

    @staticmethod
    def get_logs(limit=100):
        """Fetch latest audit logs."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,))
        logs = cursor.fetchall()
        conn.close()
        return logs
