import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from controllers.authController import AuthController
from controllers.backup_controller import BackupController
from controllers.audit_controller import AuditLogger
from config.database import DB_NAME
import os

class AdminView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.COLORS = controller.COLORS
        self.configure(bg=self.COLORS["bg"])
        
        self.current_user = AuthController.CURRENT_USER
        
        # Verify Admin (Double check)
        if not AuthController.is_admin():
            messagebox.showerror("Access Denied", "You do not have permission to access the Admin Panel.")
            self.controller.show_dashboard()
            return

        self._build_header()
        
        # Notebook for Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_users = tk.Frame(self.notebook, bg="white")
        self.tab_backups = tk.Frame(self.notebook, bg="white")
        self.tab_audit = tk.Frame(self.notebook, bg="white")
        
        self.notebook.add(self.tab_users, text="👥 User Management")
        self.notebook.add(self.tab_backups, text="💾 Backup & Restore")
        self.notebook.add(self.tab_audit, text="📝 Audit Logs")
        
        self._build_users_tab()
        self._build_backups_tab()
        self._build_audit_tab()

    def _build_header(self):
        header = tk.Frame(self, bg=self.COLORS["primary"], padx=20, pady=15)
        header.pack(fill="x")
        ttk.Button(header, text="← DASHBOARD", command=self.controller.show_dashboard).pack(side="left")
        tk.Label(header, text="🛡️ ADMIN PANEL", font=("Segoe UI", 16, "bold"), 
                 bg=self.COLORS["primary"], fg="white").pack(side="left", padx=20)
        tk.Label(header, text=f"Logged in as: {self.current_user}", 
                 font=("Segoe UI", 10), bg=self.COLORS["primary"], fg="#E0E0E0").pack(side="right")

    # ─── USER MANAGEMENT ───
    def _build_users_tab(self):
        toolbar = tk.Frame(self.tab_users, bg="white", pady=10)
        toolbar.pack(fill="x", padx=10)
        ttk.Button(toolbar, text="+ Add User", command=self.add_user_dialog).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Reset Password", command=self.reset_user_pass).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Delete User", command=self.delete_user).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Refresh", command=self.load_users).pack(side="right", padx=5)
        
        cols = ("ID", "Username", "Role", "Created At")
        self.user_tree = ttk.Treeview(self.tab_users, columns=cols, show="headings")
        for c in cols: self.user_tree.heading(c, text=c)
        self.user_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_users()

    def load_users(self):
        for i in self.user_tree.get_children(): self.user_tree.delete(i)
        users = AuthController.get_all_users()
        for u in users:
            self.user_tree.insert("", "end", values=(u[0], u[1], u[2], u[3]))

    def add_user_dialog(self):
        # Custom Dialog for Add User
        dialog = tk.Toplevel(self)
        dialog.title("Add User")
        dialog.geometry("300x250")
        
        tk.Label(dialog, text="Username:").pack(pady=5)
        u_entry = tk.Entry(dialog); u_entry.pack()
        
        tk.Label(dialog, text="Password:").pack(pady=5)
        p_entry = tk.Entry(dialog, show="*"); p_entry.pack()
        
        tk.Label(dialog, text="Role:").pack(pady=5)
        role_var = tk.StringVar(value="user")
        ttk.Combobox(dialog, textvariable=role_var, values=["user", "admin"], state="readonly").pack()
        
        def save():
            u, p, r = u_entry.get(), p_entry.get(), role_var.get()
            if not u or not p: return messagebox.showerror("Error", "Missing fields")
            success, msg = AuthController.create_user(u, p, r)
            if success:
                messagebox.showinfo("Success", msg)
                self.load_users()
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg)
                
        ttk.Button(dialog, text="Create", command=save).pack(pady=20)

    def delete_user(self):
        sel = self.user_tree.selection()
        if not sel: return
        item = self.user_tree.item(sel[0])
        username = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Delete user {username}?"):
            success, msg = AuthController.delete_user(username)
            if success:
                self.load_users()
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)

    def reset_user_pass(self):
        sel = self.user_tree.selection()
        if not sel: return
        item = self.user_tree.item(sel[0])
        username = item['values'][1]
        
        new_pass = simpledialog.askstring("Reset Password", f"Enter new password for {username}:", show='*')
        if new_pass:
            AuthController.change_password_admin(username, new_pass)
            messagebox.showinfo("Success", "Password updated.")

    # ─── BACKUP MANAGEMENT ───
    def _build_backups_tab(self):
        toolbar = tk.Frame(self.tab_backups, bg="white", pady=10)
        toolbar.pack(fill="x", padx=10)
        ttk.Button(toolbar, text="Create Backup Now", command=self.create_backup).pack(side="left", padx=5)
        ttk.Button(toolbar, text="⚡ RESTORE SELECTED", command=self.restore_backup).pack(side="left", padx=5)
        
        # Danger Zone
        ttk.Button(toolbar, text="⚠️ RESET DATABASE", command=self.reset_database).pack(side="right", padx=5)
        
        cols = ("Filename",)
        self.backup_tree = ttk.Treeview(self.tab_backups, columns=cols, show="headings")
        self.backup_tree.heading("Filename", text="Backup File")
        self.backup_tree.column("Filename", width=400)
        self.backup_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_backups()

    def load_backups(self):
        for i in self.backup_tree.get_children(): self.backup_tree.delete(i)
        for f in BackupController.get_available_backups():
            self.backup_tree.insert("", "end", values=(f,))

    def create_backup(self):
        success, msg = BackupController.create_backup("MANUAL", self.current_user)
        if success:
            self.load_backups()
            messagebox.showinfo("Success", "Backup created successfully.")
        else:
            messagebox.showerror("Error", msg)

    def restore_backup(self):
        sel = self.backup_tree.selection()
        if not sel: return
        filename = self.backup_tree.item(sel[0])['values'][0]
        
        if not messagebox.askyesno("⚠️ DANGER: RESTORE", 
                                   f"Are you sure you want to restore {filename}?\n\n"
                                   "This will OVERWRITE the current database.\n"
                                   "The application will need to restart."):
            return
            
        success, msg = BackupController.restore_backup(filename, self.current_user)
        if success:
            messagebox.showinfo("Restore Complete", msg)
            self.controller.destroy() # Exit app to force restart/reload
        else:
            messagebox.showerror("Restore Failed", msg)

    def reset_database(self):
        if not messagebox.askyesno("⚠️ CRITICAL WARNING", 
                                   "Are you sure you want to RESET the database?\n"
                                   "ALL DATA WILL BE LOST.\n\n"
                                   "This action cannot be undone."):
            return
            
        # Admin Password Confirmation
        pwd = simpledialog.askstring("Security Check", "Enter Admin Password to confirm:", show='*')
        if not pwd or not AuthController.authenticate(self.current_user, pwd):
            return messagebox.showerror("Authentication Failed", "Incorrect password.")
            
        # Pre-reset backup
        BackupController.create_backup("PRE_RESET", self.current_user)
        
        # Simple implementation: Delete DB file and exit
        try:
            os.remove(DB_NAME)
            messagebox.showinfo("Reset Complete", "Database deleted. Application will now close.\nRestart to initialize a fresh database.")
            self.controller.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ─── AUDIT LOGS ───
    def _build_audit_tab(self):
        cols = ("Timestamp", "Action", "User", "Details")
        self.audit_tree = ttk.Treeview(self.tab_audit, columns=cols, show="headings")
        self.audit_tree.heading("Timestamp", text="Time"); self.audit_tree.column("Timestamp", width=140)
        self.audit_tree.heading("Action", text="Action"); self.audit_tree.column("Action", width=120)
        self.audit_tree.heading("User", text="User"); self.audit_tree.column("User", width=100)
        self.audit_tree.heading("Details", text="Details"); self.audit_tree.column("Details", width=300)
        
        self.audit_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Button(self.tab_audit, text="Refresh Logs", command=self.load_logs).pack(pady=5)
        self.load_logs()

    def load_logs(self):
        for i in self.audit_tree.get_children(): self.audit_tree.delete(i)
        for log in AuditLogger.get_logs(100):
            # log: id, action, performed_by, details, timestamp
            # We want: timestamp, action, performed_by, details
            self.audit_tree.insert("", "end", values=(log[4], log[1], log[2], log[3]))
