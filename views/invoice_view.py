"""
InvoiceView — Invoice creation wizard and viewer.
Lives inside AppShell. Light-mode golden theme.
"""
from config.settings import Settings
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.invoice_controller import InvoiceController
from controllers.product_controller import ProductController
from controllers.customer_controller import CustomerController
from controllers.settings_controller import SettingsController
import os
import sys
from services.pdf_service import PDFService
from PIL import Image, ImageTk
from utils.invoice_utils import InvoiceUtils
from utils.async_utils import run_async


class InvoiceView(tk.Frame):
    def __init__(self, parent, controller, invoice_id=None, **kwargs):
        super().__init__(parent)
        self.controller = controller
        self.C = Settings.COLORS
        self.F = Settings.FONTS
        self.settings = SettingsController.get_all_settings()
        self.configure(bg=self.C["bg"])

        self.invoice_id = invoice_id
        self.invoice_items = []
        self.current_step = 1
        self.view_mode = False
        self.current_fiscal_year = InvoiceUtils.get_fiscal_year_nepali()
        self.invoice_number = None

        # Initialize financial fields so they always exist
        self.vat_rate = str(Settings.DEFAULT_VAT_RATE)
        self.discount = "0"
        self.paid_amt = "0"

        self.LABELS = {
            "customer": "CUSTOMER NAME",
            "contact": "CONTACT NUMBER",
            "address": "BILLING ADDRESS",
            "tax_id": "TAX ID / PAN NUMBER",
            "item": "ITEM DESCRIPTION",
            "qty": "QTY",
            "price": "UNIT PRICE",
            "total": "TOTAL AMOUNT"
        }

        logo_path = os.path.abspath("moonal_blackwhite.png")
        self.logo_image = self.load_logo(logo_path)
        self.apply_styles()

        if self.invoice_id:
            self.view_mode = True
            self.load_existing_invoice()
        else:
            self.render_wizard()

    def apply_styles(self):
        style = ttk.Style()
        style.configure("Wizard.TButton", font=self.F["button"], padding=10)
        style.configure("Primary.TButton", background=self.C["primary"], foreground="white",
                         borderwidth=0, focuscolor="none")
        style.map("Primary.TButton",
                   background=[("active", self.C["primary_hover"])])
        style.configure("Accent.TButton", background=self.C["primary"], foreground="white",
                         borderwidth=0, focuscolor="none")
        style.map("Accent.TButton",
                   background=[("active", self.C["primary_hover"])])

    def load_logo(self, path):
        try:
            image = Image.open(path).resize((140, 25), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception:
            return None

    def render_wizard(self):
        for widget in self.winfo_children():
            widget.destroy()

        if not self.view_mode:
            progress_frame = tk.Frame(self, bg="white", height=50,
                                       highlightbackground=self.C["border"],
                                       highlightthickness=1)
            progress_frame.pack(fill="x")
            steps = ["1. Customer Details", "2. Add Items", "3. Review & Payment"]
            for i, s in enumerate(steps, 1):
                color = self.C["primary"] if i <= self.current_step else self.C["muted"]
                font = self.F["body_bold"] if i == self.current_step else self.F["body"]
                lbl = tk.Label(progress_frame, text=s, font=font, bg="white", fg=color, padx=30)
                lbl.pack(side="left", expand=True)

        self.body = tk.Frame(self, bg=self.C["bg"], padx=40, pady=30)
        self.body.pack(fill="both", expand=True)

        if self.view_mode:
            self.render_view_mode()
        else:
            if self.current_step == 1:
                self.render_step_1()
            elif self.current_step == 2:
                self.render_step_2()
            elif self.current_step == 3:
                self.render_step_3()

    def render_step_1(self):
        card = tk.Frame(self.body, bg="white", padx=40, pady=40,
                        highlightbackground=self.C["border"], highlightthickness=1)
        card.place(relx=0.5, rely=0.4, anchor="center", width=600)

        tk.Label(card, text="CUSTOMER INFORMATION", font=self.F["h3"],
                 bg="white", fg=self.C["primary"]).pack(anchor="w", pady=(0, 20))

        # Customer Name with autocomplete
        self.all_customers = CustomerController.get_all_customers()
        customer_names = [c[1] for c in self.all_customers]

        tk.Label(card, text=self.LABELS["customer"], font=self.F["small_bold"],
                 bg="white", fg=self.C["secondary"]).pack(anchor="w")
        self.cust_name_entry = ttk.Combobox(card, values=customer_names, font=self.F["body"])
        self.cust_name_entry.pack(fill="x", pady=(2, 12), ipady=5)
        self.cust_name_entry.bind("<<ComboboxSelected>>", self.on_customer_select)

        if hasattr(self, 'cust_name') and self.cust_name:
            self.cust_name_entry.set(self.cust_name)

        def create_field(label, attr):
            tk.Label(card, text=label, font=self.F["small_bold"],
                     bg="white", fg=self.C["secondary"]).pack(anchor="w")
            e = tk.Entry(card, font=self.F["body"], bg=self.C["input_bg"],
                         relief="flat", highlightthickness=2,
                         highlightbackground=self.C["input_border"],
                         highlightcolor=self.C["primary"])
            e.pack(fill="x", pady=(2, 12), ipady=5)
            if hasattr(self, attr) and getattr(self, attr):
                e.insert(0, getattr(self, attr))
            return e

        self.cust_contact_entry = create_field(self.LABELS["contact"], "cust_contact")
        self.cust_address_entry = create_field(self.LABELS["address"], "cust_address")
        self.cust_tax_entry = create_field(self.LABELS["tax_id"], "cust_tax")

        ttk.Button(card, text="CONTINUE TO ITEMS →", style="Gold.TButton",
                    command=self.next_step).pack(side="right", pady=20)
        
        ttk.Button(card, text="CANCEL ❌", style="Ghost.TButton",
                    command=self.controller.show_dashboard).pack(side="left", pady=20)

    def on_customer_select(self, event):
        name = self.cust_name_entry.get()
        customer = next((c for c in self.all_customers if c[1] == name), None)
        if customer:
            self.cust_address_entry.delete(0, tk.END)
            self.cust_address_entry.insert(0, customer[3] or "")
            self.cust_contact_entry.delete(0, tk.END)
            self.cust_contact_entry.insert(0, customer[5] or "")
            self.cust_tax_entry.delete(0, tk.END)
            self.cust_tax_entry.insert(0, customer[2] or "")

    def render_step_2(self):
        left = tk.Frame(self.body, bg=self.C["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 20))

        right = tk.Frame(self.body, bg="white",
                         highlightbackground=self.C["border"], highlightthickness=1)
        right.pack(side="right", fill="both", expand=True)

        # Product form
        form = tk.Frame(left, bg="white", padx=20, pady=20,
                        highlightbackground=self.C["border"], highlightthickness=1)
        form.pack(fill="x", pady=(0, 20))

        tk.Label(form, text="SELECT PRODUCT", font=self.F["h3"],
                 bg="white", fg=self.C["primary"]).pack(anchor="w", pady=(0, 10))

        self.product_list = ProductController.get_all_products()
        self.prod_dropdown = ttk.Combobox(
            form, values=[f"{p[1]} (Rs. {p[2]}/{p[5]})" for p in self.product_list],
            font=self.F["body"])
        self.prod_dropdown.pack(fill="x", pady=5)

        tk.Label(form, text="QUANTITY", font=self.F["small_bold"],
                 bg="white", fg=self.C["secondary"]).pack(anchor="w", pady=(10, 0))
        self.qty_entry = tk.Entry(form, font=self.F["body"], bg=self.C["input_bg"],
                                   relief="flat", highlightthickness=2,
                                   highlightbackground=self.C["input_border"],
                                   highlightcolor=self.C["primary"])
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(fill="x", pady=5, ipady=5)

        ttk.Button(form, text="ADD TO INVOICE", style="Gold.TButton",
                    command=self.add_product).pack(fill="x", pady=15)

        # Items list
        tk.Label(right, text="INVOICE ITEMS", font=self.F["h3"],
                 bg="white", fg=self.C["primary"], padx=20, pady=20).pack(anchor="w")
        self.tree = ttk.Treeview(right, columns=("Item", "HS", "Qty", "Total"),
                                  show="headings", style="Custom.Treeview")
        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.tree.heading("Item", text="ITEM")
        self.tree.heading("HS", text="HS CODE")
        self.tree.heading("Qty", text="QTY")
        self.tree.heading("Total", text="TOTAL")
        self.update_items_table()

        nav = tk.Frame(left, bg=self.C["bg"])
        nav.pack(fill="x", side="bottom")
        ttk.Button(nav, text="← BACK", style="Ghost.TButton",
                    command=self.prev_step).pack(side="left")
        ttk.Button(nav, text="REVIEW INVOICE →", style="Gold.TButton",
                    command=self.next_step).pack(side="right")
        
        ttk.Button(nav, text="CANCEL ❌", style="Ghost.TButton",
                    command=self.controller.show_dashboard).pack(side="right", padx=10)

    def add_product(self):
        val = self.prod_dropdown.get()
        qty_str = self.qty_entry.get()
        if not qty_str.isdigit():
            return messagebox.showerror("Error", "Invalid quantity")
        qty = int(qty_str)
        selected = next((p for p in self.product_list
                         if f"{p[1]} (Rs. {p[2]}/{p[5]})" == val), None)
        if selected:
            pid, name, price, hs = selected[0], selected[1], selected[2], selected[3]
            existing = next((item for item in self.invoice_items
                             if item["product_id"] == pid), None)
            if existing:
                existing["quantity"] += qty
                existing["total_price"] = float(price) * existing["quantity"]
            else:
                self.invoice_items.append({
                    "product_id": pid, "product_name": name,
                    "price_per_unit": float(price), "hs_code": hs,
                    "quantity": qty, "total_price": float(price) * qty
                })
            self.update_items_table()

    def update_items_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for item in self.invoice_items:
            self.tree.insert("", "end", values=(
                item["product_name"], item["hs_code"],
                item["quantity"], f"Rs. {item['total_price']:.2f}"
            ))

    def render_step_3(self):
        sheet = tk.Frame(self.body, bg="white",
                         highlightbackground=self.C["border"], highlightthickness=1)
        sheet.pack(side="left", fill="both", expand=True, padx=(0, 20))
        self.render_preview_sheet(sheet)

        payment = tk.Frame(self.body, bg="white", width=400,
                           highlightbackground=self.C["border"], highlightthickness=1,
                           padx=30, pady=30)
        payment.pack(side="right", fill="y")

        tk.Label(payment, text="FINALIZING", font=self.F["h3"],
                 bg="white", fg=self.C["primary"]).pack(anchor="w", pady=(0, 10))

        def create_field(label, attr, default="0"):
            tk.Label(payment, text=label, font=self.F["small_bold"],
                     bg="white", fg=self.C["secondary"]).pack(anchor="w")
            e = tk.Entry(payment, font=("Segoe UI", 12, "bold"),
                         bg=self.C["input_bg"], relief="flat",
                         highlightthickness=2,
                         highlightbackground=self.C["primary"],
                         highlightcolor=self.C["primary"])
            if not hasattr(self, attr) or getattr(self, attr) is None:
                setattr(self, attr, default)
            e.insert(0, str(getattr(self, attr)))
            e.pack(fill="x", pady=(5, 10), ipady=5)
            return e

        self.vat_entry = create_field("TAX RATE (%)", "vat_rate", "13")
        self.disc_entry = create_field("DISCOUNT (%)", "discount", "0")
        self.paid_entry = create_field("AMOUNT PAID (Rs.)", "paid_amt", "0")

        ttk.Button(payment, text="FINALIZE & SAVE ✅", style="Gold.TButton",
                    command=self.finalize_invoice).pack(fill="x", pady=10)
        ttk.Button(payment, text="← BACK", style="Ghost.TButton",
                    command=self.prev_step).pack(fill="x")
        
        ttk.Button(payment, text="CANCEL ❌", style="Ghost.TButton",
                    command=self.controller.show_dashboard).pack(fill="x", pady=10)

    def render_view_mode(self):
        sheet = tk.Frame(self.body, bg="white",
                         highlightbackground=self.C["border"], highlightthickness=1)
        sheet.pack(side="left", fill="both", expand=True)
        self.render_preview_sheet(sheet)

        sidebar = tk.Frame(self.body, bg="white", width=250, padx=20, pady=20)
        sidebar.pack(side="right", fill="y")
        ttk.Button(sidebar, text="⎙ PRINT INVOICE", style="Gold.TButton",
                    command=self.print_invoice).pack(fill="x", pady=10)
        ttk.Button(sidebar, text="← GO TO HISTORY", style="Ghost.TButton",
                    command=self.controller.show_invoice_history).pack(fill="x")

    def render_preview_sheet(self, parent):
        # CANCELLED banner
        invoice_status = getattr(self, 'invoice_status', 'ACTIVE')
        if invoice_status == 'CANCELLED':
            cancel_bar = tk.Frame(parent, bg=self.C["danger"], pady=8)
            cancel_bar.pack(fill="x")
            cancel_reason = getattr(self, 'cancel_reason', '')
            cancelled_date = getattr(self, 'cancelled_date', '')
            tk.Label(cancel_bar, text="❌  THIS INVOICE HAS BEEN CANCELLED",
                     font=("Segoe UI", 11, "bold"), bg=self.C["danger"], fg="white").pack()
            if cancel_reason:
                tk.Label(cancel_bar, text=f"Reason: {cancel_reason}  |  Date: {cancelled_date}",
                         font=("Segoe UI", 8), bg=self.C["danger"], fg="#FECACA").pack()

        top = tk.Frame(parent, bg="white", pady=10)
        top.pack(fill="x", padx=30)
        if self.logo_image:
            tk.Label(top, image=self.logo_image, bg="white").pack(side="left")

        company_frame = tk.Frame(top, bg="white")
        company_frame.pack(side="left", padx=15)
        
        comp_name = self.settings.get("company_name", "MOONAL UDHYOG PVT. LTD.")
        comp_addr = self.settings.get("company_address", "Golbazar-4, Siraha, Nepal")
        
        tk.Label(company_frame, text=comp_name, font=("Segoe UI", 14, "bold"),
                 bg="white", fg=self.C["primary"]).pack(anchor="w")
        tk.Label(company_frame, text=f"{comp_addr} | VAT Registered",
                 font=("Segoe UI", 8), bg="white", fg=self.C["secondary"]).pack(anchor="w")

        if hasattr(self, 'invoice_number') and self.invoice_number:
            inv_frame = tk.Frame(top, bg="white")
            inv_frame.pack(side="right")
            title = "CREDIT NOTE" if getattr(self, 'is_credit_note', False) else "TAX INVOICE"
            fg_color = self.C["warning"] if getattr(self, 'is_credit_note', False) else self.C["primary"]
            tk.Label(inv_frame, text=title, font=("Segoe UI", 12, "bold"),
                     bg="white", fg=fg_color).pack(anchor="e")
            tk.Label(inv_frame, text=f"No: {self.invoice_number}",
                     font=("Segoe UI", 9), bg="white", fg=self.C["text"]).pack(anchor="e")

        tk.Frame(parent, height=1, bg=self.C["divider"]).pack(fill="x", padx=30, pady=5)

        info = tk.Frame(parent, bg="white", padx=30)
        info.pack(fill="x")
        tk.Label(info, text="BILL TO:", font=self.F["small_bold"],
                 bg="white", fg=self.C["secondary"]).pack(anchor="w")
        tk.Label(info, text=self.cust_name, font=("Segoe UI", 12, "bold"),
                 bg="white", fg=self.C["text"]).pack(anchor="w")
        tk.Label(info, text=self.cust_address, font=self.F["body"],
                 bg="white", fg=self.C["secondary"]).pack(anchor="w")
        if hasattr(self, 'cust_tax') and self.cust_tax:
            tk.Label(info, text=f"PAN/VAT: {self.cust_tax}", font=self.F["small"],
                     bg="white", fg=self.C["secondary"]).pack(anchor="w")

        table = ttk.Treeview(parent, columns=("D", "Q", "P", "T"),
                              show="headings", height=8, style="Custom.Treeview")
        table.pack(fill="both", expand=True, padx=30, pady=(15, 5))
        table.heading("D", text="DESCRIPTION")
        table.heading("Q", text="QTY")
        table.heading("P", text="UNIT PRICE")
        table.heading("T", text="AMOUNT")
        table.column("D", width=200)
        table.column("Q", width=60, anchor="center")
        table.column("P", width=100, anchor="e")
        table.column("T", width=100, anchor="e")

        for i in self.invoice_items:
            table.insert("", "end", values=(
                i["product_name"], i["quantity"],
                f"Rs. {float(i['price_per_unit']):,.2f}",
                f"Rs. {float(i['total_price']):,.2f}"
            ))

        # ── Tax Breakdown ──
        subtotal = sum(float(i['total_price']) for i in self.invoice_items)
        vat_rate = float(getattr(self, 'vat_rate', 13) or 13)
        discount_pct = float(getattr(self, 'discount', 0) or 0)
        paid_amt = float(getattr(self, 'paid_amt', 0) or 0)

        discount_amt = subtotal * (discount_pct / 100)
        taxable_amount = subtotal - discount_amt
        vat_amount = taxable_amount * (vat_rate / 100)
        grand_total = taxable_amount + vat_amount
        due_amount = grand_total - paid_amt

        # STORE on self so finalize_invoice() can access them
        self.subtotal = subtotal
        self.tax_amount = vat_amount
        self.grand_total = grand_total
        self.paid_amount = paid_amt
        self.due_amount = due_amount

        summary = tk.Frame(parent, bg="white", padx=30)
        summary.pack(fill="x", pady=(5, 15))
        summary_right = tk.Frame(summary, bg="white")
        summary_right.pack(side="right")

        def add_line(label, value, bold=False, color=None):
            row = tk.Frame(summary_right, bg="white")
            row.pack(fill="x", pady=1)
            font = ("Segoe UI", 10, "bold") if bold else ("Segoe UI", 9)
            fg = color or self.C["text"]
            tk.Label(row, text=label, font=font, bg="white", fg=self.C["secondary"],
                     width=20, anchor="e").pack(side="left")
            tk.Label(row, text=value, font=font, bg="white", fg=fg,
                     width=15, anchor="e").pack(side="right")

        add_line("Subtotal:", f"Rs. {subtotal:,.2f}")
        if discount_pct > 0:
            add_line(f"Discount ({discount_pct:.1f}%):", f"- Rs. {discount_amt:,.2f}")
            add_line("Taxable Amount:", f"Rs. {taxable_amount:,.2f}")
        add_line(f"VAT ({vat_rate:.0f}%):", f"Rs. {vat_amount:,.2f}")
        tk.Frame(summary_right, height=1, bg=self.C["primary"]).pack(fill="x", pady=3)
        add_line("GRAND TOTAL:", f"Rs. {grand_total:,.2f}", bold=True, color=self.C["primary"])
        if paid_amt > 0:
            add_line("Paid:", f"Rs. {paid_amt:,.2f}")
            due_color = self.C["danger"] if due_amount > 0 else self.C["success"]
            add_line("Due:", f"Rs. {due_amount:,.2f}", bold=True, color=due_color)

    def next_step(self):
        if self.current_step == 1:
            self.cust_name = self.cust_name_entry.get().strip()
            self.cust_contact = self.cust_contact_entry.get().strip()
            self.cust_address = self.cust_address_entry.get().strip()
            self.cust_tax = self.cust_tax_entry.get().strip()

            if not self.cust_name:
                return messagebox.showerror("Error", "Customer Name is required")

            try:
                exists = None
                if self.cust_tax:
                    exists = next((c for c in self.all_customers if c[2] == self.cust_tax), None)
                if not exists:
                    exists = next((c for c in self.all_customers
                                   if c[1].lower() == self.cust_name.lower()), None)
                if not exists:
                    if messagebox.askyesno("New Customer",
                                           f"Save '{self.cust_name}' to customer database?"):
                        CustomerController.add_customer(
                            self.cust_name, self.cust_tax, self.cust_address,
                            "", self.cust_contact, ""
                        )
            except Exception as e:
                print(f"CRM Error: {e}")

        if self.current_step == 2 and not self.invoice_items:
            return messagebox.showerror("Error", "Please add at least one item")

        if self.current_step == 3:
            # Save entry values before re-render
            self.vat_rate = self.vat_entry.get()
            self.discount = self.disc_entry.get()
            self.paid_amt = self.paid_entry.get()

        self.current_step += 1
        self.render_wizard()

    def prev_step(self):
        if self.current_step == 3:
            # Save entry values before going back
            try:
                self.vat_rate = self.vat_entry.get()
                self.discount = self.disc_entry.get()
                self.paid_amt = self.paid_entry.get()
            except Exception:
                pass
        self.current_step -= 1
        self.render_wizard()

    def finalize_invoice(self):
        """Save invoice to database. Compute totals from the current entries."""
        try:
            # Read values from the step-3 entry widgets
            vat_rate = float(self.vat_entry.get() or 13)
            discount_pct = float(self.disc_entry.get() or 0)
            paid_amt = float(self.paid_entry.get() or 0)

            # Compute financial totals
            subtotal = sum(float(i['total_price']) for i in self.invoice_items)
            discount_amt = subtotal * (discount_pct / 100)
            taxable = subtotal - discount_amt
            tax_amount = taxable * (vat_rate / 100)
            grand_total = taxable + tax_amount
            due_amount = grand_total - paid_amt

            # Generate invoice number
            if not self.invoice_number:
                self.invoice_number = InvoiceUtils.generate_invoice_number(self.current_fiscal_year)

            invoice_id = InvoiceController.create_invoice(
                self.invoice_number, self.cust_name, self.cust_contact,
                self.cust_address, self.cust_tax, self.invoice_items,
                vat_rate, discount_pct, paid_amt
            )

            # Update inventory
            for item in self.invoice_items:
                try:
                    ProductController.adjust_stock(item["product_id"], -item["quantity"])
                except Exception:
                    pass

            messagebox.showinfo("Success", "Invoice Saved Successfully!")
            self.invoice_id = invoice_id
            
            # Ask to print
            if messagebox.askyesno("Print Invoice", "Do you want to print the invoice?"):
                # Print and then exit to dashboard
                self.print_invoice(on_exit=self.controller.show_dashboard)
            else:
                self.controller.show_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice: {e}")

    def load_existing_invoice(self):
        data, items = InvoiceController.get_invoice_details(self.invoice_id)
        self.cust_name = data["client_name"]
        self.cust_contact = data["client_contact"]
        self.cust_address = data["address"]
        self.cust_tax = data["pan_no"]
        self.invoice_number = data["invoice_number"]
        self.invoice_items = items
        self.vat_rate = data["vat_rate"]
        self.discount = data["discount"]
        self.paid_amt = data["paid_amount"]
        self.invoice_status = data.get("status", "ACTIVE")
        self.cancel_reason = data.get("cancel_reason", "")
        self.cancelled_date = data.get("cancelled_date", "")
        self.is_credit_note = data.get("is_credit_note", 0)
        self.cancellation_comment = data.get("cancellation_comment", "")
        self.render_wizard()

    def print_invoice(self, on_exit=None):
        try:
            pdf_service = PDFService()

            invoice_data = {
                "invoice_number": self.invoice_number,
                "client_name": self.cust_name,
                "client_contact": getattr(self, 'cust_contact', ''),
                "address": getattr(self, 'cust_address', ''),
                "pan_no": getattr(self, 'cust_tax', ''),
                "vat_rate": getattr(self, 'vat_rate', 13),
                "discount": getattr(self, 'discount', 0),
                "paid_amount": getattr(self, 'paid_amt', 0),
                "status": getattr(self, 'invoice_status', 'ACTIVE'),
                "cancel_reason": getattr(self, 'cancel_reason', ''),
                "cancelled_date": getattr(self, 'cancelled_date', ''),
                "is_credit_note": getattr(self, 'is_credit_note', False),
                "company_name": self.settings.get("company_name", "MOONAL UDHYOG PVT. LTD."),
                "company_address": self.settings.get("company_address", "Golbazar-4, Siraha, Nepal"),
                "company_pan": self.settings.get("company_pan", "123456789"),
            }

            self.configure(cursor="watch")

            def generate_task():
                return pdf_service.generate_invoice_pdf(invoice_data, self.invoice_items)

            def on_success(pdf_path):
                if not self.winfo_exists(): return
                try:
                    self.configure(cursor="")
                except tk.TclError: pass
                
                try:
                    pdf_service.open_pdf(pdf_path)
                    # Optional: messagebox.showinfo("Success", f"PDF generated at {pdf_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"PDF generated but could not open: {e}")

                if on_exit:
                    on_exit()

            def on_error(e):
                if not self.winfo_exists(): return
                try:
                    self.configure(cursor="")
                except tk.TclError: pass
                messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")

            from utils.async_utils import run_async
            run_async(self, generate_task, on_success, on_error)

        except Exception as e:
            if self.winfo_exists():
                self.configure(cursor="")
            messagebox.showerror("Error", f"Failed to start PDF generation: {str(e)}")
