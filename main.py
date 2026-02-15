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
from views.reports_view import ReportsView

from views.reports_view import ReportsView
from controllers.backup_controller import BackupController
from views.admin_view import AdminView

class MoonalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.title("Moonal Udhyog PVT. LTD. - IMS")
        
        # Manually maximize
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        
        self.COLORS = {
            "primary": "#D4AF37",    # Gold
            "accent": "#E91E63",     # Pink
            "bg": "#FFF9FB",         # Soft base
            "text": "#3E2723",       # Dark brown
            "secondary": "#757575",
            "card": "#FFFFFF"        # Added card color to prevent KeyError
        }
        
        self.configure(bg=self.COLORS["bg"])
        
        # Container to hold all frames
        self.container = tk.Frame(self, bg=self.COLORS["bg"])
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        # Initial View
        self.show_login()

    def show_login(self):
        """Show the Login View."""
        self.clear_container()
        frame = LoginView(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames["LoginView"] = frame

    def show_dashboard(self):
        """Show the Dashboard View."""
        self.clear_container()
        frame = DashboardView(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames["DashboardView"] = frame

    def show_invoice_generator(self, **kwargs):
        """Show the Invoice Generator (Wizard)."""
        self.clear_container()
        frame = InvoiceView(self.container, self, **kwargs)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames["InvoiceView"] = frame

    def show_product_manager(self):
        """Show the Product Management View."""
        self.clear_container()
        frame = ProductView(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames["ProductView"] = frame

    def show_invoice_history(self):
        """Show the Invoice History View."""
        self.clear_container()
        frame = InvoiceManagementView(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")

    def show_reports(self):
        """Show the Reports & Analytics View."""
        self.clear_container()
        frame = ReportsView(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames["ReportsView"] = frame

    def show_admin_panel(self):
        """Show the Admin Panel View."""
        self.clear_container()
        frame = AdminView(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames["AdminView"] = frame

    def show_security_settings(self, is_default_user=False):
        """Show the Security Settings View."""
        self.clear_container()
        frame = ChangeCredentialsView(self.container, self, is_default_user=is_default_user)
        frame.grid(row=0, column=0, sticky="nsew")

    def show_forgot_password(self):
        """Show the Forgot Password View."""
        self.clear_container()
        frame = ForgotPasswordView(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")

    def clear_container(self):
        """Remove current frame from container."""
        for widget in self.container.winfo_children():
            widget.destroy()

    def on_close(self):
        """Handle application close event."""
        print("Creating auto-backup...")
        BackupController.create_backup("APP_EXIT", "SYSTEM")
        self.destroy()

def main():
    # Initialize database
    create_tables()
    AuthController.initialize_users()

    # Launch the Moonal App
    app = MoonalApp()
    app.mainloop()

if __name__ == "__main__":
    main()
