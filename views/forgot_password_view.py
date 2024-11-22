import tkinter as tk
from tkinter import messagebox
from controllers.authController import AuthController


class ForgotPasswordView(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Forgot Password - Moonal Udhyog")
        self.geometry("500x550")  # Increased height for better layout
        self.configure(bg="#003366")  # Dark blue background for a professional look

        # Frame for Forgot Password Content
        forgot_frame = tk.Frame(self, bg="#f0f0f5", relief="raised", bd=2)
        forgot_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=500)

        # Title
        tk.Label(
            forgot_frame,
            text="Forgot Password",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f5",
            fg="#003366"
        ).pack(pady=10)

        # Username field
        tk.Label(
            forgot_frame,
            text="Enter Username",
            font=("Arial", 12, "bold"),
            bg="#f0f0f5",
            fg="#003366"
        ).pack(pady=5)
        self.username_entry = tk.Entry(forgot_frame, font=("Arial", 12), width=30)
        self.username_entry.pack(pady=5)

        # PIN 1 field
        tk.Label(
            forgot_frame,
            text="Enter PIN 1",
            font=("Arial", 12, "bold"),
            bg="#f0f0f5",
            fg="#003366"
        ).pack(pady=5)
        self.pin1_entry = tk.Entry(forgot_frame, font=("Arial", 12), width=30, show="*")
        self.pin1_entry.pack(pady=5)

        # PIN 2 field
        tk.Label(
            forgot_frame,
            text="Enter PIN 2",
            font=("Arial", 12, "bold"),
            bg="#f0f0f5",
            fg="#003366"
        ).pack(pady=5)
        self.pin2_entry = tk.Entry(forgot_frame, font=("Arial", 12), width=30, show="*")
        self.pin2_entry.pack(pady=5)

        # New Password field
        tk.Label(
            forgot_frame,
            text="Enter New Password",
            font=("Arial", 12, "bold"),
            bg="#f0f0f5",
            fg="#003366"
        ).pack(pady=5)
        self.new_password_entry = tk.Entry(forgot_frame, font=("Arial", 12), width=30, show="*")
        self.new_password_entry.pack(pady=5)

        # Confirm New Password field
        tk.Label(
            forgot_frame,
            text="Confirm New Password",
            font=("Arial", 12, "bold"),
            bg="#f0f0f5",
            fg="#003366"
        ).pack(pady=5)
        self.confirm_password_entry = tk.Entry(forgot_frame, font=("Arial", 12), width=30, show="*")
        self.confirm_password_entry.pack(pady=5)

        # Reset Password button
        tk.Button(
            forgot_frame,
            text="Reset Password",
            command=self.reset_password,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            relief="groove",
            bd=2
        ).pack(pady=20)

        # Footer Label
        tk.Label(
            self,
            text="Moonal Udhyog PVT. LTD. © 2024 | All Rights Reserved",
            font=("Helvetica", 10),
            bg="#003366",
            fg="#f0f8ff"
        ).pack(side="bottom", pady=10)

    def reset_password(self):
        """Handle the password reset logic."""
        username = self.username_entry.get()
        pin1 = 543210
        pin2 = 852036
        pin1_entry = self.pin1_entry.get()
        pin2_entry = self.pin2_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Validate password fields
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.", parent=self)
            return

        # Check if username exists
        user = AuthController.get_user(username)
        if not user:
            messagebox.showerror("Error", "Username not found.", parent=self)
            return

        # Validate PINs
        if str(pin1) != pin1_entry or str(pin2) != pin2_entry:
            messagebox.showerror("Error", "Invalid PIN 1 or PIN 2.", parent=self)
            return

        # Update password
        AuthController.forgot_password(username, pin1_entry, pin2_entry, new_password)
        messagebox.showinfo("Success", "Password reset successfully. You can now log in.", parent=self)
        self.destroy()
