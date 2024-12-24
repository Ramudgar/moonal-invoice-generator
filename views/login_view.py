import tkinter as tk
from tkinter import messagebox
from controllers.authController import AuthController
from views.dashboard_view import DashboardView
from views.change_credentials_view import ChangeCredentialsView
from views.forgot_password_view import ForgotPasswordView

class LoginView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - Moonal Udhyog PVT. LTD.")

        # Set the window to the screen size (manual maximization)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")

        self.configure(bg="#E8B74D")  # Warm golden background

        self.is_default_user = AuthController.is_default_user()

        # Frame for Login Content
        login_frame = tk.Frame(self, bg="#FFF8E1", relief="raised", bd=2)  # Light complementary color
        login_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=400)

        # Title
        tk.Label(
            login_frame,
            text="Welcome to Moonal Udhyog",
            font=("Helvetica", 16, "bold"),
            bg="#FFF8E1",
            fg="#2B2B2B"  # Dark gray text
        ).pack(pady=20)

        # Username field
        tk.Label(
            login_frame, text="Username", font=("Arial", 12, "bold"), bg="#FFF8E1", fg="#2B2B2B"
        ).pack(pady=5)
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12), width=30)
        self.username_entry.pack(pady=5)

        # Password field
        tk.Label(
            login_frame, text="Password", font=("Arial", 12, "bold"), bg="#FFF8E1", fg="#2B2B2B"
        ).pack(pady=5)
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), width=30, show="*")
        self.password_entry.pack(pady=5)

        # Login button
        tk.Button(
            login_frame,
            text="Login",
            command=self.login,
            bg="#388E3C",  # Dark green for buttons
            fg="white",  # White text
            font=("Arial", 12, "bold"),
            width=20,
            relief="groove",
            bd=2
        ).pack(pady=15)

        # Forgot Password button
        tk.Button(
            login_frame,
            text="Forgot Password?",
            command=self.open_forgot_password,
            bg="#F57C00",  # Deep orange for "Forgot Password"
            fg="white",  # White text
            font=("Arial", 10, "bold"),
            relief="flat"
        ).pack(pady=5)

        # Footer Label
        tk.Label(
            self,
            text="Moonal Udhyog PVT. LTD. © 2024",
            font=("Helvetica", 10),
            bg="#E8B74D",  # Same as main background
            fg="#2B2B2B"  # Dark text for footer
        ).pack(side="bottom", pady=10)


    def login(self):
        """Handle login logic."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if AuthController.authenticate(username, password):
            # Check if the user is using default credentials
            if username == "moonal@invoice" and password == "invoice@user":
                if self.is_default_user:
                    # Enforce username and password change for default user
                    messagebox.showinfo(
                        "Default Credentials",
                        "You are using default credentials. Please update your username and password.",
                    )
                    self.hide()
                    self.open_change_credentials_view(self.is_default_user)
            else:
                # Open the dashboard for updated credentials
                self.destroy()
                self.open_dashboard()
        else:
            messagebox.showerror(
                "Login Failed", "Invalid username or password.", parent=self
            )

    def open_dashboard(self):
        """Open the dashboard after successful login."""
        dashboard = DashboardView()
        dashboard.mainloop()

    def open_change_credentials_view(self, is_default_user=False):
        """Open the view to change username and password."""
        change_credentials_view = ChangeCredentialsView(is_default_user=is_default_user)
        self.wait_window(change_credentials_view)  # Wait for the window to close
        if not is_default_user:
            self.open_dashboard()
        else:
            self.show()  # Show the login view again if default credentials were updated

    def open_forgot_password(self):
        """Open the Forgot Password window."""
        forgot_password_view = ForgotPasswordView()
        forgot_password_view.mainloop()

    def hide(self):
        """Hide the login window."""
        self.withdraw()

    def show(self):
        """Show the login window."""
        self.deiconify()
