"""
ChangeCredentialsView — Security settings with light golden theme.
Renders inside AppShell content area.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import Settings
from controllers.authController import AuthController


class ChangeCredentialsView(tk.Frame):
    def __init__(self, parent, controller, is_default_user=False, **kwargs):
        super().__init__(parent)
        self.controller = controller
        self.C = Settings.COLORS
        self.F = Settings.FONTS
        self.configure(bg=self.C["bg"])
        self.is_default_user = is_default_user
        self._build_ui()

    def _build_ui(self):
        # Configure grid for centering
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Centered card
        card = tk.Frame(self, bg="white", padx=40, pady=40,
                        highlightbackground=self.C["border"], highlightthickness=1)
        card.grid(row=0, column=0)
        # Force specific width by wrapping or using a frame with width (grid propagates size)
        # But for grid, we can just let intrinsic size work, or strict width
        # Let's add an inner frame with requested width if needed, or just let padding decide.
        # Original width was 440.

        if self.is_default_user:
            warn = tk.Frame(card, bg="#FEF3C7", padx=12, pady=8)
            warn.pack(fill="x", pady=(0, 16))
            tk.Label(warn, text="⚠️  Please change the default password to continue.",
                     font=self.F["small_bold"], bg="#FEF3C7",
                     fg="#92400E").pack(anchor="w")

        tk.Label(card, text="Change Password", font=self.F["h3"],
                 bg="white", fg=self.C["primary"]).pack(anchor="w", pady=(0, 20))

        self.entries = {}
        for label, key in [("Current Password", "current"),
                           ("New Password", "new"),
                           ("Confirm New Password", "confirm")]:
            tk.Label(card, text=label.upper(), font=self.F["small_bold"],
                     bg="white", fg=self.C["secondary"]).pack(anchor="w")
            e = tk.Entry(card, font=self.F["body"], show="•",
                         bg=self.C["input_bg"], relief="flat",
                         highlightthickness=2,
                         highlightbackground=self.C["input_border"],
                         highlightcolor=self.C["primary"])
            e.pack(fill="x", ipady=5, pady=(2, 12))
            self.entries[key] = e

        ttk.Button(card, text="Update Password", style="Gold.TButton",
                    command=self.change_password).pack(fill="x", ipady=2)

    def change_password(self):
        current = self.entries["current"].get()
        new = self.entries["new"].get()
        confirm = self.entries["confirm"].get()

        if not current or not new or not confirm:
            return messagebox.showwarning("Missing", "All fields are required.")
        if new != confirm:
            return messagebox.showerror("Mismatch", "New passwords don't match.")
        if len(new) < 4:
            return messagebox.showerror("Weak", "Password must be at least 4 characters.")

        try:
            user = AuthController.CURRENT_USER
            AuthController.change_password(user, current, new)
            messagebox.showinfo("Success", "Password changed successfully.")
            self.controller.show_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))
