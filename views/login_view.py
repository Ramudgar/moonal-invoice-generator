import tkinter as tk
from tkinter import ttk, messagebox
from controllers.authController import AuthController

class LoginView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.COLORS = controller.COLORS
        
        self.configure(bg=self.COLORS["bg"])
        self.configure(bg=self.COLORS["bg"])
        # self.is_default_user = AuthController.is_default_user() # Removed legacy check

        # Login Card
        card = tk.Frame(self, bg="white", highlightbackground="#E0E0E0", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=500)

        # Header Image/Logo space
        header = tk.Frame(card, bg=self.COLORS["primary"], height=8)
        header.pack(fill="x")

        content = tk.Frame(card, bg="white", padx=40, pady=30)
        content.pack(fill="both", expand=True)

        tk.Label(content, text="MOONAL UDHYOG", font=("Segoe UI", 18, "bold"), bg="white", fg=self.COLORS["primary"]).pack(pady=(0, 5))
        tk.Label(content, text="Invoice Management System", font=("Segoe UI", 9), bg="white", fg=self.COLORS["secondary"]).pack(pady=(0, 30))

        # Inputs
        def create_entry(label):
            tk.Label(content, text=label, font=("Segoe UI", 9, "bold"), bg="white", fg=self.COLORS["secondary"]).pack(anchor="w")
            e = tk.Entry(content, font=("Segoe UI", 11), bg="#F8F9FA", relief="flat", highlightthickness=1, highlightbackground="#D1D1D1")
            e.pack(fill="x", pady=(5, 15), ipady=8)
            return e

        self.username_entry = create_entry("USERNAME")
        self.password_entry = create_entry("PASSWORD")
        self.password_entry.configure(show="•")

        # Login button
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Login.TButton", font=("Segoe UI", 11, "bold"), background=self.COLORS["primary"], foreground="white")
        style.map("Login.TButton", background=[("active", self.COLORS["accent"])])
        
        btn = ttk.Button(content, text="SECURE LOGIN", style="Login.TButton", command=self.login)
        btn.pack(fill="x", pady=10, ipady=5)

        # Forgot
        tk.Button(content, text="Forgot Password?", command=self.show_admin_contact, bg="white", fg=self.COLORS["accent"], 
                  font=("Segoe UI", 9), relief="flat", cursor="hand2").pack()

        # Footer
        tk.Label(self, text="Moonal Udhyog PVT. LTD. © 2024 | Secure Administration", 
                 font=("Segoe UI", 8), bg=self.COLORS["bg"], fg="#9E9E9E").pack(side="bottom", pady=20)


    def login(self):
        """Handle login logic."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if AuthController.authenticate(username, password):
            # Check for default credentials (admin/admin123) by hash or just hardcoded check for first login
            # Actually, better to check if it's the default admin and warn
            
            if username == "admin" and password == "admin123":
                 messagebox.showwarning("Security Warning", 
                                        "You are using the default Admin account.\n"
                                        "Please change your password immediately in Security Settings.")
            
            self.controller.show_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.", parent=self)

    def show_admin_contact(self):
        messagebox.showinfo("Forgot Password", "Please contact the system Administrator to reset your password.")

