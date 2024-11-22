# views/login_view.py
import tkinter as tk
from tkinter import messagebox
from controllers.authController import AuthController
from views.dashboard_view import DashboardView
from views.change_credentials_view import ChangeCredentialsView


class LoginView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("400x300")
        self.configure(bg="#f0f0f5")

        tk.Label(self, text="Login", font=("Arial", 16, "bold"), bg="#f0f0f5").pack(pady=20)

        # Username field
        tk.Label(self, text="Username", bg="#f0f0f5").pack()
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        # Password field
        tk.Label(self, text="Password", bg="#f0f0f5").pack()
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        # Login button
        tk.Button(self, text="Login", command=self.login, bg="#4CAF50", fg="white", width=15).pack(pady=20)

    def login(self):
        """Handle login logic."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if AuthController.authenticate(username, password):
            # Destroy the current login view
            self.destroy()

            # Check if the user is using default credentials
            if username == "moonal@invoice" and password == "invoice@user":
                # Enforce username and password change for default user
                messagebox.showinfo(
                    "Default Credentials",
                    "You are using default credentials. Please update your username and password.",
                )
                self.open_change_credentials_view()
            else:
                # Open the dashboard for updated credentials
                self.open_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.", parent=self)

    def open_dashboard(self):
        """Open the dashboard after successful login."""
        dashboard = DashboardView()
        dashboard.mainloop()

    def open_change_credentials_view(self):
        """Open the view to change username and password."""
        change_credentials_view = ChangeCredentialsView()
        change_credentials_view.mainloop()
