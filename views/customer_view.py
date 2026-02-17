"""
CustomerView — Customer management with light golden theme.
Renders inside AppShell content area.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import Settings
from controllers.customer_controller import CustomerController


class CustomerView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.C = Settings.COLORS
        self.F = Settings.FONTS
        self.configure(bg=self.C["bg"])
        self.selected_customer_id = None

        self._build_ui()
        self.load_customers()

    def _build_ui(self):
        main = tk.Frame(self, bg=self.C["bg"], padx=24, pady=16)
        main.pack(fill="both", expand=True)

        # Left: Form
        left = tk.Frame(main, bg="white", padx=24, pady=20,
                        highlightbackground=self.C["border"], highlightthickness=1)
        left.pack(side="left", fill="y", padx=(0, 16))

        tk.Label(left, text="Customer Details", font=self.F["h3"],
                 bg="white", fg=self.C["primary"]).pack(anchor="w", pady=(0, 16))

        self.entries = {}
        fields = [
            ("Name", "name"), ("PAN No.", "pan"), ("Address", "address"),
            ("Contact", "contact"), ("Mobile", "mobile"), ("Email", "email")
        ]

        for label, key in fields:
            tk.Label(left, text=label.upper(), font=self.F["small_bold"],
                     bg="white", fg=self.C["secondary"]).pack(anchor="w", pady=(6, 0))
            e = tk.Entry(left, font=self.F["body"], bg=self.C["input_bg"],
                         relief="flat", highlightthickness=2,
                         highlightbackground=self.C["input_border"],
                         highlightcolor=self.C["primary"], width=28)
            e.pack(fill="x", ipady=5, pady=(2, 0))
            self.entries[key] = e

        btn_frame = tk.Frame(left, bg="white")
        btn_frame.pack(fill="x", pady=(16, 0))
        ttk.Button(btn_frame, text="💾  Save", style="Gold.TButton",
                    command=self.save_customer).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(btn_frame, text="🗑  Delete", style="Danger.TButton",
                    command=self.delete_customer).pack(side="left", fill="x", expand=True, padx=(4, 0))
        ttk.Button(left, text="Clear Form", style="Ghost.TButton",
                    command=self.clear_form).pack(fill="x", pady=(8, 0))

        # Right: Table
        right = tk.Frame(main, bg="white",
                         highlightbackground=self.C["border"], highlightthickness=1)
        right.pack(side="right", fill="both", expand=True)

        # Search
        search_frame = tk.Frame(right, bg="white", padx=16, pady=12)
        search_frame.pack(fill="x")
        tk.Label(search_frame, text="🔍", font=("Segoe UI", 11),
                 bg="white", fg=self.C["muted"]).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.load_customers())
        tk.Entry(search_frame, textvariable=self.search_var,
                 font=self.F["body"], bg=self.C["input_bg"],
                 relief="flat", highlightthickness=2,
                 highlightbackground=self.C["input_border"],
                 highlightcolor=self.C["primary"]).pack(
            side="left", fill="x", expand=True, ipady=5, padx=8)

        cols = ("ID", "Name", "PAN", "Address", "Mobile", "Email")
        self.tree = ttk.Treeview(right, columns=cols, show="headings",
                                  style="Custom.Treeview")
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=60 if c == "ID" else 120)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def load_customers(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            customers = CustomerController.get_all_customers()
        except Exception:
            customers = []
        search = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        for c in customers:
            if search and search not in c[1].lower():
                continue
            self.tree.insert("", "end", values=(
                c[0], c[1], c[2] or "",
                c[3] or "", c[5] or "", c[6] or ""
            ))

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0])["values"]
        self.selected_customer_id = values[0]
        try:
            customers = CustomerController.get_all_customers()
            cust = next((c for c in customers if c[0] == self.selected_customer_id), None)
        except Exception:
            cust = None
        if cust:
            self.clear_form()
            mapping = [
                ("name", cust[1]), ("pan", cust[2]),
                ("address", cust[3]), ("contact", cust[4]),
                ("mobile", cust[5]), ("email", cust[6])
            ]
            for key, val in mapping:
                self.entries[key].insert(0, str(val or ""))

    def save_customer(self):
        name = self.entries["name"].get().strip()
        if not name:
            return messagebox.showerror("Error", "Customer name is required")
        try:
            d = {k: e.get().strip() for k, e in self.entries.items()}
            if self.selected_customer_id:
                CustomerController.update_customer(
                    self.selected_customer_id, d["name"], d["pan"],
                    d["address"], d["contact"], d["mobile"], d["email"]
                )
                messagebox.showinfo("Updated", f"'{name}' updated.")
            else:
                CustomerController.add_customer(
                    d["name"], d["pan"], d["address"],
                    d["contact"], d["mobile"], d["email"]
                )
                messagebox.showinfo("Added", f"'{name}' added.")
            self.clear_form()
            self.load_customers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_customer(self):
        if not self.selected_customer_id:
            return messagebox.showwarning("Select", "Select a customer first.")
        if messagebox.askyesno("Confirm", "Delete this customer?"):
            try:
                CustomerController.delete_customer(self.selected_customer_id)
                self.clear_form()
                self.load_customers()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def clear_form(self):
        self.selected_customer_id = None
        for e in self.entries.values():
            e.delete(0, tk.END)
