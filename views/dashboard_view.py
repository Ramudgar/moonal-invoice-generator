import tkinter as tk
from tkinter import ttk
from views.product_view import ProductView
from views.invoice_view import InvoiceView
from views.invoice_management_view import InvoiceManagementView
from views.change_credentials_view import ChangeCredentialsView  # Import the Change Credentials View


class DashboardView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Moonal Udhyog PVT. LTD. - Invoice Management System")

        # Manually maximize the window (cross-platform compatible)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")  # Set to full screen dimensions

        self.configure(bg="#003366")  # Match background with login view

        # Title label with updated styling
        title_label = tk.Label(
            self,
            text="Moonal Udhyog PVT. LTD.\nInvoice Management System",
            font=("Helvetica", 18, "bold"),
            bg="#003366",  # Matches the main window background
            fg="#f0f8ff"  # Contrasting white for readability
        )
        title_label.pack(pady=30)

        # Navigation buttons with modern design
        self.create_button_frame()

        # Footer section
        self.create_footer()

    def create_button_frame(self):
        """Creates and displays the button frame for navigation."""
        button_frame = tk.Frame(self, bg="#004080", relief="solid", bd=1)  # Darker blue for button frame
        button_frame.place(relx=0.5, rely=0.5, anchor="center")  # Centered in the screen

        # Define button styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dashboard.TButton",
            font=("Helvetica", 12, "bold"),
            padding=10,
            width=25,
            foreground="#ffffff",
            background="#0059b3",
            borderwidth=2,
        )
        style.map(
            "Dashboard.TButton",
            background=[("active", "#003366")],  # Matches hover to darker blue
            foreground=[("active", "#f0f8ff")],
        )

        # Buttons for navigation
        ttk.Button(
            button_frame,
            text="Manage Products",
            style="Dashboard.TButton",
            command=self.open_product_view
        ).grid(row=0, column=0, padx=20, pady=10)

        ttk.Button(
            button_frame,
            text="Generate New Invoice",
            style="Dashboard.TButton",
            command=self.open_invoice_view
        ).grid(row=1, column=0, padx=20, pady=10)

        ttk.Button(
            button_frame,
            text="View Past Invoices",
            style="Dashboard.TButton",
            command=self.view_invoices
        ).grid(row=2, column=0, padx=20, pady=10)

        ttk.Button(
            button_frame,
            text="Change Password",
            style="Dashboard.TButton",
            command=self.change_password
        ).grid(row=3, column=0, padx=20, pady=10)  # Added Change Password Button

    def create_footer(self):
        """Creates the footer with company information."""
        footer_frame = tk.Frame(self, bg="#003366")
        footer_frame.pack(side="bottom", fill="x")
        footer_label = tk.Label(
            footer_frame,
            text="Moonal Udhyog PVT. LTD. © 2024 | All Rights Reserved",
            font=("Helvetica", 10),
            bg="#003366",
            fg="#f0f8ff"
        )
        footer_label.pack(pady=5)

    def open_product_view(self):
        """Open the product management view."""
        ProductView(self)

    def open_invoice_view(self):
        """Open the invoice generation view."""
        InvoiceView(self)

    def view_invoices(self):
        """Open the past invoices management view."""
        InvoiceManagementView(self)  # Replace with actual implementation

    def change_password(self):
        """Open the Change Password View."""
        ChangeCredentialsView()  # Open the Change Credentials View
