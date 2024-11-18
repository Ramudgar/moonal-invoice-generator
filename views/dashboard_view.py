import tkinter as tk
from tkinter import ttk
from views.product_view import ProductView
from views.invoice_view import InvoiceView
from views.invoice_management_view import InvoiceManagementView  # Placeholder for the invoice management view

class DashboardView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Moonal Udhyog PVT. LTD. - Invoice System")
        self.geometry("800x600")
        self.configure(bg="#f0f0f5")  # Light background for better contrast

        # Add title label
        title_label = tk.Label(
            self,
            text="Moonal Udhyog PVT. LTD. Invoice Management System",
            font=("Arial", 16, "bold"),
            bg="#f0f0f5"
        )
        title_label.pack(pady=20)

        # Create a frame for buttons
        button_frame = tk.Frame(self, bg="#f0f0f5")
        button_frame.pack(pady=40)

        # Define button styling
        style = ttk.Style()
        style.configure("Dashboard.TButton", font=("Arial", 12), padding=10, width=20)

        # Buttons for navigation
        product_button = ttk.Button(
            button_frame, text="Manage Products", style="Dashboard.TButton", command=self.open_product_view
        )
        product_button.grid(row=0, column=0, padx=20, pady=10)

        invoice_button = ttk.Button(
            button_frame, text="Generate New Invoice", style="Dashboard.TButton", command=self.open_invoice_view
        )
        invoice_button.grid(row=1, column=0, padx=20, pady=10)

        view_invoice_button = ttk.Button(
            button_frame, text="View Past Invoices", style="Dashboard.TButton", command=self.view_invoices
        )
        view_invoice_button.grid(row=2, column=0, padx=20, pady=10)

        # Footer information
        footer_label = tk.Label(
            self,
            text="Moonal Udhyog PVT. LTD. © 2024 | All Rights Reserved",
            font=("Arial", 10),
            bg="#f0f0f5",
            fg="grey"
        )
        footer_label.pack(side="bottom", pady=10)

    def open_product_view(self):
        """Open the product management view."""
        ProductView(self)

    def open_invoice_view(self):
        """Open the invoice generation view."""
        InvoiceView(self)

    def view_invoices(self):
        """Open the past invoices management view."""
        InvoiceManagementView(self)  # Replace with actual implementation
