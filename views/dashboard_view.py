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

        self.configure(bg="#E8B74D")  # Golden hue for the main background

        # Title label with updated styling
        self.create_title()

        # Navigation buttons with modern design
        self.create_button_frame()

        # Footer section
        self.create_footer()

    def create_title(self):
        """Creates a styled title section."""
        title_frame = tk.Frame(self, bg="#E8B74D")
        title_frame.pack(pady=40)

        title_label = tk.Label(
            title_frame,
            text="🌟 Manage Your Invoices 🌟",
            font=("Helvetica", 24, "bold"),
            bg="#E8B74D",  # Matches the main background
            fg="#4B3E2F",  # Dark brown for readability
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Simplify Your Business Operations",
            font=("Helvetica", 14),
            bg="#E8B74D",
            fg="#6B4226"  # Slightly lighter brown for the subtitle
        )
        subtitle_label.pack()

    def create_button_frame(self):
        """Creates and displays the button frame for navigation."""
        button_frame = tk.Frame(self, bg="#FFF8E1", relief="solid", bd=2)  # Light cream for button frame
        button_frame.place(relx=0.5, rely=0.55, anchor="center")  # Centered in the screen

        # Define button styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dashboard.TButton",
            font=("Helvetica", 14, "bold"),
            padding=15,
            width=30,
            foreground="#FFFFFF",  # White text for readability
            background="#6B4226",  # Dark brown button background
            borderwidth=3,
        )
        style.map(
            "Dashboard.TButton",
            background=[("active", "#4B3E2F")],  # Darker brown on hover
            foreground=[("active", "#FFFFFF")],  # White text on hover
        )

        # Buttons for navigation
        ttk.Button(
            button_frame,
            text="🛒 Manage Products",
            style="Dashboard.TButton",
            command=self.open_product_view
        ).grid(row=0, column=0, padx=20, pady=15)

        ttk.Button(
            button_frame,
            text="📄 Generate New Invoice",
            style="Dashboard.TButton",
            command=self.open_invoice_view
        ).grid(row=1, column=0, padx=20, pady=15)

        ttk.Button(
            button_frame,
            text="📂 View Past Invoices",
            style="Dashboard.TButton",
            command=self.view_invoices
        ).grid(row=2, column=0, padx=20, pady=15)

        ttk.Button(
            button_frame,
            text="🔒 Change Password",
            style="Dashboard.TButton",
            command=self.change_password
        ).grid(row=3, column=0, padx=20, pady=15)

    def create_footer(self):
        """Creates the footer with company information."""
        footer_frame = tk.Frame(self, bg="#E8B74D")  # Matches the main background
        footer_frame.pack(side="bottom", fill="x")
        footer_label = tk.Label(
            footer_frame,
            text="Moonal Udhyog PVT. LTD. © 2024 | All Rights Reserved",
            font=("Helvetica", 10),
            bg="#E8B74D",  # Matches the footer background
            fg="#4B3E2F"  # Darker brown for footer text
        )
        footer_label.pack(pady=10)

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


# Uncomment below to run independently for testing
# if __name__ == "__main__":
#     app = DashboardView()
#     app.mainloop()
