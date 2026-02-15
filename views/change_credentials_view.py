import tkinter as tk
from tkinter import ttk, messagebox
from controllers.authController import AuthController

class ChangeCredentialsView(tk.Frame):
    def __init__(self, parent, controller, is_default_user=False):
        super().__init__(parent)
        self.controller = controller
        self.is_default_user = is_default_user
        self.COLORS = controller.COLORS
        self.configure(bg=self.COLORS["bg"])

        # Header
        header = tk.Frame(self, bg=self.COLORS["primary"], padx=20, pady=10)
        header.pack(fill="x")
        
        # If default user, they MUST change credentials, so maybe hide back if they aren't done?
        # But user said back/forth button.
        ttk.Button(header, text="← BACK", command=self.controller.show_dashboard if not is_default_user else self.controller.show_login).pack(side="left")
        
        tk.Label(header, text="ACCOUNT SECURITY", font=("Segoe UI", 16, "bold"), bg=self.COLORS["primary"], fg="white").pack(side="left", padx=20)

        # Form Card
        card = tk.Frame(self, bg="white", padx=40, pady=40, highlightbackground="#E0E0E0", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=500, height=500)

        # Form Fields
        def create_field(label, row):
            tk.Label(card, text=label, font=("Segoe UI", 9, "bold"), bg="white", fg=self.COLORS["secondary"]).grid(row=row*2, column=0, sticky="w", pady=(15, 0))
            e = tk.Entry(card, font=("Segoe UI", 11), width=45, bg="#F8F9FA", highlightthickness=1, highlightbackground="#D1D1D1", relief="flat")
            if "PASSWORD" in label: e.config(show="•")
            e.grid(row=row*2+1, column=0, pady=(5, 10), ipady=5)
            return e

        self.current_username_entry = create_field("CURRRENT USERNAME", 0)
        self.current_password_entry = create_field("CURRENT PASSWORD", 1)
        self.new_username_entry = create_field("NEW USERNAME", 2)
        self.new_password_entry = create_field("NEW PASSWORD", 3)

        # Submit Button
        style = ttk.Style()
        style.configure("Security.TButton", font=("Segoe UI", 11, "bold"), background=self.COLORS["primary"], foreground="white")
        
        btn = ttk.Button(card, text="UPDATE CREDENTIALS", style="Security.TButton", command=self.change_credentials)
        btn.grid(row=8, column=0, pady=30, sticky="ew")

        # Footer
        tk.Label(self, text="Moonal Udhyog © 2024 | Secure Administration", 
                 font=("Segoe UI", 10), bg=self.COLORS["bg"], fg="#9E9E9E").pack(side="bottom", pady=20)

    def change_credentials(self):
        """Handle changing user credentials."""
        curr_u = self.current_username_entry.get()
        curr_p = self.current_password_entry.get()
        new_u = self.new_username_entry.get()
        new_p = self.new_password_entry.get()

        try:
            AuthController.change_credentials(curr_u, curr_p, new_u, new_p)
            messagebox.showinfo("Success", "Credentials updated successfully.")
            if self.is_default_user:
                self.controller.show_dashboard()
            else:
                self.controller.show_dashboard()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)
