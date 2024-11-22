# views/change_credentials_view.py
import tkinter as tk
from tkinter import messagebox
from controllers.authController import AuthController

class ChangeCredentialsView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Change Credentials")
        self.geometry("400x400")
        self.configure(bg="#f0f0f5")

        tk.Label(self, text="Change Credentials", font=("Arial", 16, "bold"), bg="#f0f0f5").pack(pady=20)

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

        tk.Button(self, text="Change Credentials", command=self.change_credentials, bg="#4CAF50", fg="white", width=20).pack(pady=20)

    def change_credentials(self):
        current_username = self.current_username_entry.get()
        current_password = self.current_password_entry.get()
        new_username = self.new_username_entry.get()
        new_password = self.new_password_entry.get()

        try:
            AuthController.change_credentials(current_username, current_password, new_username, new_password)
            messagebox.showinfo("Success", "Credentials updated successfully.", parent=self)
            self.destroy()
            # self.open_dashboard()

        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def open_dashboard(self):
        from views.dashboard_view import DashboardView

        """Ensure the correct appearance is set before opening."""
        dashboard = DashboardView()
        dashboard.configure(bg="#f0f8ff")  # Ensure the correct background color
        dashboard.mainloop()
