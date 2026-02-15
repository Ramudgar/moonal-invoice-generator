import tkinter as tk
from tkinter import ttk, messagebox
from controllers.product_controller import ProductController


class ProductView(tk.Frame):
    """Premium Product Management view for Moonal Udhyog IMS."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.COLORS = controller.COLORS
        self.configure(bg=self.COLORS["bg"])
        self.selected_product_id = None  # Always stored as int or None

        self._apply_styles()
        self._build_header()
        self._build_stats_bar()
        self._build_content()
        self._refresh_all()

    # ─── Styles ────────────────────────────────────────────────────────

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Treeview styling
        style.configure("Product.Treeview",
                         background="white",
                         foreground=self.COLORS["text"],
                         rowheight=34,
                         fieldbackground="white",
                         font=("Segoe UI", 10))
        style.configure("Product.Treeview.Heading",
                         background=self.COLORS["primary"],
                         foreground="white",
                         font=("Segoe UI", 9, "bold"),
                         relief="flat",
                         padding=6)
        style.map("Product.Treeview.Heading",
                   background=[("active", "#B8960E")])

        # Selection colors for treeview
        style.map("Product.Treeview",
                   background=[("selected", "#D4AF37")],
                   foreground=[("selected", "white")])

        # Buttons
        style.configure("Gold.TButton",
                         font=("Segoe UI", 10, "bold"), padding=8,
                         background=self.COLORS["primary"], foreground="white")
        style.map("Gold.TButton",
                   background=[("active", "#B8960E"), ("disabled", "#E0E0E0")])
        style.configure("Danger.TButton",
                         font=("Segoe UI", 10, "bold"), padding=8,
                         background="#D32F2F", foreground="white")
        style.map("Danger.TButton",
                   background=[("active", "#B71C1C"), ("disabled", "#E0E0E0")])
        style.configure("Pink.TButton",
                         font=("Segoe UI", 10, "bold"), padding=8,
                         background=self.COLORS["accent"], foreground="white")
        style.map("Pink.TButton",
                   background=[("active", "#C2185B"), ("disabled", "#E0E0E0")])
        style.configure("Ghost.TButton",
                         font=("Segoe UI", 10), padding=8,
                         background="#F5F5F5", foreground=self.COLORS["secondary"])
        style.map("Ghost.TButton",
                   background=[("active", "#EEEEEE")])

    # ─── Header ────────────────────────────────────────────────────────

    def _build_header(self):
        header = tk.Frame(self, bg=self.COLORS["primary"], padx=20, pady=12)
        header.pack(fill="x")

        # Left: Back + Title
        left = tk.Frame(header, bg=self.COLORS["primary"])
        left.pack(side="left")
        ttk.Button(left, text="← DASHBOARD", command=self.controller.show_dashboard,
                   style="Ghost.TButton").pack(side="left", padx=(0, 15))
        tk.Label(left, text="PRODUCT CATALOG", font=("Segoe UI", 16, "bold"),
                 bg=self.COLORS["primary"], fg="white").pack(side="left")

        # Right: Search bar
        search_frame = tk.Frame(header, bg=self.COLORS["primary"])
        search_frame.pack(side="right")

        tk.Label(search_frame, text="🔍", font=("Segoe UI", 12),
                 bg=self.COLORS["primary"], fg="white").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                font=("Segoe UI", 11), bg="white", fg=self.COLORS["text"],
                                relief="flat", highlightthickness=2,
                                highlightbackground="#B8960E",
                                highlightcolor="#D4AF37", width=30)
        search_entry.pack(side="left", ipady=4)

    # ─── Stats Bar ─────────────────────────────────────────────────────

    def _build_stats_bar(self):
        self.stats_frame = tk.Frame(self, bg="white", pady=8)
        self.stats_frame.pack(fill="x")

        self.stat_labels = {}
        stats_data = [
            ("total", "📦 TOTAL PRODUCTS", "0"),
            ("categories", "🏷️ CATEGORIES", "0"),
            ("avg_price", "💰 AVG. PRICE", "Rs. 0.00"),
        ]
        for key, title, default in stats_data:
            card = tk.Frame(self.stats_frame, bg="white", padx=30)
            card.pack(side="left", expand=True)
            tk.Label(card, text=title, font=("Segoe UI", 8, "bold"),
                     bg="white", fg=self.COLORS["secondary"]).pack()
            lbl = tk.Label(card, text=default, font=("Segoe UI", 14, "bold"),
                           bg="white", fg=self.COLORS["primary"])
            lbl.pack()
            self.stat_labels[key] = lbl

        # Divider
        tk.Frame(self, height=1, bg="#E0E0E0").pack(fill="x")

    # ─── Main Content ──────────────────────────────────────────────────

    def _build_content(self):
        content = tk.Frame(self, bg=self.COLORS["bg"], padx=25, pady=15)
        content.pack(fill="both", expand=True)

        # ── Left: Form Card ──
        form_card = tk.Frame(content, bg="white", padx=25, pady=20,
                             highlightbackground="#E0E0E0", highlightthickness=1)
        form_card.pack(side="left", fill="y", padx=(0, 15))

        # Title row with mode indicator
        title_row = tk.Frame(form_card, bg="white")
        title_row.pack(fill="x", pady=(0, 15))
        tk.Label(title_row, text="PRODUCT DETAILS", font=("Segoe UI", 12, "bold"),
                 bg="white", fg=self.COLORS["primary"]).pack(side="left")
        self.form_mode_label = tk.Label(title_row, text="  NEW  ", font=("Segoe UI", 8, "bold"),
                                         bg="#E8F5E9", fg="#2E7D32", padx=8, pady=2)
        self.form_mode_label.pack(side="right")

        # Fields
        self.name_entry = self._create_field(form_card, "PRODUCT NAME *", width=35)
        self.hs_code_entry = self._create_field(form_card, "HS CODE", width=35)
        self.price_entry = self._create_field(form_card, "UNIT PRICE (Rs.) *", width=35)
        self.desc_entry = self._create_field(form_card, "DESCRIPTION", width=35)

        # Unit dropdown
        tk.Label(form_card, text="UNIT", font=("Segoe UI", 8, "bold"),
                 bg="white", fg=self.COLORS["secondary"]).pack(anchor="w", pady=(8, 0))
        self.unit_var = tk.StringVar(value="Ltr")
        unit_combo = ttk.Combobox(form_card, textvariable=self.unit_var,
                                  values=ProductController.UNITS,
                                  font=("Segoe UI", 10), state="readonly", width=33)
        unit_combo.pack(fill="x", pady=(2, 8), ipady=4)

        # Category dropdown
        tk.Label(form_card, text="CATEGORY", font=("Segoe UI", 8, "bold"),
                 bg="white", fg=self.COLORS["secondary"]).pack(anchor="w", pady=(4, 0))
        self.cat_var = tk.StringVar(value="Lubricant")
        cat_combo = ttk.Combobox(form_card, textvariable=self.cat_var,
                                 values=ProductController.CATEGORIES,
                                 font=("Segoe UI", 10), state="readonly", width=33)
        cat_combo.pack(fill="x", pady=(2, 8), ipady=4)

        # Action buttons
        btn_frame = tk.Frame(form_card, bg="white")
        btn_frame.pack(fill="x", pady=(15, 5))

        self.add_btn = ttk.Button(btn_frame, text="➕ ADD PRODUCT", style="Gold.TButton",
                                  command=self._add_product)
        self.add_btn.pack(fill="x", pady=(0, 5))

        self.update_btn = ttk.Button(btn_frame, text="✏️ UPDATE PRODUCT", style="Pink.TButton",
                                     command=self._update_product, state="disabled")
        self.update_btn.pack(fill="x", pady=(0, 5))

        self.delete_btn = ttk.Button(btn_frame, text="🗑️ DELETE PRODUCT", style="Danger.TButton",
                                     command=self._delete_product, state="disabled")
        self.delete_btn.pack(fill="x", pady=(0, 5))

        ttk.Button(btn_frame, text="🔄 CLEAR FORM", style="Ghost.TButton",
                   command=self._clear_form).pack(fill="x")

        # ── Right: Table Card ──
        table_card = tk.Frame(content, bg="white", padx=15, pady=15,
                              highlightbackground="#E0E0E0", highlightthickness=1)
        table_card.pack(side="right", fill="both", expand=True)

        # Table header
        table_header = tk.Frame(table_card, bg="white")
        table_header.pack(fill="x", pady=(0, 10))
        tk.Label(table_header, text="INVENTORY LIST", font=("Segoe UI", 12, "bold"),
                 bg="white", fg=self.COLORS["primary"]).pack(side="left")
        self.count_label = tk.Label(table_header, text="0 items", font=("Segoe UI", 9),
                                    bg="white", fg=self.COLORS["secondary"])
        self.count_label.pack(side="right")

        # Treeview
        columns = ("SN", "PID", "Name", "Category", "HS Code", "Unit", "Price")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings",
                                   style="Product.Treeview")

        self.tree.heading("SN", text="S.N.")
        self.tree.heading("PID", text="PID")
        self.tree.heading("Name", text="PRODUCT NAME")
        self.tree.heading("Category", text="CATEGORY")
        self.tree.heading("HS Code", text="HS CODE")
        self.tree.heading("Unit", text="UNIT")
        self.tree.heading("Price", text="PRICE")

        self.tree.column("SN", width=50, anchor="center")
        self.tree.column("PID", width=80, anchor="center")
        self.tree.column("Name", width=220, anchor="w")
        self.tree.column("Category", width=120, anchor="center")
        self.tree.column("HS Code", width=100, anchor="center")
        self.tree.column("Unit", width=70, anchor="center")
        self.tree.column("Price", width=110, anchor="e", minwidth=80)

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Empty state label
        self.empty_label = tk.Label(table_card, text="No products found.\nAdd your first product using the form on the left.",
                                     font=("Segoe UI", 11), bg="white", fg="#BDBDBD", justify="center")

        # Footer
        footer = tk.Frame(self, bg="white", height=40)
        footer.pack(side="bottom", fill="x")
        tk.Label(footer, text="Moonal Udhyog © 2024 | Product Catalog",
                 font=("Segoe UI", 9), bg="white", fg="#9E9E9E").pack(pady=10)

    # ─── Field Helper ──────────────────────────────────────────────────

    def _create_field(self, parent, label, width=35):
        tk.Label(parent, text=label, font=("Segoe UI", 8, "bold"),
                 bg="white", fg=self.COLORS["secondary"]).pack(anchor="w", pady=(8, 0))
        entry = tk.Entry(parent, font=("Segoe UI", 10), bg="#F8F9FA", relief="flat",
                         highlightthickness=1, highlightbackground="#D1D1D1", width=width)
        entry.pack(fill="x", pady=(2, 4), ipady=5)
        return entry

    # ─── Data Loading ──────────────────────────────────────────────────

    def _refresh_all(self):
        """Reload both the table and the stats bar."""
        self._load_products()
        self._refresh_stats()

    def _load_products(self, products=None):
        """Load products into the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        if products is None:
            products = ProductController.get_all_products()

        for i, p in enumerate(products, 1):
            # p = (id, name, price, hs_code, description, unit, category)
            pid, name, price, hs_code, desc, unit, category = p
            tag = "even" if i % 2 == 0 else "odd"
            systematic_pid = f"MU-P{pid:03d}"
            self.tree.insert("", "end", iid=str(pid), values=(
                i, systematic_pid, name, category or "—", hs_code or "—", unit or "Ltr", f"Rs. {float(price):,.2f}"
            ), tags=(tag,))

        # Zebra striping — these should NOT override selection
        self.tree.tag_configure("even", background="white")
        self.tree.tag_configure("odd", background="#F9F9F9")

        # Empty state
        count = len(products)
        self.count_label.config(text=f"{count} item{'s' if count != 1 else ''}")
        if count == 0:
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.empty_label.place_forget()

    def _refresh_stats(self):
        """Update the stats bar."""
        try:
            total, cats, avg = ProductController.get_stats()
            self.stat_labels["total"].config(text=str(total))
            self.stat_labels["categories"].config(text=str(cats))
            self.stat_labels["avg_price"].config(text=f"Rs. {avg:,.2f}")
        except Exception:
            pass

    # ─── Search ────────────────────────────────────────────────────────

    def _on_search(self, *args):
        keyword = self.search_var.get().strip()
        if keyword:
            results = ProductController.search_products(keyword)
            self._load_products(results)
        else:
            self._load_products()

    # ─── Selection ─────────────────────────────────────────────────────

    def _on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        vals = self.tree.item(selected[0], "values")
        # vals = (ID, Name, Category, HS Code, Unit, Price)
        self.selected_product_id = int(vals[0])  # Store as int for DB

        # Populate form
        self._clear_form(reset_mode=False)
        self.name_entry.insert(0, vals[1])

        # Get full product data for description field
        try:
            full = ProductController.get_all_products()
            product = next((p for p in full if p[0] == self.selected_product_id), None)
            if product:
                self.hs_code_entry.insert(0, product[3] or "")
                self.price_entry.insert(0, str(product[2]))
                self.desc_entry.insert(0, product[4] or "")
                self.unit_var.set(product[5] or "Ltr")
                self.cat_var.set(product[6] or "Lubricant")
        except Exception:
            # Fallback
            hs = vals[3] if vals[3] != "—" else ""
            self.hs_code_entry.insert(0, hs)
            price_str = vals[5].replace("Rs.", "").replace(",", "").strip()
            self.price_entry.insert(0, price_str)
            self.cat_var.set(vals[2] if vals[2] != "—" else "Lubricant")
            self.unit_var.set(vals[4])

        # Switch to edit mode
        self.form_mode_label.config(text="  EDITING  ", bg="#FFF3E0", fg="#E65100")
        self.add_btn.config(state="disabled")
        self.update_btn.config(state="normal")
        self.delete_btn.config(state="normal")

    # ─── CRUD Operations ──────────────────────────────────────────────

    def _add_product(self):
        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip()

        if not name:
            return messagebox.showwarning("Validation", "Product name is required.")
        if not price_str:
            return messagebox.showwarning("Validation", "Unit price is required.")

        try:
            price = float(price_str)
            if price < 0:
                return messagebox.showwarning("Validation", "Price cannot be negative.")

            ProductController.add_product(
                name, price,
                self.hs_code_entry.get(),
                self.desc_entry.get(),
                self.unit_var.get(),
                self.cat_var.get()
            )
            self._clear_form()
            self._refresh_all()
            messagebox.showinfo("Success", f"'{name}' added to catalog.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _update_product(self):
        if not self.selected_product_id:
            return

        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip()

        if not name:
            return messagebox.showwarning("Validation", "Product name is required.")
        if not price_str:
            return messagebox.showwarning("Validation", "Unit price is required.")

        try:
            price = float(price_str)
            if price < 0:
                return messagebox.showwarning("Validation", "Price cannot be negative.")

            ProductController.update_product(
                self.selected_product_id, name, price,
                self.hs_code_entry.get(),
                self.desc_entry.get(),
                self.unit_var.get(),
                self.cat_var.get()
            )
            self._clear_form()
            self._refresh_all()
            messagebox.showinfo("Success", f"'{name}' updated successfully.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _delete_product(self):
        if not self.selected_product_id:
            return

        name = self.name_entry.get().strip()
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{name}'?\n\nThis action cannot be undone.",
            icon="warning"
        )
        if confirm:
            try:
                ProductController.delete_product(self.selected_product_id)
                self._clear_form()
                self._refresh_all()
                messagebox.showinfo("Deleted", f"'{name}' removed from catalog.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _clear_form(self, reset_mode=True):
        """Clear all form fields. Only reset product ID and mode when reset_mode=True."""
        self.name_entry.delete(0, tk.END)
        self.hs_code_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.unit_var.set("Ltr")
        self.cat_var.set("Lubricant")

        if reset_mode:
            self.selected_product_id = None
            self.form_mode_label.config(text="  NEW  ", bg="#E8F5E9", fg="#2E7D32")
            self.add_btn.config(state="normal")
            self.update_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            # Deselect tree only on full reset
            for sel in self.tree.selection():
                self.tree.selection_remove(sel)

    def _build_footer(self, parent):
        footer = tk.Frame(parent, bg="white", height=30)
        footer.pack(side="bottom", fill="x")
        tk.Label(footer, text="Powered by Nexpioneer Technologies Pvt. Ltd.",
                 font=("Segoe UI", 8), bg="white", fg="#9E9E9E").pack(pady=5)
