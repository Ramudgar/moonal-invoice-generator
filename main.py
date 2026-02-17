# main.py
import tkinter as tk
from config.database import create_tables
from controllers.authController import AuthController
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.invoice_view import InvoiceView
from views.product_view import ProductView
from views.invoice_management_view import InvoiceManagementView
from views.change_credentials_view import ChangeCredentialsView
from views.forgot_password_view import ForgotPasswordView
from views.settings_view import SettingsView
from views.reports_view import ReportsView
from views.app_shell import AppShell
from controllers.backup_controller import BackupController
from views.admin_view import AdminView
from views.customer_view import CustomerView
from config.settings import Settings


class MoonalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.title(Settings.APP_NAME)

        # Fullscreen
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"{screen_w}x{screen_h}")

        self.COLORS = Settings.COLORS
        self.configure(bg=self.COLORS["bg"])

        # Main container
        self.container = tk.Frame(self, bg=self.COLORS["bg"])
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.shell = None  # AppShell reference (created after login)
        self.show_login()

    # ── Login (Full Screen, no sidebar) ─────────────────────────────

    def show_login(self):
        self.shell = None
        self._clear()
        frame = LoginView(self.container, self)
        frame.pack(fill="both", expand=True)
        self.container.update()
        self.update_idletasks()

    def logout(self):
        AuthController.CURRENT_USER = None
        AuthController.CURRENT_ROLE = None
        # Use after(1) to avoid destroying widgets during their own click handler context
        self.after(1, self.show_login)

    # ── Shell Bootstrap (after login) ───────────────────────────────

    def _ensure_shell(self):
        """Create the sidebar shell if it doesn't exist yet."""
        if self.shell is None:
            self._clear()
            self.shell = AppShell(self.container, self)
            self.shell.pack(fill="both", expand=True)

    def _show_in_shell(self, sidebar_key, page_title, frame_class, **kwargs):
        """Generic method to show a view inside the AppShell content area."""
        self._ensure_shell()
        # Clear content area
        for w in self.shell.get_content_frame().winfo_children():
            w.destroy()
        # Create and place the view
        frame = frame_class(self.shell.get_content_frame(), self, **kwargs)
        frame.grid(row=0, column=0, sticky="nsew")
        # Update sidebar highlight and navbar title
        self.shell.set_active(sidebar_key)
        self.shell.set_page_title(page_title)

    # ── Navigation Methods ──────────────────────────────────────────

    def show_dashboard(self):
        self._show_in_shell("dashboard", "Dashboard", DashboardView)

    def show_invoice_generator(self, **kwargs):
        self._show_in_shell("invoice", "New Invoice", InvoiceView, **kwargs)

    def show_product_manager(self):
        self._show_in_shell("products", "Product Catalog", ProductView)

    def show_customer_manager(self):
        self._show_in_shell("customers", "Customer Management", CustomerView)

    def show_invoice_history(self):
        self._show_in_shell("history", "Invoice History", InvoiceManagementView)

    def show_reports(self):
        self._show_in_shell("reports", "Reports", ReportsView)

    def show_system_settings(self):
        self._show_in_shell("system_settings", "System Settings", SettingsView)

    def show_admin_panel(self):
        self._show_in_shell("admin", "Admin Panel", AdminView)

    def show_security_settings(self, is_default_user=False):
        self._show_in_shell("security", "Security Settings", ChangeCredentialsView,
                            is_default_user=is_default_user)

    def show_forgot_password(self):
        """Full screen (no shell) — only from login."""
        self.shell = None
        self._clear()
        frame = ForgotPasswordView(self.container, self)
        frame.pack(fill="both", expand=True)

    # ── Utility ─────────────────────────────────────────────────────

    def _clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def on_close(self):
        print("Creating auto-backup...")
        BackupController.create_backup("APP_EXIT", "SYSTEM")
        self.destroy()


def main():
    create_tables()
    AuthController.initialize_users()
    app = MoonalApp()
    app.mainloop()


if __name__ == "__main__":
    main()
