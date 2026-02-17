"""
DashboardView — KPI cards and quick actions in warm light theme.
Renders inside AppShell content area. Responsive layout.
"""
import tkinter as tk
from tkinter import ttk
from config.settings import Settings
from controllers.product_controller import ProductController


class DashboardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.C = Settings.COLORS

        # Responsive fonts
        try:
            sw = self.winfo_screenwidth()
        except Exception:
            sw = 1920
        self.F = Settings.get_fonts(sw)

        self.configure(bg=self.C["bg"])
        self._build_welcome()
        self._build_kpi_cards()
        self._build_quick_actions()

    def _build_welcome(self):
        top = tk.Frame(self, bg=self.C["bg"], padx=28, pady=20)
        top.pack(fill="x")
        tk.Label(top, text="Welcome Back 👋", font=self.F["h2"],
                 bg=self.C["bg"], fg=self.C["text"]).pack(anchor="w")
        tk.Label(top, text="Here's an overview of your business today.",
                 font=self.F["body"], bg=self.C["bg"], fg=self.C["secondary"]).pack(anchor="w")

    def _build_kpi_cards(self):
        wrapper = tk.Frame(self, bg=self.C["bg"], padx=28)
        wrapper.pack(fill="x")

        try:
            products = ProductController.get_all_products()
        except Exception:
            products = []

        total = len(products)
        categories = len(set(p[6] for p in products if len(p) > 6)) if products else 0
        avg_price = sum(float(p[2]) for p in products) / total if total > 0 else 0
        low_stock = sum(1 for p in products if len(p) > 10 and float(p[10]) < 10) if products else 0

        cards_data = [
            ("Total Products", str(total), "📦", self.C["primary"]),
            ("Categories", str(categories), "📂", self.C["info"]),
            ("Avg Price", f"Rs. {avg_price:,.0f}", "💰", self.C["success"]),
            ("Low Stock", str(low_stock), "⚠️", self.C["danger"] if low_stock > 0 else self.C["muted"]),
        ]

        for i, (title, value, icon, accent) in enumerate(cards_data):
            card = tk.Frame(wrapper, bg="white", padx=20, pady=18,
                            highlightbackground=self.C["border"], highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=(0 if i == 0 else 8, 0))

            # Accent top bar
            bar = tk.Frame(card, bg=accent, height=3)
            bar.pack(fill="x", pady=(0, 10))

            tk.Label(card, text=icon, font=("Segoe UI", 20),
                     bg="white", fg=accent).pack(anchor="w")
            tk.Label(card, text=value, font=("Segoe UI", 22, "bold"),
                     bg="white", fg=self.C["text"]).pack(anchor="w")
            tk.Label(card, text=title, font=self.F["small"],
                     bg="white", fg=self.C["secondary"]).pack(anchor="w")

            # Hover effect
            def on_enter(e, c=card):
                c.config(highlightbackground=self.C["primary"])
            def on_leave(e, c=card):
                c.config(highlightbackground=self.C["border"])
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

    def _build_quick_actions(self):
        section = tk.Frame(self, bg=self.C["bg"], padx=28, pady=20)
        section.pack(fill="x")
        tk.Label(section, text="Quick Actions", font=self.F["h3"],
                 bg=self.C["bg"], fg=self.C["text"]).pack(anchor="w", pady=(0, 12))

        grid = tk.Frame(section, bg=self.C["bg"])
        grid.pack(fill="x")

        actions = [
            ("📄", "New Invoice", "Create a new invoice", self.controller.show_invoice_generator, self.C["primary"]),
            ("🛒", "Products", "Manage product catalog", self.controller.show_product_manager, self.C["info"]),
            ("👥", "Customers", "View customer list", self.controller.show_customer_manager, self.C["success"]),
            ("📂", "History", "Browse past invoices", self.controller.show_invoice_history, self.C["warning"]),
            ("📈", "Reports", "Revenue & analytics", self.controller.show_reports, "#8B5CF6"),
        ]

        for i, (icon, title, desc, cmd, accent) in enumerate(actions):
            card = tk.Frame(grid, bg="white", padx=16, pady=14, cursor="hand2",
                            highlightbackground=self.C["border"], highlightthickness=1)
            card.grid(row=0, column=i, padx=(0 if i == 0 else 6, 0), sticky="nsew")
            grid.grid_columnconfigure(i, weight=1)

            # Accent left bar
            tk.Frame(card, bg=accent, width=3).pack(side="left", fill="y", padx=(0, 12))

            inner = tk.Frame(card, bg="white", cursor="hand2")
            inner.pack(fill="both", expand=True)

            tk.Label(inner, text=icon, font=("Segoe UI", 16), bg="white",
                     fg=accent, cursor="hand2").pack(anchor="w")
            tk.Label(inner, text=title, font=self.F["body_bold"], bg="white",
                     fg=self.C["text"], cursor="hand2").pack(anchor="w")
            tk.Label(inner, text=desc, font=self.F["small"], bg="white",
                     fg=self.C["muted"], cursor="hand2").pack(anchor="w")

            # Click + hover
            for w in [card, inner] + inner.winfo_children():
                w.bind("<Button-1>", lambda e, c=cmd: c())

            def on_enter(e, c=card):
                c.config(highlightbackground=self.C["primary"])
            def on_leave(e, c=card):
                c.config(highlightbackground=self.C["border"])
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
