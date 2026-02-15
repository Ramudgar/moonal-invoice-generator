import tkinter as tk
from tkinter import ttk, messagebox
from controllers.invoice_controller import InvoiceController
from controllers.product_controller import ProductController
import os
import sys
import subprocess
import platform
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import num2words
from PIL import Image, ImageTk
from decimal import Decimal
from utils.invoice_utils import InvoiceUtils

class InvoiceView(tk.Frame):
    def __init__(self, parent, controller, invoice_id=None, **kwargs):
        super().__init__(parent)
        self.controller = controller
        self.COLORS = controller.COLORS
        self.configure(bg=self.COLORS["bg"])
        
        self.invoice_id = invoice_id
        self.invoice_items = []
        self.current_step = 1
        self.view_mode = False
        self.current_fiscal_year = InvoiceUtils.get_fiscal_year_nepali()
        self.invoice_number = None

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
        style.theme_use("clam")
        style.configure("Wizard.TButton", font=("Segoe UI", 10, "bold"), padding=10)
        style.configure("Primary.TButton", background=self.COLORS["primary"], foreground="white")
        style.configure("Accent.TButton", background=self.COLORS["accent"], foreground="white")

    def load_logo(self, path):
        try:
            image = Image.open(path).resize((140, 25), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except: return None

    def render_wizard(self):
        for widget in self.winfo_children(): widget.destroy()
        header = tk.Frame(self, bg=self.COLORS["primary"], padx=20, pady=10)
        header.pack(fill="x")
        ttk.Button(header, text="← BACK TO DASHBOARD", command=self.controller.show_dashboard).pack(side="left")
        tk.Label(header, text="SALES INVOICE" if not self.view_mode else f"INVOICE {self.invoice_number}", font=("Segoe UI", 14, "bold"), bg=self.COLORS["primary"], fg="white").pack(side="left", padx=20)

        if not self.view_mode:
            progress_frame = tk.Frame(self, bg="white", height=50)
            progress_frame.pack(fill="x")
            steps = ["1. Customer Details", "2. Add Items", "3. Review & Payment"]
            for i, s in enumerate(steps, 1):
                color = self.COLORS["primary"] if i <= self.current_step else "#E0E0E0"
                lbl = tk.Label(progress_frame, text=s, font=("Segoe UI", 10, "bold" if i == self.current_step else "normal"), bg="white", fg=color, padx=30)
                lbl.pack(side="left", expand=True)

        self.body = tk.Frame(self, bg=self.COLORS["bg"], padx=40, pady=30)
        self.body.pack(fill="both", expand=True)

        if self.view_mode: self.render_view_mode()
        else:
            if self.current_step == 1: self.render_step_1()
            elif self.current_step == 2: self.render_step_2()
            elif self.current_step == 3: self.render_step_3()

    def render_step_1(self):
        card = tk.Frame(self.body, bg="white", padx=40, pady=40, highlightbackground="#E0E0E0", highlightthickness=1)
        card.place(relx=0.5, rely=0.4, anchor="center", width=600)
        tk.Label(card, text="CUSTOMER INFORMATION", font=("Segoe UI", 12, "bold"), bg="white", fg=self.COLORS["primary"]).pack(anchor="w", pady=(0, 20))
        def create_field(label, attr):
            tk.Label(card, text=label, font=("Segoe UI", 9, "bold"), bg="white", fg=self.COLORS["secondary"]).pack(anchor="w")
            e = tk.Entry(card, font=("Segoe UI", 11), bg="#F8F9FA", relief="flat", highlightthickness=1, highlightbackground="#D1D1D1")
            e.pack(fill="x", pady=(2, 12), ipady=5)
            if hasattr(self, attr) and getattr(self, attr): e.insert(0, getattr(self, attr))
            return e
        self.cust_name_entry = create_field(self.LABELS["customer"], "cust_name")
        self.cust_contact_entry = create_field(self.LABELS["contact"], "cust_contact")
        self.cust_address_entry = create_field(self.LABELS["address"], "cust_address")
        self.cust_tax_entry = create_field(self.LABELS["tax_id"], "cust_tax")
        ttk.Button(card, text="CONTINUE TO ITEMS →", style="Primary.TButton", command=self.next_step).pack(side="right", pady=20)

    def render_step_2(self):
        left = tk.Frame(self.body, bg=self.COLORS["bg"]); left.pack(side="left", fill="both", expand=True, padx=(0, 20))
        right = tk.Frame(self.body, bg="white", highlightbackground="#E0E0E0", highlightthickness=1); right.pack(side="right", fill="both", expand=True)
        form = tk.Frame(left, bg="white", padx=20, pady=20, highlightbackground="#E0E0E0", highlightthickness=1); form.pack(fill="x", pady=(0, 20))
        tk.Label(form, text="SELECT PRODUCT", font=("Segoe UI", 10, "bold"), bg="white", fg=self.COLORS["primary"]).pack(anchor="w", pady=(0, 10))
        self.product_list = ProductController.get_all_products()
        self.prod_dropdown = ttk.Combobox(form, values=[f"{p[1]} (Rs. {p[2]}/{p[5]})" for p in self.product_list], font=("Segoe UI", 11)); self.prod_dropdown.pack(fill="x", pady=5)
        tk.Label(form, text="QUANTITY", font=("Segoe UI", 9, "bold"), bg="white", fg=self.COLORS["secondary"]).pack(anchor="w", pady=(10, 0))
        self.qty_entry = tk.Entry(form, font=("Segoe UI", 11), bg="#F8F9FA", relief="flat", highlightthickness=1, highlightbackground="#D1D1D1"); self.qty_entry.insert(0, "1"); self.qty_entry.pack(fill="x", pady=5, ipady=5)
        ttk.Button(form, text="ADD TO INVOICE", style="Primary.TButton", command=self.add_product).pack(fill="x", pady=15)
        tk.Label(right, text="INVOICE ITEMS", font=("Segoe UI", 12, "bold"), bg="white", fg=self.COLORS["primary"], padx=20, pady=20).pack(anchor="w")
        self.tree = ttk.Treeview(right, columns=("Item", "HS", "Qty", "Total"), show="headings"); self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.tree.heading("Item", text="ITEM"); self.tree.heading("HS", text="HS CODE"); self.tree.heading("Qty", text="QTY"); self.tree.heading("Total", text="TOTAL")
        self.update_items_table()
        nav = tk.Frame(left, bg=self.COLORS["bg"]); nav.pack(fill="x", side="bottom")
        ttk.Button(nav, text="← BACK", command=self.prev_step).pack(side="left"); ttk.Button(nav, text="REVIEW INVOICE →", style="Accent.TButton", command=self.next_step).pack(side="right")

    def add_product(self):
        val = self.prod_dropdown.get(); qty_str = self.qty_entry.get()
        if not qty_str.isdigit(): return messagebox.showerror("Error", "Invalid quantity")
        qty = int(qty_str)
        # Product tuple: (pid, name, price, hs_code, description, unit, category)
        selected = next((p for p in self.product_list if f"{p[1]} (Rs. {p[2]}/{p[5]})" == val), None)
        if selected:
            pid, name, price, hs = selected[0], selected[1], selected[2], selected[3]
            existing = next((item for item in self.invoice_items if item["product_id"] == pid), None)
            if existing: existing["quantity"] += qty; existing["total_price"] = float(price) * existing["quantity"]
            else: self.invoice_items.append({"product_id": pid, "product_name": name, "price_per_unit": float(price), "hs_code": hs, "quantity": qty, "total_price": float(price) * qty})
            self.update_items_table()


    def update_items_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for item in self.invoice_items:
            self.tree.insert("", "end", values=(item["product_name"], item["hs_code"], item["quantity"], f"Rs. {item['total_price']:.2f}"))

    def render_step_3(self):
        sheet = tk.Frame(self.body, bg="white", highlightbackground="#E0E0E0", highlightthickness=1); sheet.pack(side="left", fill="both", expand=True, padx=(0, 20)); self.render_preview_sheet(sheet)
        payment = tk.Frame(self.body, bg="white", width=400, highlightbackground="#E0E0E0", highlightthickness=1, padx=30, pady=30); payment.pack(side="right", fill="y")
        tk.Label(payment, text="FINALIZING", font=("Segoe UI", 14, "bold"), bg="white", fg=self.COLORS["primary"]).pack(anchor="w", pady=(0, 10))
        def create_field(l, a, d="0"):
            tk.Label(payment, text=l, font=("Segoe UI", 9, "bold"), bg="white", fg=self.COLORS["secondary"]).pack(anchor="w")
            e = tk.Entry(payment, font=("Segoe UI", 12, "bold"), bg="#F8F9FA", highlightthickness=1, highlightbackground=self.COLORS["primary"])
            if not hasattr(self, a) or getattr(self, a) is None: setattr(self, a, d)
            e.insert(0, str(getattr(self, a))); e.pack(fill="x", pady=(5, 10), ipady=5); return e
        self.vat_entry = create_field("TAX RATE (%)", "vat_rate", "13"); self.disc_entry = create_field("DISCOUNT (%)", "discount", "0"); self.paid_entry = create_field("AMOUNT PAID (Rs.)", "paid_amt", "0")
        ttk.Button(payment, text="FINALIZE & SAVE ✅", style="Accent.TButton", command=self.finalize_invoice).pack(fill="x", pady=10); ttk.Button(payment, text="← BACK", command=self.prev_step).pack(fill="x")

    def render_view_mode(self):
        sheet = tk.Frame(self.body, bg="white", highlightbackground="#E0E0E0", highlightthickness=1); sheet.pack(side="left", fill="both", expand=True)
        self.render_preview_sheet(sheet)
        
        sidebar = tk.Frame(self.body, bg="white", width=250, padx=20, pady=20)
        sidebar.pack(side="right", fill="y")
        ttk.Button(sidebar, text="⎙ PRINT INVOICE", style="Accent.TButton", command=self.print_invoice).pack(fill="x", pady=10)
        ttk.Button(sidebar, text="← GO TO HISTORY", command=self.controller.show_invoice_history).pack(fill="x")

    def render_preview_sheet(self, parent):
        # CANCELLED banner if applicable
        invoice_status = getattr(self, 'invoice_status', 'ACTIVE')
        if invoice_status == 'CANCELLED':
            cancel_bar = tk.Frame(parent, bg="#D32F2F", pady=8)
            cancel_bar.pack(fill="x")
            cancel_reason = getattr(self, 'cancel_reason', '')
            cancelled_date = getattr(self, 'cancelled_date', '')
            tk.Label(cancel_bar, text="❌  THIS INVOICE HAS BEEN CANCELLED",
                     font=("Segoe UI", 11, "bold"), bg="#D32F2F", fg="white").pack()
            if cancel_reason:
                tk.Label(cancel_bar, text=f"Reason: {cancel_reason}  |  Date: {cancelled_date}",
                         font=("Segoe UI", 8), bg="#D32F2F", fg="#FFCDD2").pack()

        top = tk.Frame(parent, bg="white", pady=10); top.pack(fill="x", padx=30)
        if self.logo_image: tk.Label(top, image=self.logo_image, bg="white").pack(side="left")

        # Company header
        company_frame = tk.Frame(top, bg="white")
        company_frame.pack(side="left", padx=15)
        tk.Label(company_frame, text="MOONAL UDHYOG PVT. LTD.", font=("Segoe UI", 14, "bold"),
                 bg="white", fg=self.COLORS["primary"]).pack(anchor="w")
        tk.Label(company_frame, text="Golbazar-4, Siraha, Nepal | VAT Registered",
                 font=("Segoe UI", 8), bg="white", fg=self.COLORS["secondary"]).pack(anchor="w")

        # Invoice number on the right
        if hasattr(self, 'invoice_number') and self.invoice_number:
            inv_frame = tk.Frame(top, bg="white")
            inv_frame.pack(side="right")
            
            title = "CREDIT NOTE" if getattr(self, 'is_credit_note', False) else "TAX INVOICE"
            fg_color = "#E65100" if getattr(self, 'is_credit_note', False) else self.COLORS["primary"]
            
            tk.Label(inv_frame, text=title, font=("Segoe UI", 12, "bold"),
                     bg="white", fg=fg_color).pack(anchor="e")
            tk.Label(inv_frame, text=f"No: {self.invoice_number}",
                     font=("Segoe UI", 9), bg="white", fg=self.COLORS["text"]).pack(anchor="e")

        # Divider
        tk.Frame(parent, height=1, bg="#E0E0E0").pack(fill="x", padx=30, pady=5)

        # Customer info
        info = tk.Frame(parent, bg="white", padx=30); info.pack(fill="x")
        tk.Label(info, text="BILL TO:", font=("Segoe UI", 8, "bold"),
                 bg="white", fg=self.COLORS["secondary"]).pack(anchor="w")
        tk.Label(info, text=self.cust_name, font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w")
        tk.Label(info, text=self.cust_address, font=("Segoe UI", 9),
                 bg="white", fg=self.COLORS["secondary"]).pack(anchor="w")
        if hasattr(self, 'cust_tax') and self.cust_tax:
            tk.Label(info, text=f"PAN/VAT: {self.cust_tax}", font=("Segoe UI", 9),
                     bg="white", fg=self.COLORS["secondary"]).pack(anchor="w")

        # Items table
        table = ttk.Treeview(parent, columns=("D","Q","P","T"), show="headings", height=8)
        table.pack(fill="both", expand=True, padx=30, pady=(15, 5))
        table.heading("D", text="DESCRIPTION"); table.heading("Q", text="QTY")
        table.heading("P", text="UNIT PRICE"); table.heading("T", text="AMOUNT")
        table.column("D", width=200); table.column("Q", width=60, anchor="center")
        table.column("P", width=100, anchor="e"); table.column("T", width=100, anchor="e")
        for i in self.invoice_items:
            table.insert("", "end", values=(
                i["product_name"], i["quantity"],
                f"Rs. {float(i['price_per_unit']):,.2f}",
                f"Rs. {float(i['total_price']):,.2f}"
            ))

        # ─── Tax Breakdown (Nepal IRD compliant) ───
        subtotal = sum(float(i['total_price']) for i in self.invoice_items)
        vat_rate = float(getattr(self, 'vat_rate', 13) or 13)
        discount_pct = float(getattr(self, 'discount', 0) or 0)
        paid_amt = float(getattr(self, 'paid_amt', 0) or 0)

        discount_amt = subtotal * (discount_pct / 100)
        taxable_amount = subtotal - discount_amt
        vat_amount = taxable_amount * (vat_rate / 100)
        grand_total = taxable_amount + vat_amount
        due_amount = grand_total - paid_amt

        summary = tk.Frame(parent, bg="white", padx=30); summary.pack(fill="x", pady=(5, 15))
        # Right-aligned summary lines
        summary_right = tk.Frame(summary, bg="white"); summary_right.pack(side="right")

        def add_line(label, value, bold=False, color=None):
            row = tk.Frame(summary_right, bg="white"); row.pack(fill="x", pady=1)
            font = ("Segoe UI", 10, "bold") if bold else ("Segoe UI", 9)
            fg = color or self.COLORS["text"]
            tk.Label(row, text=label, font=font, bg="white", fg=self.COLORS["secondary"],
                     width=20, anchor="e").pack(side="left")
            tk.Label(row, text=value, font=font, bg="white", fg=fg,
                     width=15, anchor="e").pack(side="right")

        add_line("Subtotal:", f"Rs. {subtotal:,.2f}")
        if discount_pct > 0:
            add_line(f"Discount ({discount_pct:.1f}%):", f"- Rs. {discount_amt:,.2f}")
            add_line("Taxable Amount:", f"Rs. {taxable_amount:,.2f}")
        add_line(f"VAT ({vat_rate:.0f}%):", f"Rs. {vat_amount:,.2f}")
        tk.Frame(summary_right, height=1, bg=self.COLORS["primary"]).pack(fill="x", pady=3)
        add_line("GRAND TOTAL:", f"Rs. {grand_total:,.2f}", bold=True, color=self.COLORS["primary"])
        if paid_amt > 0:
            add_line("Paid:", f"Rs. {paid_amt:,.2f}")
            due_color = "#D32F2F" if due_amount > 0 else "#2E7D32"
            add_line("Due:", f"Rs. {due_amount:,.2f}", bold=True, color=due_color)


    def next_step(self):
        if self.current_step == 1:
            self.cust_name = self.cust_name_entry.get(); self.cust_contact = self.cust_contact_entry.get()
            self.cust_address = self.cust_address_entry.get(); self.cust_tax = self.cust_tax_entry.get()
            if not self.cust_name: return messagebox.showerror("Error", "Name required")
        if self.current_step == 2 and not self.invoice_items: return messagebox.showerror("Error", "No items")
        self.current_step += 1; self.render_wizard()

    def prev_step(self): self.current_step -= 1; self.render_wizard()

    def finalize_invoice(self):
        try:
            self.vat_rate = float(self.vat_entry.get()); self.discount = float(self.disc_entry.get()); self.paid_amt = float(self.paid_entry.get())
            self.invoice_number = InvoiceUtils.generate_invoice_number(self.current_fiscal_year)
            InvoiceController.create_invoice(self.invoice_number, self.cust_name, self.cust_contact, self.cust_address, self.cust_tax, self.invoice_items, self.vat_rate, self.discount, self.paid_amt)
            messagebox.showinfo("Success", f"Invoice {self.invoice_number} finalized!")
            self.view_mode = True; self.render_wizard()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for Tax, Discount, and Paid Amount.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def load_existing_invoice(self):
        data, items = InvoiceController.get_invoice_details(self.invoice_id)
        self.cust_name = data["client_name"]; self.cust_contact = data["client_contact"]
        self.cust_address = data["address"]; self.cust_tax = data["pan_no"]
        self.invoice_number = data["invoice_number"]; self.invoice_items = items
        self.vat_rate = data["vat_rate"]; self.discount = data["discount"]
        self.paid_amt = data["paid_amount"]
        self.invoice_status = data.get("status", "ACTIVE")
        self.cancel_reason = data.get("cancel_reason", "")
        self.cancelled_date = data.get("cancelled_date", "")
        self.is_credit_note = data.get("is_credit_note", 0)
        self.cancellation_comment = data.get("cancellation_comment", "")
        self.render_wizard()

    def total_in_words(self, total):
        total = Decimal(total).quantize(Decimal('0.01'))
        rupees = int(total); paisa = int((total - rupees) * 100)
        text = f"{num2words.num2words(rupees, lang='en_IN').title()} Rupees"
        if paisa > 0: text += f" And {num2words.num2words(paisa, lang='en_IN').title()} Paisa"
        return text

    def print_invoice(self):
        output_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "outputs")
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        safe_filename = self.invoice_number.replace("/", "_").replace("\\", "_")
        pdf_path = os.path.join(output_dir, f"Invoice_{safe_filename}.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4); width, height = A4

        # Precompute tax breakdown
        subtotal = sum(float(i['total_price']) for i in self.invoice_items)
        vat_rate = float(self.vat_rate or 13)
        discount_pct = float(self.discount or 0)
        paid_amt = float(self.paid_amt or 0)
        discount_amt = subtotal * (discount_pct / 100)
        taxable = subtotal - discount_amt
        vat_amt = taxable * (vat_rate / 100)
        grand_total = taxable + vat_amt
        due = grand_total - paid_amt

        # ── Column positions for the items table ──
        LEFT = 40
        RIGHT = width - 40
        COL_SN = LEFT + 5       # S.N.
        COL_DESC = LEFT + 35    # Description
        COL_HS = LEFT + 260     # HS Code
        COL_QTY = LEFT + 340    # Qty
        COL_RATE = LEFT + 395   # Rate
        COL_AMT = RIGHT - 5     # Amount (right-aligned)
        TABLE_W = RIGHT - LEFT

        # Logo path
        logo_path = os.path.abspath("moonal_blackwhite.png")

        def draw_text_line(c, x, y, text):
            """Draw monospaced text."""
            c.drawString(x, y, text)

        def draw_copy(c, start_y):
            """Draw one invoice copy (half-page) using dot-matrix friendly format."""
            c.setFillColorRGB(0, 0, 0)

            # ═══ OUTER BORDER ═══
            copy_height = (height / 2) - 30
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(1)
            c.rect(LEFT, start_y - copy_height + 20, TABLE_W, copy_height)

            y = start_y

            # ═══ COMPANY HEADER ═══
            # Logo (if available)
            try:
                logo_w, logo_h = 80, 22
                c.drawImage(logo_path, LEFT + 8, y - 5, width=logo_w, height=logo_h,
                            preserveAspectRatio=True, mask='auto')
                company_x = LEFT + logo_w + 15
            except Exception:
                company_x = LEFT + 8

            c.setFont("Courier-Bold", 14)
            c.drawString(company_x, y, "MOONAL UDHYOG PVT. LTD.")
            c.setFont("Courier", 8)
            y -= 12
            c.drawString(company_x, y, "Golbazar-4, Siraha, Nepal")
            y -= 10
            c.drawString(company_x, y, "PAN/VAT No: 610338108")

            # TAX INVOICE title (right side)
            c.setFont("Courier-Bold", 14)
            title = "CREDIT NOTE" if getattr(self, 'is_credit_note', False) else "TAX INVOICE"
            c.drawRightString(RIGHT - 8, start_y, title)
            c.setFont("Courier", 9)
            c.drawRightString(RIGHT - 8, start_y - 12, f"Invoice No : {self.invoice_number}")
            c.drawRightString(RIGHT - 8, start_y - 22, f"Date       : {datetime.now().strftime('%Y-%m-%d')}")

            # Separator line
            y -= 12
            c.setLineWidth(0.5)
            c.line(LEFT, y, RIGHT, y)

            # ═══ CUSTOMER INFO ═══
            y -= 12
            c.setFont("Courier", 9)
            c.drawString(LEFT + 8, y, f"Customer : {self.cust_name}")
            c.drawRightString(RIGHT - 8, y, f"Contact: {getattr(self, 'cust_contact', '') or ''}")
            y -= 12
            c.drawString(LEFT + 8, y, f"Address  : {self.cust_address or ''}")
            pan_val = getattr(self, 'cust_tax', '') or ''
            if pan_val:
                c.drawRightString(RIGHT - 8, y, f"PAN/VAT: {pan_val}")

            # Separator
            y -= 8
            c.setLineWidth(0.5)
            c.line(LEFT, y, RIGHT, y)

            # ═══ TABLE HEADER ═══
            y -= 12
            c.setFont("Courier-Bold", 8)
            c.drawString(COL_SN, y, "S.N.")
            c.drawString(COL_DESC, y, "DESCRIPTION")
            c.drawString(COL_HS, y, "HS CODE")
            c.drawString(COL_QTY, y, "QTY")
            c.drawString(COL_RATE, y, "RATE")
            c.drawRightString(COL_AMT, y, "AMOUNT")

            y -= 5
            c.line(LEFT, y, RIGHT, y)

            # ═══ TABLE BODY ═══
            c.setFont("Courier", 9)
            for idx, item in enumerate(self.invoice_items, 1):
                y -= 13
                c.drawString(COL_SN, y, f"{idx:>2}.")
                # Truncate long names
                name = item['product_name'][:28]
                c.drawString(COL_DESC, y, name)
                c.drawString(COL_HS, y, str(item.get('hs_code', '') or ''))
                c.drawRightString(COL_QTY + 25, y, str(item['quantity']))
                c.drawRightString(COL_RATE + 45, y, f"{float(item['price_per_unit']):>10,.2f}")
                c.drawRightString(COL_AMT, y, f"{float(item['total_price']):>10,.2f}")

            # Separator after items
            y -= 8
            c.line(LEFT, y, RIGHT, y)

            # ═══ TOTALS SECTION ═══
            total_label_x = RIGHT - 220
            total_value_x = COL_AMT

            y -= 13
            c.setFont("Courier", 9)
            c.drawString(total_label_x, y, "Sub Total     :")
            c.drawRightString(total_value_x, y, f"Rs. {subtotal:>12,.2f}")

            if discount_pct > 0:
                y -= 12
                c.drawString(total_label_x, y, f"Discount({discount_pct:.1f}%):")
                c.drawRightString(total_value_x, y, f"Rs. {discount_amt:>12,.2f}")

            y -= 12
            c.drawString(total_label_x, y, "Taxable Amount:")
            c.drawRightString(total_value_x, y, f"Rs. {taxable:>12,.2f}")

            y -= 12
            c.drawString(total_label_x, y, f"VAT ({vat_rate:.0f}%)      :")
            c.drawRightString(total_value_x, y, f"Rs. {vat_amt:>12,.2f}")

            # Grand total with double underline
            y -= 5
            c.setLineWidth(1)
            c.line(total_label_x, y, RIGHT - 8, y)
            y -= 1
            c.line(total_label_x, y, RIGHT - 8, y)

            y -= 13
            c.setFont("Courier-Bold", 10)
            c.drawString(total_label_x, y, "GRAND TOTAL   :")
            c.drawRightString(total_value_x, y, f"Rs. {grand_total:>12,.2f}")

            if paid_amt > 0:
                y -= 12
                c.setFont("Courier", 9)
                c.drawString(total_label_x, y, "Paid Amount   :")
                c.drawRightString(total_value_x, y, f"Rs. {paid_amt:>12,.2f}")
                y -= 12
                c.setFont("Courier-Bold", 9)
                c.drawString(total_label_x, y, "Due Amount    :")
                c.drawRightString(total_value_x, y, f"Rs. {due:>12,.2f}")

            # ═══ AMOUNT IN WORDS ═══
            y -= 16
            c.setFont("Courier", 7)
            c.drawString(LEFT + 8, y, f"In Words: {self.total_in_words(grand_total)}")

            # ═══ FOOTER ═══
            y -= 20
            c.setFont("Courier", 7)
            c.drawString(LEFT + 8, y, "Goods once sold cannot be taken back.")
            c.setFont("Courier-Bold", 8)
            c.drawRightString(RIGHT - 8, y, "Authorized Signature")
            # Signature line
            c.setLineWidth(0.3)
            c.line(RIGHT - 140, y + 10, RIGHT - 8, y + 10)

            # Nexpioneer footer REMOVED as per user request for PDF
            # Only keep it in App UI

            # CANCELLED watermark
            if getattr(self, 'invoice_status', 'ACTIVE') == 'CANCELLED':
                c.saveState()
                c.setFillColorRGB(0.85, 0.15, 0.15, 0.25)  # Semi-transparent red
                c.setFont("Courier-Bold", 40)
                c.translate((LEFT + RIGHT) / 2, start_y - copy_height / 2)
                c.rotate(35)
                c.drawCentredString(0, 0, "CANCELLED")
                c.restoreState()

        # ── Draw two copies: top half and bottom half ──
        draw_copy(c, height - 55)
        # Dotted cut line in the middle
        c.setDash(3, 3)
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.setLineWidth(0.5)
        c.line(20, height / 2, width - 20, height / 2)
        c.setFont("Courier", 6)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawCentredString(width / 2, height / 2 + 3, "--- CUT HERE ---")
        c.setDash()  # Reset dash
        draw_copy(c, height / 2 - 25)

        c.save()
        if platform.system() == "Linux": subprocess.run(["xdg-open", pdf_path])
        elif platform.system() == "Windows": os.startfile(pdf_path)
        elif platform.system() == "Darwin": subprocess.run(["open", pdf_path])
        messagebox.showinfo("Success", f"PDF generated at {pdf_path}")
