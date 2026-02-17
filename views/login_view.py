"""
LoginView — Premium split-layout login with warm golden theme.
Full screen (no AppShell). Responsive for 12"–18" screens.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.authController import AuthController
from config.settings import Settings
from datetime import datetime
import nepali_datetime



class LoginView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.C = Settings.COLORS
        self.F = Settings.FONTS
        self.configure(bg="white")
        self._build_ui()

    def _build_ui(self):
        # Responsive: decide left panel width
        try:
            sw = self.winfo_screenwidth()
        except Exception:
            sw = 1920
        left_w = max(360, int(sw * 0.3))

        # ── LEFT PANEL: Warm Golden Branding ────────────────────────
        left = tk.Frame(self, bg="#FDF6E3", width=left_w)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        # Decorative top bar
        tk.Frame(left, bg=self.C["primary"], height=4).pack(fill="x")

        # Brand centered
        brand_frame = tk.Frame(left, bg="#FDF6E3")
        brand_frame.place(relx=0.5, rely=0.4, anchor="center")

        tk.Label(brand_frame, text="MOONAL", font=("Segoe UI", 32, "bold"),
                 bg="#FDF6E3", fg=self.C["primary"]).pack()
        tk.Label(brand_frame, text="UDHYOG PVT. LTD.", font=("Segoe UI", 12),
                 bg="#FDF6E3", fg=self.C["gold_accent"]).pack(pady=(0, 16))

        # Divider
        tk.Frame(brand_frame, bg=self.C["primary"], height=2, width=60).pack(pady=8)

        tk.Label(brand_frame, text="Invoice Management System",
                 font=("Segoe UI", 10), bg="#FDF6E3", fg="#78716C").pack(pady=(8, 0))
        tk.Label(brand_frame, text="Golbazar-4, Siraha, Nepal",
                 font=("Segoe UI", 9), bg="#FDF6E3", fg="#A8A29E").pack()

        # Bottom footer
        tk.Label(left, text="© 2024 Nexpioneer Technologies",
                 font=("Segoe UI", 8), bg="#FDF6E3", fg="#A8A29E").pack(side="bottom", pady=16)

        # ── CLOCK & DATE WIDGET ─────────────────────────────────────
        self.time_label = tk.Label(left, text="", font=("Segoe UI", 48, "bold"),
                                   bg="#FDF6E3", fg=self.C["primary"])
        self.time_label.pack(side="bottom", pady=(0, 10))

        self.date_label = tk.Label(left, text="", font=("Segoe UI", 12),
                                   bg="#FDF6E3", fg=self.C["secondary"], cursor="hand2")
        self.date_label.pack(side="bottom", pady=(0, 20))
        self.date_label.bind("<Button-1>", self._toggle_date_format)

        self.show_nepali_date = False
        self._update_clock()

        # ── RIGHT PANEL: Login Form ────────────────────────────────
        right = tk.Frame(self, bg="white")
        right.pack(side="right", fill="both", expand=True)

        form_w = min(400, int(sw * 0.25))
        form = tk.Frame(right, bg="white")
        form.place(relx=0.5, rely=0.45, anchor="center", width=form_w)

        tk.Label(form, text="Welcome Back", font=("Segoe UI", 20, "bold"),
                 bg="white", fg=self.C["text"]).pack(anchor="w")
        tk.Label(form, text="Sign in to continue to your account",
                 font=self.F["body"], bg="white", fg=self.C["muted"]).pack(anchor="w", pady=(4, 28))

        # Username
        tk.Label(form, text="USERNAME", font=self.F["small_bold"],
                 bg="white", fg=self.C["secondary"]).pack(anchor="w")
        self.username_entry = tk.Entry(form, font=self.F["body"],
                                        bg=self.C["input_bg"], fg=self.C["text"],
                                        relief="flat", highlightthickness=2,
                                        highlightbackground=self.C["input_border"],
                                        highlightcolor=self.C["primary"])
        self.username_entry.pack(fill="x", ipady=8, pady=(4, 16))

        # Password
        tk.Label(form, text="PASSWORD", font=self.F["small_bold"],
                 bg="white", fg=self.C["secondary"]).pack(anchor="w")

        pw_frame = tk.Frame(form, bg=self.C["input_bg"],
                            highlightthickness=2, highlightbackground=self.C["input_border"],
                            highlightcolor=self.C["primary"])
        pw_frame.pack(fill="x", pady=(4, 8))

        self.password_entry = tk.Entry(pw_frame, font=self.F["body"],
                                        bg=self.C["input_bg"], fg=self.C["text"],
                                        relief="flat", show="•", bd=0)
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=4)

        self._show_pw = False
        self.toggle_btn = tk.Label(pw_frame, text="👁", font=("Segoe UI", 11),
                                    bg=self.C["input_bg"], fg=self.C["muted"],
                                    cursor="hand2")
        self.toggle_btn.pack(side="right", padx=8)
        self.toggle_btn.bind("<Button-1>", self._toggle_password)

        # Forgot password link
        forgot = tk.Label(form, text="Forgot password?", font=("Segoe UI", 9),
                           bg="white", fg=self.C["primary"], cursor="hand2")
        forgot.pack(anchor="e", pady=(2, 16))
        forgot.bind("<Button-1>", lambda e: self.controller.show_forgot_password())

        # Login button
        style = ttk.Style()
        style.configure("Login.TButton", font=self.F["button"], padding=12,
                         background=self.C["primary"], foreground="white",
                         borderwidth=0, focuscolor="none")
        style.map("Login.TButton",
                   background=[("active", self.C["primary_hover"])])

        login_btn = ttk.Button(form, text="SIGN IN", style="Login.TButton",
                                command=self.login, cursor="hand2")
        login_btn.pack(fill="x", ipady=2)

        # Loading indicator
        self.loading_lbl = tk.Label(form, text="", font=self.F["small"],
                                     bg="white", fg=self.C["primary"])
        self.loading_lbl.pack(pady=(8, 0))

        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self.login())
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.username_entry.focus_set()

    def _toggle_password(self, event=None):
        self._show_pw = not self._show_pw
        self.password_entry.config(show="" if self._show_pw else "•")
        self.toggle_btn.config(text="🙈" if self._show_pw else "👁")

    def login(self):
        user = self.username_entry.get().strip()
        pw = self.password_entry.get().strip()

        if not user or not pw:
            return messagebox.showwarning("Missing Fields", "Please enter both username and password.")

        self.loading_lbl.config(text="Signing in…")
        self.update_idletasks()

        try:
            if not AuthController.authenticate(user, pw):
                if self.winfo_exists():
                    self.loading_lbl.config(text="")
                messagebox.showerror("Login Failed", "Invalid username or password.")
                return
                
            is_default = (user == "admin" and pw == "admin")
            if is_default:
                self.controller.show_security_settings(is_default_user=True)
            else:
                self.controller.show_dashboard()
                
        except Exception as e:
            if self.winfo_exists():
                self.loading_lbl.config(text="")
            messagebox.showerror("Error", str(e))

    def _update_clock(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("%I:%M %p"))
        
        if self.show_nepali_date:
            try:
                # Convert to Nepali Date
                nd = nepali_datetime.date.from_datetime_date(now.date())
                date_str = f"{nd.year}-{nd.month:02}-{nd.day:02} (BS)"
            except Exception:
                date_str = now.strftime("%A, %B %d, %Y")
        else:
            date_str = now.strftime("%A, %B %d, %Y")
            
        self.date_label.config(text=date_str)
        
        # Update every second
        self.after(1000, self._update_clock)

    def _toggle_date_format(self, event):
        self.show_nepali_date = not self.show_nepali_date
        self._update_clock()
