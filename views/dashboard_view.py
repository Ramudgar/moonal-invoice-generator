import tkinter as tk
from tkinter import ttk, messagebox
from controllers.authController import AuthController

class DashboardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.COLORS = controller.COLORS
        self.configure(bg=self.COLORS["bg"])

        # Main Container
        self.main_container = tk.Frame(self, bg=self.COLORS["bg"], padx=50, pady=50)
        self.main_container.pack(expand=True, fill="both")

        self.create_header()
        self.create_navigation()
        self.create_footer()

    def create_header(self):
        """Creates a professional header section."""
        header = tk.Frame(self.main_container, bg=self.COLORS["bg"])
        header.pack(fill="x", pady=(0, 40))

        tk.Label(header, text="MOONAL UDHYOG", font=("Segoe UI", 28, "bold"), bg=self.COLORS["bg"], fg=self.COLORS["primary"]).pack()
        tk.Label(header, text="Invoice Management System", font=("Segoe UI", 12), bg=self.COLORS["bg"], fg="#757575").pack()
        
        # Subtle divider
        tk.Frame(header, height=2, width=100, bg=self.COLORS["accent"]).pack(pady=10)

    def create_navigation(self):
        """Creates centered navigation cards."""
        nav_frame = tk.Frame(self.main_container, bg=self.COLORS["bg"])
        nav_frame.pack(expand=True)

        # Style setup
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dashboard.TButton", font=("Segoe UI", 12, "bold"), padding=20, background="white", foreground=self.COLORS["text"])
        style.map("Dashboard.TButton", background=[("active", self.COLORS["primary"])], foreground=[("active", "white")])
        
        buttons = [
            ("🛒  MANAGE PRODUCTS", self.controller.show_product_manager),
            ("📄  GENERATE INVOICE", self.controller.show_invoice_generator),
            ("📂  INVOICE HISTORY", self.controller.show_invoice_history),
            ("📊  REPORTS & ANALYTICS", self.controller.show_reports),
            ("🔑  SECURITY SETTINGS", self.change_password)
        ]

        if AuthController.is_admin():
            buttons.append(("🛡️  ADMIN PANEL", self.controller.show_admin_panel))

        for i, (text, cmd) in enumerate(buttons):
            btn = ttk.Button(nav_frame, text=text, style="Dashboard.TButton", command=cmd, width=35)
            btn.grid(row=i//2, column=i%2, padx=20, pady=20)

    def create_footer(self):
        """Creates a clean footer."""
        footer = tk.Frame(self, bg="white", height=50)
        footer.pack(side="bottom", fill="x")
        
        tk.Label(footer, text="Powered by Nexpioneer Technologies Pvt. Ltd. | Professional Invoice Solutions", 
                 font=("Segoe UI", 9), bg="white", fg="#9E9E9E").pack(pady=15)

    def change_password(self):
        """Navigate to the Security Settings view."""
        self.controller.show_security_settings()
