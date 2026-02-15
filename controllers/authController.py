import hashlib
import sqlite3
from config.database import connect_db
from controllers.audit_controller import AuditLogger

class AuthController:
    CURRENT_USER = None
    CURRENT_ROLE = None

    @staticmethod
    def _hash_password(password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def initialize_users():
        """Create default Admin and standard User if none exist."""
        conn = connect_db()
        cursor = conn.cursor()
        
        # Check if any users exist
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Create Default Admin
            admin_pass = AuthController._hash_password("admin123")
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                           ("admin", admin_pass, "admin"))
            
            # Create Default User
            user_pass = AuthController._hash_password("invoice@user")
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                           ("moonal@invoice", user_pass, "user"))
            
            conn.commit()
            AuditLogger.log_action("SYSTEM_INIT", "SYSTEM", "Created default users")
            print("Default users initialized.")
        conn.close()

    @staticmethod
    def authenticate(username, password):
        """Verify credentials and set session."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row:
            stored_hash, role = row
            if AuthController._hash_password(password) == stored_hash:
                AuthController.CURRENT_USER = username
                AuthController.CURRENT_ROLE = role
                AuditLogger.log_action("LOGIN", username, "Success")
                return True
        
        AuditLogger.log_action("LOGIN_FAILED", username, "Invalid credentials")
        return False

    @staticmethod
    def get_current_role():
        return AuthController.CURRENT_ROLE

    @staticmethod
    def is_admin():
        return AuthController.CURRENT_ROLE == 'admin'

    @staticmethod
    def logout():
        if AuthController.CURRENT_USER:
            AuditLogger.log_action("LOGOUT", AuthController.CURRENT_USER)
        AuthController.CURRENT_USER = None
        AuthController.CURRENT_ROLE = None

    @staticmethod
    def change_password_admin(username, new_password):
        """Admin force reset password."""
        if not AuthController.is_admin(): return False
        
        new_hash = AuthController._hash_password(new_password)
        conn = connect_db()
        conn.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, username))
        conn.commit()
        conn.close()
        AuditLogger.log_action("ADMIN_PASS_RESET", AuthController.CURRENT_USER, f"Target: {username}")
        return True

    @staticmethod
    def create_user(username, password, role='user'):
        """Create a new user (Admin only)."""
        if not AuthController.is_admin(): return False, "Unauthorized"
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            p_hash = AuthController._hash_password(password)
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                           (username, p_hash, role))
            conn.commit()
            conn.close()
            AuditLogger.log_action("USER_CREATE", AuthController.CURRENT_USER, f"Created {username} ({role})")
            return True, "User created successfully"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_all_users():
        """Get list of users (Admin only)."""
        if not AuthController.is_admin(): return []
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, created_at FROM users")
        users = cursor.fetchall()
        conn.close()
        return users

    @staticmethod
    def delete_user(username):
        """Delete a user (Admin only). Cannot delete self."""
        if not AuthController.is_admin(): return False, "Unauthorized"
        if username == AuthController.CURRENT_USER: return False, "Cannot delete yourself"
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        AuditLogger.log_action("USER_DELETE", AuthController.CURRENT_USER, f"Deleted {username}")
        return True, "User deleted"
