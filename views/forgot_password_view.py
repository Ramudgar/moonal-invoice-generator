"""
ForgotPasswordView — Password recovery with light golden theme.
Full screen (no AppShell). Only accessible from login.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.authController import AuthController
from config.settings import Settings


class ForgotPasswordView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.C = Settings.COLORS
        self.F = Settings.FONTS
        self.configure(bg=self.C["bg"])
        self._build_ui()

    def _build_ui(self):
        # Top bar with back button
        top = tk.Frame(self, bg="white", pady=10, padx=16,
                       highlightbackground=self.C["border"], highlightthickness=1)
        top.pack(fill="x")
        back = tk.Label(top, text="← Back to Login", font=self.F["body"],
                        bg="white", fg=self.C["primary"], cursor="hand2")
        back.pack(side="left")
        back.bind("<Button-1>", lambda e: self.controller.show_login())

        # Card
        card = tk.Frame(self, bg="white", padx=40, pady=30,
                        highlightbackground=self.C["border"], highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=420)

        tk.Label(card, text="Account Recovery", font=("Segoe UI", 16, "bold"),
                 bg="white", fg=self.C["primary"]).pack(pady=(0, 8))
        tk.Label(card, text="Enter your credentials and security PINs",
                 font=self.F["small"], bg="white", fg=self.C["muted"]).pack(pady=(0, 20))

        self.entries = {}

        def create_field(label, key, show=None):
            tk.Label(card, text=label, font=self.F["small_bold"],
                     bg="white", fg=self.C["secondary"]).pack(anchor="w")
            e = tk.Entry(card, font=self.F["body"], bg=self.C["input_bg"],
                         relief="flat", highlightthickness=2,
                         highlightbackground=self.C["input_border"],
                         highlightcolor=self.C["primary"])
            if show:
                e.config(show=show)
            e.pack(fill="x", pady=(2, 10), ipady=5)
            self.entries[key] = e

        create_field("USERNAME", "username")
        create_field("SECURITY PIN 1", "pin1", "•")
        create_field("SECURITY PIN 2", "pin2", "•")
        create_field("NEW PASSWORD", "new_pw", "•")
        create_field("CONFIRM PASSWORD", "confirm_pw", "•")

        ttk.Button(card, text="Reset Password", style="Gold.TButton",
                    command=self.reset_password).pack(fill="x", pady=(12, 0), ipady=2)

    def reset_password(self):
        username = self.entries["username"].get()
        pin1 = 543210
        pin2 = 852036
        pin1_e = self.entries["pin1"].get()
        pin2_e = self.entries["pin2"].get()
        new_p = self.entries["new_pw"].get()
        conf_p = self.entries["confirm_pw"].get()

        if new_p != conf_p:
            return messagebox.showerror("Error", "Passwords do not match.")
        if str(pin1) != pin1_e or str(pin2) != pin2_e:
            return messagebox.showerror("Error", "Invalid Security PINs.")

        try:
            AuthController.forgot_password(username, pin1_e, pin2_e, new_p)
            messagebox.showinfo("Success", "Password reset successfully.")
            self.controller.show_login()
        except Exception as e:
            messagebox.showerror("Error", str(e))
