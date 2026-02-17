"""
ProductView — Product management with light golden theme.
Renders inside AppShell content area.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import Settings
from controllers.product_controller import ProductController


class ProductView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.C = Settings.COLORS
        self.F = Settings.FONTS
        self.configure(bg=self.C["bg"])
        self.selected_product_id = None

        self._build_stats_bar()
        self._build_main_layout()
        self.load_products()

    def _build_stats_bar(self):
        bar = tk.Frame(self, bg=self.C["bg"], padx=24, pady=12)
        bar.pack(fill="x")

        try:
            products = ProductController.get_all_products()
        except Exception:
            products = []

        total = len(products)
        low = sum(1 for p in products if len(p) > 10 and float(p[10]) < 10)

        for i, (label, val, color) in enumerate([
            ("Total Products", str(total), self.C["primary"]),
            ("Low Stock", str(low), self.C["danger"] if low > 0 else self.C["muted"]),
        ]):
            chip = tk.Frame(bar, bg="white", padx=16, pady=8,
                            highlightbackground=self.C["border"], highlightthickness=1)
            chip.pack(side="left", padx=(0 if i == 0 else 8, 0))
            tk.Label(chip, text=f"{label}: ", font=self.F["small"],
                     bg="white", fg=self.C["secondary"]).pack(side="left")
            tk.Label(chip, text=val, font=self.F["body_bold"],
                     bg="white", fg=color).pack(side="left")

    def _build_main_layout(self):
        main = tk.Frame(self, bg=self.C["bg"], padx=24)
        main.pack(fill="both", expand=True)

        # Left: Form
        left = tk.Frame(main, bg="white", padx=24, pady=20,
                        highlightbackground=self.C["border"], highlightthickness=1)
        left.pack(side="left", fill="y", padx=(0, 16))

        tk.Label(left, text="Product Details", font=self.F["h3"],
                 bg="white", fg=self.C["primary"]).pack(anchor="w", pady=(0, 16))

        self.entries = {}
        # We'll use a grid for a cleaner layout
        form_grid = tk.Frame(left, bg="white")
        form_grid.pack(fill="x", pady=(0, 10))
        form_grid.columnconfigure(0, weight=1)
        form_grid.columnconfigure(1, weight=1)

        fields = [
            ("Product Name", "name", 0, 0, 2), # label, key, row, col, span
            ("Unit Price (Rs.)", "price", 2, 0, 1),
            ("HS Code", "hs_code", 2, 1, 1),
            ("Category", "category", 4, 0, 1),
            ("Unit", "unit", 4, 1, 1),
            ("Current Stock", "stock", 6, 0, 1),
            ("Min Stock Alert", "min", 6, 1, 1),
            ("Description", "desc", 8, 0, 2)
        ]

        for label, key, r, c, span in fields:
            lbl = tk.Label(form_grid, text=label.upper(), font=self.F["small_bold"],
                           bg="white", fg=self.C["secondary"])
            lbl.grid(row=r, column=c, columnspan=span, sticky="w", pady=(10 if r>0 else 0, 0), padx=(5 if c>0 else 0, 0))
            
            if key == "category":
                e = ttk.Combobox(form_grid, values=[
                    "Engine Oil", "Gear Oil", "Hydraulic Oil", "Transmission Fluid", 
                    "Grease", "Coolant", "Brake Fluid", "Industrial Oil", "Other"
                ], font=self.F["body"], state="normal")
                e.grid(row=r+1, column=c, columnspan=span, sticky="ew", pady=(2, 0), ipady=5, padx=(5 if c>0 else 0, 0))
            elif key == "unit":
                e = ttk.Combobox(form_grid, values=[
                    "Ltr", "Kg", "Pcs", "Barrel", "Drum", "Gallon", "Box", "Set"
                ], font=self.F["body"], state="normal")
                e.grid(row=r+1, column=c, columnspan=span, sticky="ew", pady=(2, 0), ipady=5, padx=(5 if c>0 else 0, 0))
            else:
                e = tk.Entry(form_grid, font=self.F["body"], bg=self.C["input_bg"],
                             relief="flat", highlightthickness=2,
                             highlightbackground=self.C["input_border"],
                             highlightcolor=self.C["primary"])
                e.grid(row=r+1, column=c, columnspan=span, sticky="ew", pady=(2, 0), ipady=5, padx=(5 if c>0 else 0, 0))
            self.entries[key] = e

        btn_frame = tk.Frame(left, bg="white")
        btn_frame.pack(fill="x", pady=(20, 0))
        ttk.Button(btn_frame, text="💾  Save Product", style="Gold.TButton",
                    command=self.save_product).pack(fill="x", ipady=5)
        
        lower_btns = tk.Frame(left, bg="white")
        lower_btns.pack(fill="x", pady=(8, 0))
        ttk.Button(lower_btns, text="🗑  Delete", style="Danger.TButton",
                    command=self.delete_product).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(lower_btns, text="Clear", style="Ghost.TButton",
                    command=self.clear_form).pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Right: Table
        right = tk.Frame(main, bg="white",
                         highlightbackground=self.C["border"], highlightthickness=1)
        right.pack(side="right", fill="both", expand=True)

        # Search bar
        search_frame = tk.Frame(right, bg="white", padx=16, pady=12)
        search_frame.pack(fill="x")
        tk.Label(search_frame, text="🔍", font=("Segoe UI", 11),
                 bg="white", fg=self.C["muted"]).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.load_products())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                font=self.F["body"], bg=self.C["input_bg"],
                                relief="flat", highlightthickness=2,
                                highlightbackground=self.C["input_border"],
                                highlightcolor=self.C["primary"])
        search_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=8)

        cols = ("ID", "Name", "Price", "Stock", "Unit", "Category")
        self.tree = ttk.Treeview(right, columns=cols, show="headings",
                                  style="Custom.Treeview")
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=80 if c == "ID" else 120)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def load_products(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            products = ProductController.get_all_products()
        except Exception:
            products = []

        search = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        for p in products:
            if search and search not in p[1].lower():
                continue
            tag = "low_stock" if len(p) > 10 and float(p[10]) < 10 else ""
            self.tree.insert("", "end", values=(
                p[0], p[1], f"Rs. {float(p[2]):,.2f}",
                p[10] if len(p) > 10 else "N/A",
                p[5] if len(p) > 5 else "",
                p[6] if len(p) > 6 else ""
            ), tags=(tag,))

        self.tree.tag_configure("low_stock", foreground=self.C["danger"])
            
    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0])["values"]
        self.selected_product_id = values[0]
        try:
            products = ProductController.get_all_products()
            product = next((p for p in products if p[0] == self.selected_product_id), None)
        except Exception:
            product = None

        if product:
            self.clear_form()
            mapping = [
                ("name", product[1]), ("price", product[2]),
                ("hs_code", product[3]), ("desc", product[4]),
                ("unit", product[5]), ("category", product[6]),
                ("stock", product[10]), ("min", product[11]),
            ]
            for key, val in mapping:
                if key in self.entries:
                    self.entries[key].insert(0, str(val or ""))

    def save_product(self):
        name = self.entries["name"].get().strip()
        if not name:
            return messagebox.showerror("Error", "Product name is required")
        try:
            d = {k: e.get().strip() for k, e in self.entries.items()}
            
            # Numeric conversions with fallbacks
            def to_f(v): return float(v) if v else 0.0
            def to_i(v): return int(v) if v else 0

            args = [
                d["name"], to_f(d["price"]), d["hs_code"], d["desc"],
                d["unit"] or "Ltr", d["category"] or "Lubricant",
                "", "", 0.0, # Brand, Viscosity, Purchase Price (Hidden)
                to_f(d["stock"]), to_f(d.get("min", 10)), "" # Batch (Hidden)
            ]

            if self.selected_product_id:
                ProductController.update_product(self.selected_product_id, *args)
                messagebox.showinfo("Updated", f"'{name}' updated successfully.")
            else:
                ProductController.add_product(*args)
                messagebox.showinfo("Added", f"'{name}' added successfully.")
                
            self.clear_form()
            self.load_products()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_product(self):
        if not self.selected_product_id:
            return messagebox.showwarning("Select", "Please select a product first.")
        if messagebox.askyesno("Confirm", "Delete this product?"):
            try:
                ProductController.delete_product(self.selected_product_id)
                self.clear_form()
                self.load_products()
                messagebox.showinfo("Deleted", "Product deleted.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def clear_form(self):
        self.selected_product_id = None
        for e in self.entries.values():
            e.delete(0, tk.END)
