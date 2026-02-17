"""
AdminView — Admin panel with light golden theme.
Renders inside AppShell content area.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import Settings
from controllers.authController import AuthController
from controllers.backup_controller import BackupController


class AdminView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.C = Settings.COLORS
        self.F = Settings.FONTS
        self.configure(bg=self.C["bg"])
        self._build_ui()

    def _build_ui(self):
        # Tab-like buttons
        tab_bar = tk.Frame(self, bg="white", padx=24, pady=10,
                           highlightbackground=self.C["border"], highlightthickness=1)
        tab_bar.pack(fill="x", padx=24, pady=(16, 0))

        self.tabs = {}
        self.tab_frames = {}

        for key, label in [("users", "👥 Users"), ("backup", "💾 Backups"), ("audit", "📋 Audit Log")]:
            btn = tk.Label(tab_bar, text=label, font=self.F["body_bold"],
                           bg="white", fg=self.C["secondary"], padx=16, pady=6, cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, k=key: self._switch_tab(k))
            self.tabs[key] = btn

        # Content area
        self.content = tk.Frame(self, bg=self.C["bg"], padx=24, pady=16)
        self.content.pack(fill="both", expand=True)

        self._switch_tab("users")

    def _switch_tab(self, key):
        # Update tab styles
        for k, btn in self.tabs.items():
            if k == key:
                btn.config(fg=self.C["primary"],
                           bg=self.C["primary_light"])
            else:
                btn.config(fg=self.C["secondary"], bg="white")

        # Clear content
        for w in self.content.winfo_children():
            w.destroy()

        if key == "users":
            self._build_users_tab()
        elif key == "backup":
            self._build_backup_tab()
        elif key == "audit":
            self._build_audit_tab()

    def _build_users_tab(self):
        card = tk.Frame(self.content, bg="white",
                        highlightbackground=self.C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        toolbar = tk.Frame(card, bg="white", padx=16, pady=12)
        toolbar.pack(fill="x")
        tk.Label(toolbar, text="User Management", font=self.F["h3"],
                 bg="white", fg=self.C["text"]).pack(side="left")
        ttk.Button(toolbar, text="+ Add User", style="Gold.TButton",
                    command=self._add_user_dialog).pack(side="right")

        cols = ("Username", "Role", "Created")
        self.user_tree = ttk.Treeview(card, columns=cols, show="headings",
                                       style="Custom.Treeview")
        self.user_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        for c in cols:
            self.user_tree.heading(c, text=c)
            self.user_tree.column(c, width=150)

        self._load_users()

    def _load_users(self):
        for i in self.user_tree.get_children():
            self.user_tree.delete(i)
        try:
            users = AuthController.get_all_users()
            for u in users:
                self.user_tree.insert("", "end", values=tuple(u))
        except Exception:
            pass

    def _add_user_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add User")
        dialog.geometry("380x360")
        dialog.configure(bg="white")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="New User", font=self.F["h3"],
                 bg="white", fg=self.C["primary"]).pack(pady=(20, 16))

        entries = {}
        for label in ["Username", "Password", "Role (admin/user)"]:
            key = label.split(" ")[0].lower()
            tk.Label(dialog, text=label.upper(), font=self.F["small_bold"],
                     bg="white", fg=self.C["secondary"]).pack(anchor="w", padx=30)
            e = tk.Entry(dialog, font=self.F["body"], bg=self.C["input_bg"],
                         relief="flat", highlightthickness=2,
                         highlightbackground=self.C["input_border"],
                         highlightcolor=self.C["primary"])
            if "password" in label.lower():
                e.config(show="•")
            e.pack(fill="x", padx=30, ipady=5, pady=(2, 10))
            entries[key] = e

        def do_add():
            u = entries["username"].get().strip()
            p = entries["password"].get().strip()
            r = entries["role"].get().strip().lower() or "user"
            if not u or not p:
                return messagebox.showerror("Error", "All fields required.")
            try:
                AuthController.register_user(u, p, r)
                dialog.destroy()
                self._load_users()
                messagebox.showinfo("Success", f"User '{u}' created.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Create User", style="Gold.TButton",
                    command=do_add).pack(fill="x", padx=30, pady=(8, 0))

    def _build_backup_tab(self):
        card = tk.Frame(self.content, bg="white", padx=30, pady=30,
                        highlightbackground=self.C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Database Backups", font=self.F["h3"],
                 bg="white", fg=self.C["text"]).pack(anchor="w", pady=(0, 16))

        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(fill="x", pady=(0, 20))

        ttk.Button(btn_frame, text="Create Backup Now", style="Gold.TButton",
                    command=self._create_backup).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Restore from Backup", style="Danger.TButton",
                    command=self._restore_backup).pack(side="left")

        cols = ("Date", "Trigger", "User", "Size")
        self.backup_tree = ttk.Treeview(card, columns=cols, show="headings",
                                         style="Custom.Treeview")
        self.backup_tree.pack(fill="both", expand=True)
        for c in cols:
            self.backup_tree.heading(c, text=c)

        self._load_backups()

    def _create_backup(self):
        try:
            BackupController.create_backup("MANUAL", AuthController.CURRENT_USER or "admin")
            self._load_backups()
            messagebox.showinfo("Success", "Backup created.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _restore_backup(self):
        sel = self.backup_tree.selection()
        if not sel:
            return messagebox.showinfo("Select", "Select a backup to restore.")
        if messagebox.askyesno("Confirm", "Restore this backup? Current data will be replaced."):
            try:
                values = self.backup_tree.item(sel[0])["values"]
                BackupController.restore_backup(values[0])
                messagebox.showinfo("Restored", "Backup restored. Restart the app.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _load_backups(self):
        for i in self.backup_tree.get_children():
            self.backup_tree.delete(i)
        try:
            backups = BackupController.list_backups()
            for b in backups:
                self.backup_tree.insert("", "end", values=b)
        except Exception:
            pass

    def _build_audit_tab(self):
        card = tk.Frame(self.content, bg="white",
                        highlightbackground=self.C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        toolbar = tk.Frame(card, bg="white", padx=16, pady=12)
        toolbar.pack(fill="x")
        tk.Label(toolbar, text="Audit Log", font=self.F["h3"],
                 bg="white", fg=self.C["text"]).pack(side="left")

        cols = ("Time", "User", "Action", "Details")
        self.audit_tree = ttk.Treeview(card, columns=cols, show="headings",
                                        style="Custom.Treeview")
        self.audit_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        for c in cols:
            self.audit_tree.heading(c, text=c)
            self.audit_tree.column(c, width=150)

        try:
            logs = AuthController.get_audit_logs()
            for l in logs:
                self.audit_tree.insert("", "end", values=l)
        except Exception:
            pass
