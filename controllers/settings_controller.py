from config.database import connect_db
import sqlite3

class SettingsController:
    @staticmethod
    def get_all_settings():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        settings = {row['key']: row['value'] for row in cursor.fetchall()}
        conn.close()
        return settings

    @staticmethod
    def get_setting(key, default=None):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row['value'] if row else default

    @staticmethod
    def save_settings(settings_dict):
        conn = connect_db()
        cursor = conn.cursor()
        try:
            for key, value in settings_dict.items():
                cursor.execute("""
                    INSERT INTO settings (key, value) VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """, (key, value))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving settings: {e}")
            return False
        finally:
            conn.close()
