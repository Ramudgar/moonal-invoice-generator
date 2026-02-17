"""
AppShell — Light-mode application shell with sidebar, navbar, content area.
White sidebar with warm golden accents. Fully responsive.
"""
import tkinter as tk
from tkinter import ttk
from config.settings import Settings
from controllers.authController import AuthController


class AppShell(tk.Frame):
    """Persistent shell: white sidebar + navbar + content area."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.C = Settings.COLORS

        # Responsive: scale fonts & sidebar width for screen
        sw = self.winfo_screenwidth()
        self.sidebar_w, _ = Settings.scale_for_screen(sw)
        self.F = Settings.get_fonts(sw)

        self.configure(bg=self.C["bg"])
        self.active_page = None

        self._build_sidebar()
        self._build_right_panel()
        self._apply_global_styles()

    # ── Sidebar ─────────────────────────────────────────────────────

    def _build_sidebar(self):
        # Outer wrapper with right border
        self.sidebar = tk.Frame(self, bg=self.C["sidebar"], width=self.sidebar_w,
                                highlightbackground=self.C["border"],
                                highlightthickness=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Right edge border
        border_line = tk.Frame(self.sidebar, bg=self.C["sidebar_border"], width=1)
        border_line.pack(side="right", fill="y")

        inner = tk.Frame(self.sidebar, bg=self.C["sidebar"])
        inner.pack(side="left", fill="both", expand=True)

        # ── Brand Header ──
        brand = tk.Frame(inner, bg=self.C["sidebar"], pady=18, padx=16)
        brand.pack(fill="x")
        tk.Label(brand, text="MOONAL", font=("Segoe UI", 18, "bold"),
                 bg=self.C["sidebar"], fg=self.C["primary"]).pack(anchor="w")
        tk.Label(brand, text="UDHYOG PVT. LTD.", font=("Segoe UI", 8),
                 bg=self.C["sidebar"], fg=self.C["muted"]).pack(anchor="w")

        # Divider
        tk.Frame(inner, height=1, bg=self.C["divider"]).pack(fill="x", padx=16, pady=(0, 8))

        # Menu navigation section label
        tk.Label(inner, text="NAVIGATION", font=("Segoe UI", 8, "bold"),
                 bg=self.C["sidebar"], fg=self.C["muted"]).pack(anchor="w", padx=20, pady=(4, 4))

        # ── Menu Items ──
        self.menu_items = {}
        menu_data = [
            ("dashboard",  "📊", "Dashboard",        self.controller.show_dashboard),
            ("invoice",    "📄", "New Invoice",       self.controller.show_invoice_generator),
            ("products",   "🛒", "Products",          self.controller.show_product_manager),
            ("customers",  "👥", "Customers",         self.controller.show_customer_manager),
            ("history",    "📂", "Invoice History",    self.controller.show_invoice_history),
            ("reports",    "📈", "Reports",            self.controller.show_reports),
        ]
        for key, icon, label, cmd in menu_data:
            self._create_menu_item(inner, key, icon, label, cmd)

        # Spacer
        tk.Frame(inner, bg=self.C["sidebar"]).pack(fill="both", expand=True)

        # Bottom section label
        tk.Label(inner, text="SETTINGS", font=("Segoe UI", 8, "bold"),
                 bg=self.C["sidebar"], fg=self.C["muted"]).pack(anchor="w", padx=20, pady=(4, 4))

        if AuthController.is_admin():
            self._create_menu_item(inner, "admin", "🛡️", "Admin Panel",
                                   self.controller.show_admin_panel)
            self._create_menu_item(inner, "system_settings", "⚙️", "System Settings",
                                   self.controller.show_system_settings)

        self._create_menu_item(inner, "security", "🔑", "Security",
                               lambda: self.controller.show_security_settings())

        # Divider
        tk.Frame(inner, height=1, bg=self.C["divider"]).pack(fill="x", padx=16, pady=6)

        # Logout
        logout_frame = tk.Frame(inner, bg=self.C["sidebar"], pady=8, padx=20, cursor="hand2")
        logout_frame.pack(fill="x")
        tk.Label(logout_frame, text="⏻  Logout", font=self.F["sidebar"],
                 bg=self.C["sidebar"], fg="#DC2626", cursor="hand2").pack(anchor="w")
        for w in [logout_frame] + logout_frame.winfo_children():
            w.bind("<Button-1>", lambda e: self.controller.logout())

        # Version footer
        tk.Label(inner, text="v2.0 • Nexpioneer", font=("Segoe UI", 7),
                 bg=self.C["sidebar"], fg=self.C["muted"]).pack(side="bottom", pady=(0, 10))

    def _create_menu_item(self, parent, key, icon, label, command):
        """Create a sidebar menu item with warm hover and golden active state."""
        frame = tk.Frame(parent, bg=self.C["sidebar"], padx=12, cursor="hand2")
        frame.pack(fill="x", pady=1)

        # Left gold indicator (hidden by default)
        indicator = tk.Frame(frame, bg=self.C["sidebar"], width=3, height=32)
        indicator.pack(side="left", padx=(0, 8))

        inner = tk.Frame(frame, bg=self.C["sidebar"], pady=7, padx=4, cursor="hand2")
        inner.pack(fill="x")

        lbl = tk.Label(inner, text=f"{icon}  {label}", font=self.F["sidebar"],
                       bg=self.C["sidebar"], fg=self.C["sidebar_text"], cursor="hand2", anchor="w")
        lbl.pack(fill="x")

        self.menu_items[key] = (frame, indicator, lbl)

        def on_enter(e, f=frame, l=lbl, i=inner):
            if self.active_page != key:
                for w in [f, i, l]:
                    w.config(bg=self.C["sidebar_hover"])

        def on_leave(e, f=frame, l=lbl, i=inner):
            if self.active_page != key:
                for w in [f, i, l]:
                    w.config(bg=self.C["sidebar"])
                l.config(fg=self.C["sidebar_text"])

        def on_click(e):
            command()

        for widget in [frame, inner, lbl]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

    def set_active(self, key):
        """Highlight the active menu item with golden indicator."""
        self.active_page = key
        for k, (frame, indicator, lbl) in self.menu_items.items():
            inner = frame.winfo_children()[1] if len(frame.winfo_children()) > 1 else frame
            if k == key:
                for w in [frame, inner, lbl]:
                    if hasattr(w, 'config'):
                        w.config(bg=self.C["sidebar_active"])
                indicator.config(bg=self.C["primary"])
                lbl.config(bg=self.C["sidebar_active"],
                           fg=self.C["sidebar_text_active"],
                           font=self.F["sidebar_bold"])
            else:
                for w in [frame, inner, lbl]:
                    if hasattr(w, 'config'):
                        w.config(bg=self.C["sidebar"])
                indicator.config(bg=self.C["sidebar"])
                lbl.config(bg=self.C["sidebar"],
                           fg=self.C["sidebar_text"],
                           font=self.F["sidebar"])

    # ── Right Panel (Navbar + Content) ──────────────────────────────

    def _build_right_panel(self):
        right = tk.Frame(self, bg=self.C["bg"])
        right.pack(side="right", fill="both", expand=True)

        # Top Navbar — white with bottom border
        navbar_wrap = tk.Frame(right, bg=self.C["navbar_border"])
        navbar_wrap.pack(fill="x")

        self.navbar = tk.Frame(navbar_wrap, bg=self.C["navbar"], height=Settings.NAVBAR_HEIGHT)
        self.navbar.pack(fill="x", side="top")
        self.navbar.pack_propagate(False)

        # 1px bottom border
        tk.Frame(navbar_wrap, bg=self.C["navbar_border"], height=1).pack(fill="x")

        self.page_title_lbl = tk.Label(self.navbar, text="Dashboard",
                                        font=self.F["h3"],
                                        bg=self.C["navbar"], fg=self.C["text"])
        self.page_title_lbl.pack(side="left", padx=24)

        # User info on right
        user_frame = tk.Frame(self.navbar, bg=self.C["navbar"])
        user_frame.pack(side="right", padx=24)

        user = AuthController.CURRENT_USER or "User"
        role = "Admin" if AuthController.is_admin() else "Staff"
        tk.Label(user_frame, text=f"👤 {user.title()}", font=self.F["body_bold"],
                 bg=self.C["navbar"], fg=self.C["text"]).pack(side="left", padx=(0, 6))
        tk.Label(user_frame, text=f"({role})", font=self.F["small"],
                 bg=self.C["navbar"], fg=self.C["muted"]).pack(side="left")

        # Content area
        self.content = tk.Frame(right, bg=self.C["bg"])
        self.content.pack(fill="both", expand=True)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def set_page_title(self, title):
        self.page_title_lbl.config(text=title)

    def get_content_frame(self):
        return self.content

    # ── Global Styles ───────────────────────────────────────────────

    def _apply_global_styles(self):
        """TTK styles for the warm golden light theme."""
        style = ttk.Style()
        style.theme_use("clam")

        # Primary Gold Button
        style.configure("Gold.TButton",
                         font=self.F["button"], padding=10,
                         background=self.C["primary"], foreground="white",
                         borderwidth=0, focuscolor="none")
        style.map("Gold.TButton",
                   background=[("active", self.C["primary_hover"]),
                               ("pressed", self.C["primary_pressed"]),
                               ("disabled", "#D1D5DB")],
                   foreground=[("disabled", "#9CA3AF")])

        # Danger Button
        style.configure("Danger.TButton",
                         font=self.F["button"], padding=10,
                         background=self.C["danger"], foreground="white",
                         borderwidth=0, focuscolor="none")
        style.map("Danger.TButton",
                   background=[("active", self.C["danger_hover"]),
                               ("disabled", "#D1D5DB")])

        # Ghost (secondary) Button
        style.configure("Ghost.TButton",
                         font=self.F["body"], padding=8,
                         background="#F3F4F6", foreground=self.C["secondary"],
                         borderwidth=0, focuscolor="none")
        style.map("Ghost.TButton",
                   background=[("active", "#E5E7EB")])

        # Info/Accent Button
        style.configure("Pink.TButton",
                         font=self.F["button"], padding=10,
                         background=self.C["info"], foreground="white",
                         borderwidth=0, focuscolor="none")
        style.map("Pink.TButton",
                   background=[("active", "#2563EB"),
                               ("disabled", "#D1D5DB")])

        # Treeview — light headers
        style.configure("Custom.Treeview",
                         background="white",
                         foreground=self.C["text"],
                         rowheight=36,
                         fieldbackground="white",
                         font=self.F["body"],
                         borderwidth=0)
        style.configure("Custom.Treeview.Heading",
                         background="#F3F4F6",
                         foreground=self.C["text"],
                         font=self.F["small_bold"],
                         relief="flat",
                         padding=8)
        style.map("Custom.Treeview.Heading",
                   background=[("active", "#E5E7EB")])
        style.map("Custom.Treeview",
                   background=[("selected", self.C["primary_light"])],
                   foreground=[("selected", self.C["gold_accent"])])

        # Login button style
        style.configure("Login.TButton",
                         font=self.F["button"], padding=12,
                         background=self.C["primary"], foreground="white",
                         borderwidth=0, focuscolor="none")
        style.map("Login.TButton",
                   background=[("active", self.C["primary_hover"])])
