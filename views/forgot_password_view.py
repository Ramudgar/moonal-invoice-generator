import tkinter as tk
from tkinter import ttk, messagebox
from controllers.authController import AuthController

class ForgotPasswordView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.COLORS = controller.COLORS
        self.configure(bg=self.COLORS["bg"])

        # Header
        header = tk.Frame(self, bg=self.COLORS["primary"], padx=20, pady=10)
        header.pack(fill="x")
        ttk.Button(header, text="← BACK", command=self.controller.show_login).pack(side="left")
        tk.Label(header, text="RECOVER ACCESS", font=("Segoe UI", 16, "bold"), bg=self.COLORS["primary"], fg="white").pack(side="left", padx=20)

        # Content Card
        card = tk.Frame(self, bg="white", highlightbackground="#E0E0E0", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=650)

        # Title
        tk.Label(
            card,
            text="ACCOUNT RECOVERY",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg=self.COLORS["primary"]
        ).pack(pady=(30, 20))

        def create_field(label, show=None):
            tk.Label(card, text=label, font=("Segoe UI", 8, "bold"), bg="white", fg=self.COLORS["secondary"]).pack(anchor="w", padx=40)
            e = tk.Entry(card, font=("Segoe UI", 10), width=35, bg="#F8F9FA", highlightthickness=1, highlightbackground="#D1D1D1", relief="flat")
            if show: e.config(show=show)
            e.pack(pady=(2, 12), ipady=5, padx=40)
            return e

        self.username_entry = create_field("USERNAME")
        self.pin1_entry = create_field("SECURITY PIN 1", "•")
        self.pin2_entry = create_field("SECURITY PIN 2", "•")
        self.new_password_entry = create_field("NEW PASSWORD", "•")
        self.confirm_password_entry = create_field("CONFIRM PASSWORD", "•")

        # Reset button
        tk.Button(
            card,
            text="RESET PASSWORD",
            command=self.reset_password,
            font=("Segoe UI", 11, "bold"),
            bg=self.COLORS["primary"],
            fg="white",
            relief="flat",
            activebackground=self.COLORS["accent"],
            activeforeground="white",
            cursor="hand2"
        ).pack(pady=20, fill="x", padx=40, ipady=5)

        # Footer Label
        tk.Label(
            self,
            text="Moonal Udhyog © 2024 | Secure Administration",
            font=("Segoe UI", 10),
            bg=self.COLORS["bg"],
            fg="#9E9E9E"
        ).pack(side="bottom", pady=20)

    def reset_password(self):
        """Handle the password reset logic."""
        username = self.username_entry.get()
        pin1 = 543210
        pin2 = 852036
        pin1_e = self.pin1_entry.get()
        pin2_e = self.pin2_entry.get()
        new_p = self.new_password_entry.get()
        conf_p = self.confirm_password_entry.get()

        if new_p != conf_p:
            return messagebox.showerror("Error", "Passwords do not match.")

        # Validate PINs
        if str(pin1) != pin1_e or str(pin2) != pin2_e:
            return messagebox.showerror("Error", "Invalid Security PINs.")

        try:
            AuthController.forgot_password(username, pin1_e, pin2_e, new_p)
            messagebox.showinfo("Success", "Password reset successfully. You can now log in.")
            self.controller.show_login()
        except Exception as e:
            messagebox.showerror("Error", str(e))
