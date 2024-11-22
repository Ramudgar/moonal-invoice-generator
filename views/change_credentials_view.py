import tkinter as tk
from tkinter import messagebox
from controllers.authController import AuthController


class ChangeCredentialsView(tk.Toplevel):
    def __init__(self, master=None, is_default_user=False):
        super().__init__(master)
        self.is_default_user = is_default_user  # Flag to indicate if the current user is the default user
        self.title("Change Credentials")
        self.geometry("400x400")
        self.configure(bg="#f0f0f5")

        tk.Label(self, text="Change Credentials", font=(
            "Arial", 16, "bold"), bg="#f0f0f5").pack(pady=20)

        tk.Label(self, text="Current Username", bg="#f0f0f5").pack()
        self.current_username_entry = tk.Entry(self, width=30)
        self.current_username_entry.pack(pady=5)

        tk.Label(self, text="Current Password", bg="#f0f0f5").pack()
        self.current_password_entry = tk.Entry(self, width=30, show="*")
        self.current_password_entry.pack(pady=5)

        tk.Label(self, text="New Username", bg="#f0f0f5").pack()
        self.new_username_entry = tk.Entry(self, width=30)
        self.new_username_entry.pack(pady=5)

        tk.Label(self, text="New Password", bg="#f0f0f5").pack()
        self.new_password_entry = tk.Entry(self, width=30, show="*")
        self.new_password_entry.pack(pady=5)

        tk.Button(self, text="Change Credentials", command=self.change_credentials,
                  bg="#4CAF50", fg="white", width=20).pack(pady=20)

    def change_credentials(self):
        """Handle changing user credentials."""
        current_username = self.current_username_entry.get()
        current_password = self.current_password_entry.get()
        new_username = self.new_username_entry.get()
        new_password = self.new_password_entry.get()

        try:
            # Attempt to change credentials
            AuthController.change_credentials(
                current_username, current_password, new_username, new_password
            )
            messagebox.showinfo(
                "Success", "Credentials updated successfully.", parent=self
            )

            # Handle default user flow
            if self.is_default_user:
                self.destroy()  # Close the ChangeCredentialsView
                self.open_dashboard()  # Open the dashboard for the updated user
            else:
                # Simply destroy the ChangeCredentialsView for non-default users
                self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def open_dashboard(self):
        """Open the dashboard view for the updated user."""
        from views.dashboard_view import DashboardView
        dashboard = DashboardView()
        # dashboard.configure(bg="#f0f8ff")  # Ensure consistent background color
        dashboard.mainloop()
