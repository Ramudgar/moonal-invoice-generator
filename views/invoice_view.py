import tkinter as tk
from tkinter import ttk, messagebox
from controllers.invoice_controller import InvoiceController
from controllers.product_controller import ProductController
import os
import subprocess
import platform
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from tkinter import messagebox
from datetime import datetime
import num2words  # Ensure this package is installed: pip install num2words
from PIL import Image, ImageTk
from reportlab.lib.utils import simpleSplit
from decimal import Decimal
from utils.invoice_utils import InvoiceUtils


class InvoiceView(tk.Toplevel):
    def __init__(self, master=None, invoice_id=None, invoice_number=None, client_name=None, client_contact=None, address=None, pan_no=None, vat_rate=None, discount=None, subtotal=None, paid_amount=None, due_amount=None, date=None):
        super().__init__(master)
        self.title("Invoice Details" if invoice_id else "Generate Invoice")
        self.geometry("1000x700")
        self.configure(bg="#f0f0f5")
        self.invoice_id = invoice_id
        self.invoice_items = []  # Holds the items added to the invoice

        # Left frame for invoice form, right frame for invoice preview
        self.left_frame = tk.Frame(self, bg="#f0f0f5")
        self.left_frame.pack(side="left", fill="both",
                             expand=True, padx=20, pady=20)

        self.right_frame = tk.Frame(
            self, bg="white", relief="groove", borderwidth=2)
        self.right_frame.pack(side="right", fill="both",
                              expand=True, padx=20, pady=20)

        # Load image after initializing root window
        logo_path = os.path.abspath("moonal_blackwhite.png")
        self.logo_image = self.load_logo(logo_path)

        self.invoice_file = "last_invoice.txt"
        self.current_fiscal_year = InvoiceUtils.get_fiscal_year_nepali()
        self.invoice_number = None

        # If an existing invoice_id is provided, load details
        if self.invoice_id:
            self.show_invoice_bill_only(invoice_id, invoice_number, client_name, client_contact, address,
                                        pan_no, vat_rate, discount, subtotal, paid_amount, due_amount, date)
        else:
            self.create_invoice_form()

    def load_logo(self, path):
        try:
            # Open the image and resize it
            image = Image.open(path)
            # Resize to 100x70 using LANCZOS resampling
            image = image.resize((140, 25), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    def total_in_words(self, total):
        """
        Convert a numeric total amount into a grammatically correct string representation in words.
        """
        from decimal import Decimal, ROUND_DOWN

        # Ensure total is a Decimal for precise calculations
        total = Decimal(total).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

        # Separate the integer part (rupees) and the fractional part (paisa)
        rupees = int(total)
        paisa = int((total - rupees) * 100)

        # Convert rupees and paisa to words
        rupees_in_words = num2words.num2words(rupees, lang='en_IN').title()
        if paisa > 0:
            paisa_in_words = f"{num2words.num2words(
                paisa, lang='en_IN').title()} Paisa"
        else:
            paisa_in_words = ""

        # Combine into a single grammatically correct string
        if paisa > 0:
            total_in_words = f"{rupees_in_words} Rupees And {paisa_in_words}"
        else:
            total_in_words = f"{rupees_in_words} Rupees"

        return total_in_words

    def create_invoice_form(self):
        """Create fields for generating a new invoice with left-right aligned fields."""

        # Main frame for the form
        main_frame = tk.Frame(
            self.left_frame, bg="#f0f0f5", relief="groove", bd=2)
        main_frame.grid(row=0, column=0, columnspan=2,
                        padx=20, pady=20, ipadx=10, ipady=10)

        # Header for client details
        tk.Label(
            main_frame,
            text="Enter Client Details",
            bg="#003366",
            fg="#ffffff",
            font=("Arial", 16, "bold"),
            padx=10,
            pady=10,
            relief="ridge"
        ).grid(row=0, column=0, columnspan=4, sticky="ew", pady=(10, 20))

        # Client Details Section
        tk.Label(main_frame, text="Client Name", bg="#f0f0f5", font=("Arial", 12)).grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        self.client_name_entry = tk.Entry(
            main_frame, width=30, font=("Arial", 12))
        self.client_name_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(main_frame, text="Client Contact", bg="#f0f0f5", font=("Arial", 12)).grid(
            row=1, column=2, padx=10, pady=10, sticky="w"
        )
        self.client_contact_entry = tk.Entry(
            main_frame, width=30, font=("Arial", 12))
        self.client_contact_entry.grid(row=1, column=3, padx=10, pady=10)

        tk.Label(main_frame, text="Address", bg="#f0f0f5", font=("Arial", 12)).grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )
        self.address_entry = tk.Entry(main_frame, width=30, font=("Arial", 12))
        self.address_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(main_frame, text="PAN No.", bg="#f0f0f5", font=("Arial", 12)).grid(
            row=2, column=2, padx=10, pady=10, sticky="w"
        )
        self.pan_no_entry = tk.Entry(main_frame, width=30, font=("Arial", 12))
        self.pan_no_entry.grid(row=2, column=3, padx=10, pady=10)

        # Product Selection Section
        tk.Label(main_frame, text="Select Product", bg="#f0f0f5", font=("Arial", 12)).grid(
            row=3, column=0, padx=10, pady=10, sticky="w"
        )
        self.product_list = ProductController.get_all_products()
        self.product_dropdown = ttk.Combobox(
            main_frame,
            values=[f"{p[1]} - {p[3]}" for p in self.product_list],
            font=("Arial", 12),
            width=28
        )
        self.product_dropdown.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(main_frame, text="Quantity", bg="#f0f0f5", font=("Arial", 12)).grid(
            row=3, column=2, padx=10, pady=10, sticky="w"
        )
        self.quantity_entry = tk.Entry(
            main_frame, width=30, font=("Arial", 12))
        self.quantity_entry.grid(row=3, column=3, padx=10, pady=10)

        tk.Button(
            main_frame,
            text="Add Product",
            command=self.add_product,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20
        ).grid(row=4, column=3, padx=10, pady=10, sticky="e")

        # VAT and Discount Section
        tk.Label(main_frame, text="VAT Rate (%)", bg="#f0f0f5", font=("Arial", 12)).grid(
            row=5, column=0, padx=10, pady=10, sticky="w"
        )
        self.vat_rate_entry = tk.Entry(
            main_frame, width=30, font=("Arial", 12))
        self.vat_rate_entry.insert(0, "13")  # Default VAT
        self.vat_rate_entry.grid(row=5, column=1, padx=10, pady=10)

        tk.Label(main_frame, text="Discount (%)", bg="#f0f0f5", font=("Arial", 12)).grid(
            row=5, column=2, padx=10, pady=10, sticky="w"
        )
        self.discount_entry = tk.Entry(
            main_frame, width=30, font=("Arial", 12))
        self.discount_entry.insert(0, "0")  # Default discount
        self.discount_entry.grid(row=5, column=3, padx=10, pady=10)

        # Added Products Section
        tk.Label(
            main_frame,
            text="Added Products",
            bg="#003366",
            fg="#ffffff",
            font=("Arial", 14, "bold"),
            padx=10,
            pady=10
        ).grid(row=6, column=0, columnspan=4, pady=(20, 10), sticky="ew")

        # Treeview for displaying products
        self.item_tree = ttk.Treeview(
            main_frame,
            columns=("Product", "HS Code", "Quantity", "Price"),
            show="headings",
            height=8
        )
        self.item_tree.grid(row=7, column=0, columnspan=4,
                            padx=10, pady=10, sticky="nsew")

        self.item_tree.heading("Product", text="Product")
        self.item_tree.heading("HS Code", text="HS Code")
        self.item_tree.heading("Quantity", text="Quantity")
        self.item_tree.heading("Price", text="Price")

        self.item_tree.column("Product", width=200)
        self.item_tree.column("HS Code", width=100)
        self.item_tree.column("Quantity", width=80, anchor="center")
        self.item_tree.column("Price", width=100, anchor="center")

        # Buttons for actions
        self.button_frame = tk.Frame(main_frame, bg="#f0f0f5")
        self.button_frame.grid(
            row=8, column=0, columnspan=4, pady=20, sticky="ew")

        tk.Button(
            self.button_frame,
            text="Remove Selected Product",
            command=self.remove_selected_product,
            bg="#F44336",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20
        ).grid(row=0, column=0, padx=10, pady=10)

        tk.Button(
            self.button_frame,
            text="Generate Invoice Preview",
            command=self.generate_invoice_preview,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            width=25
        ).grid(row=0, column=1, padx=10, pady=10)

    def add_product(self):
        """Add a selected product to the Treeview."""
        product_name = self.product_dropdown.get()
        quantity = self.quantity_entry.get()

        if not quantity.isdigit():
            messagebox.showerror("Error", "Quantity must be a valid number.")
            return

        selected_product = next((p for p in self.product_list if f"{
                                p[1]} - {p[3]}" == product_name), None)
        if selected_product:
            product_id, name, price_per_unit, hs_code = selected_product
            total_price = float(price_per_unit) * int(quantity)
            self.invoice_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "price_per_unit": price_per_unit,
                "total_price": total_price,
                "product_name": name,
                "hs_code": hs_code
            })
            self.item_tree.insert(
                "",
                "end",
                values=(name, hs_code, quantity, f"Rs. {total_price:.2f}")
            )

    def remove_selected_product(self):
        """Remove the selected product from the Treeview."""
        selected_item = self.item_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to remove.")
            return

        self.item_tree.delete(selected_item)

    def load_invoice_details(self):
        """Load and display details of the selected invoice."""
        try:
            invoice_data, items = InvoiceController.get_invoice_details(
                self.invoice_id)
            self.invoice_items = items

            # Extract data
            client_name = invoice_data["client_name"]
            client_contact = invoice_data["client_contact"]
            address = invoice_data["address"]
            pan_no = invoice_data["pan_no"]
            vat_rate = invoice_data["vat_rate"]
            discount = invoice_data["discount"]

            self.show_invoice_preview(
                client_name, client_contact, address, pan_no, vat_rate, discount)
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def generate_invoice_preview(self):
        """Generate and display an invoice preview without payment details initially."""
        client_name = self.client_name_entry.get()
        client_contact = self.client_contact_entry.get()
        address = self.address_entry.get()
        pan_no = self.pan_no_entry.get()
        vat_rate = float(self.vat_rate_entry.get())
        discount = float(self.discount_entry.get())

        if not self.invoice_items:
            messagebox.showerror(
                "Error", "No items added to the invoice.", parent=self)
            return

        self.show_invoice_preview(
            client_name, client_contact, address, pan_no, vat_rate, discount)

    def show_invoice_preview(self, client_name, client_contact, address, pan_no, vat_rate, discount):
        """Display invoice details including VAT and discount, but without paid amount."""

        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Invoice Title
        tk.Label(self.right_frame, text="INVOICE", font=(
            "Arial", 18, "bold"), bg="white").pack(anchor="n")

        # Header Frame for Logo, Company Info, Date, and VAT
        header_frame = tk.Frame(self.right_frame, bg="white")
        header_frame.pack(fill="x", padx=20, pady=(5, 5))

        # Logo on the Left
        if self.logo_image:
            logo_label = tk.Label(
                header_frame, image=self.logo_image, bg="white")
            logo_label.grid(row=0, column=0, rowspan=2,
                            sticky="w", padx=(10, 20))

        # Company Name and Address in the Center
        company_info_frame = tk.Frame(header_frame, bg="white")
        company_info_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")

        tk.Label(company_info_frame, text="MOONAL UDHYOG PVT. LTD.", font=(
            "Arial", 14, "bold"), bg="white").pack(anchor="center")
        tk.Label(company_info_frame, text="Golbazar-4, Siraha, Madhesh Pradesh, Nepal",
                 font=("Arial", 10), bg="white").pack(anchor="center")

        # VAT and Date on the Right
        date_vat_frame = tk.Frame(header_frame, bg="white")
        date_vat_frame.grid(row=0, column=2, sticky="ne")

        # VAT Number
        tk.Label(date_vat_frame, text="VAT: 609764022", font=("Arial", 10),
                 bg="white").pack(anchor="e")

        # Date
        date_str = datetime.now().strftime("%Y-%m-%d")
        tk.Label(date_vat_frame, text=f"Date: {date_str}", font=(
            "Arial", 10), bg="white").pack(anchor="e")

        # Adjust Column Weights for Proper Spacing
        header_frame.grid_columnconfigure(0, weight=1)  # Left (Logo)
        header_frame.grid_columnconfigure(1, weight=3)  # Center (Company Info)
        header_frame.grid_columnconfigure(2, weight=1)  # Right (VAT and Date)

        # Invoice Number and Customer Info
        info_frame = tk.Frame(self.right_frame, bg="white")
        info_frame.pack(fill="x", padx=20, pady=5)

        # Customer Information in a structured two-column format
        tk.Label(info_frame, text="Customer Name:", font=(
            "Arial", 10, "bold"), bg="white").grid(row=1, column=0, sticky="w")
        tk.Label(info_frame, text=client_name, font=("Arial", 10),
                 bg="white").grid(row=1, column=1, sticky="w", padx=(10, 0))

        tk.Label(info_frame, text="Contact:", font=("Arial", 10, "bold"),
                 bg="white").grid(row=1, column=2, sticky="w", padx=(20, 0))
        tk.Label(info_frame, text=client_contact, font=("Arial", 10),
                 bg="white").grid(row=1, column=3, sticky="w")

        tk.Label(info_frame, text="Address:", font=("Arial", 10, "bold"),
                 bg="white").grid(row=2, column=0, sticky="w")
        tk.Label(info_frame, text=address, font=("Arial", 10), bg="white").grid(
            row=2, column=1, columnspan=3, sticky="w", padx=(10, 0))

        tk.Label(info_frame, text="PAN No:", font=("Arial", 10, "bold"),
                 bg="white").grid(row=3, column=0, sticky="w")
        tk.Label(info_frame, text=pan_no, font=("Arial", 10), bg="white").grid(
            row=3, column=1, sticky="w", padx=(10, 0))

        # Item Table
        item_frame = tk.Frame(self.right_frame, bg="white")
        item_frame.pack(fill="x", padx=20, pady=20)

        # Headers for the table
        headers = ["S.N", "HS Code", "Description",
                   "Quantity", "Rate", "Amount"]
        for i, header in enumerate(headers):
            tk.Label(item_frame, text=header, font=("Arial", 10, "bold"),
                     bg="white", anchor="w").grid(row=0, column=i, padx=5, pady=(0, 5))

        # Populate the table with items
        for index, item in enumerate(self.invoice_items, start=1):
            tk.Label(item_frame, text=index, bg="white").grid(
                row=index, column=0, padx=5, sticky="w")
            tk.Label(item_frame, text=item["hs_code"], bg="white").grid(
                row=index, column=1, padx=5, sticky="w")
            tk.Label(item_frame, text=item["product_name"], bg="white").grid(
                row=index, column=2, padx=5, sticky="w")
            tk.Label(item_frame, text=item["quantity"], bg="white").grid(
                row=index, column=3, padx=5, sticky="w")
            tk.Label(item_frame, text=f"Rs.{item['price_per_unit']:.2f}", bg="white").grid(
                row=index, column=4, padx=5, sticky="w")
            tk.Label(item_frame, text=f"Rs.{item['total_price']:.2f}", bg="white").grid(
                row=index, column=5, padx=5, sticky="w")

        # Summary Section
        summary_frame = tk.Frame(self.right_frame, bg="white")
        summary_frame.pack(anchor="e", padx=20, pady=20)

        subtotal = sum(item["total_price"] for item in self.invoice_items)
        discount_amount = subtotal * (discount / 100)
        price_after_discount = subtotal-discount_amount
        vat = price_after_discount * (vat_rate / 100)
        total = price_after_discount + vat
        total_in_words = self.total_in_words(total)

        # Summary Labels
        tk.Label(summary_frame, text=f"Subtotal: Rs.{subtotal:.2f}", font=(
            "Arial", 10), bg="white").pack(anchor="e")
        tk.Label(summary_frame, text=f"Discount ({
                 discount}%): -Rs.{discount_amount:.2f}", font=("Arial", 10), bg="white").pack(anchor="e")
        tk.Label(summary_frame, text=f"VAT ({vat_rate}%): Rs.{
                 vat:.2f}", font=("Arial", 10), bg="white").pack(anchor="e")
        tk.Label(summary_frame, text=f"Total: Rs.{total:.2f}", font=(
            "Arial", 12, "bold"), bg="white").pack(anchor="e", pady=(5, 0))
        tk.Label(summary_frame, text=f"Total in Words: {total_in_words}", font=(
            "Arial", 10, "italic"), bg="white").pack(anchor="e", padx=10, pady=5)

        # Proceed to Payment Button
        tk.Button(summary_frame, text="Proceed to Pay", command=lambda: self.prompt_paid_amount(
            total), bg="#FF9800", fg="white", width=15).pack(anchor="e", pady=10)

    def prompt_paid_amount(self, total_amount):
        """Prompt the user to enter the paid amount after previewing the invoice."""
        # Add label and entry for Paid Amount in the button_frame
        tk.Label(
            self.button_frame,
            text="Paid Amount:",
            bg="#f0f0f5",
            font=("Arial", 12)
        ).grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.paid_amount_entry = tk.Entry(
            self.button_frame, width=20, font=("Arial", 12))
        self.paid_amount_entry.grid(row=1, column=1, padx=10, pady=10)

        # Add Finalize Invoice button in the button_frame
        tk.Button(
            self.button_frame,
            text="Finalize Invoice",
            command=lambda: self.finalize_invoice(total_amount),
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20
        ).grid(row=1, column=2, padx=10, pady=10)

    def finalize_invoice(self, total_amount):
        """Finalize the invoice by saving it to the database and printing."""

        if not self.invoice_number:
            # Generate the invoice number only once
            self.invoice_number = InvoiceUtils.generate_invoice_number(
                self.current_fiscal_year, self.invoice_file
            )

        try:
            paid_amount = float(self.paid_amount_entry.get())
            due_amount = total_amount - paid_amount

            client_name = self.client_name_entry.get()
            client_contact = self.client_contact_entry.get()
            address = self.address_entry.get()
            pan_no = self.pan_no_entry.get()
            vat_rate = float(self.vat_rate_entry.get())
            discount = float(self.discount_entry.get())

            invoice_id = InvoiceController.create_invoice(
                self.invoice_number, client_name, client_contact, address, pan_no, self.invoice_items, vat_rate, discount, paid_amount
            )
            messagebox.showinfo("Success", f"Invoice {
                                invoice_id} created successfully with due amount Rs.{due_amount:.2f}.", parent=self)
            self.show_final_invoice_view(invoice_id, client_name, client_contact,
                                         address, pan_no, vat_rate, discount, paid_amount, due_amount)
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def show_invoice_bill_only(self, invoice_id, invoice_number, client_name, client_contact, address, pan_no, vat_rate, discount, subtotal, paid_amount, due_amount, date):
        """Display the invoice bill only with a print button."""

        # Clear all existing widgets in the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Invoice Title
        tk.Label(self.right_frame, text="INVOICE", font=(
            "Arial", 18, "bold"), bg="white").pack(anchor="n", pady=10)

        # Header Frame for Logo, Company Info, Date, and VAT
        header_frame = tk.Frame(self.right_frame, bg="white")
        header_frame.pack(fill="x", padx=20, pady=(5, 5))

        # Logo on the Left
        if self.logo_image:
            logo_label = tk.Label(header_frame, image=self.logo_image, bg="white")
            logo_label.grid(row=0, column=0, rowspan=2, sticky="w", padx=(10, 20))

        # Company Name and Address in the Center
        company_info_frame = tk.Frame(header_frame, bg="white")
        company_info_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")

        tk.Label(company_info_frame, text="MOONAL UDHYOG PVT. LTD.", font=(
            "Arial", 14, "bold"), bg="white").pack(anchor="center")
        tk.Label(company_info_frame, text="Golbazar-4, Siraha, Madhesh Pradesh, Nepal",
                font=("Arial", 10), bg="white").pack(anchor="center")

        # VAT and Date on the Right
        date_vat_frame = tk.Frame(header_frame, bg="white")
        date_vat_frame.grid(row=0, column=2, sticky="ne")

        tk.Label(date_vat_frame, text="VAT: 609764022", font=("Arial", 10),
                bg="white").pack(anchor="e")
        tk.Label(date_vat_frame, text=f"Date: {date}", font=("Arial", 10),
                bg="white").pack(anchor="e")

        # Adjust Column Weights for Proper Spacing
        header_frame.grid_columnconfigure(0, weight=1)  # Left (Logo)
        header_frame.grid_columnconfigure(1, weight=3)  # Center (Company Info)
        header_frame.grid_columnconfigure(2, weight=1)  # Right (VAT and Date)

        # Invoice Number and Customer Info
        info_frame = tk.Frame(self.right_frame, bg="white")
        info_frame.pack(fill="x", padx=20, pady=10)

        # Invoice Number
        tk.Label(info_frame, text="Invoice Number:", font=(
            "Arial", 10, "bold"), bg="white").grid(row=0, column=0, sticky="w")
        tk.Label(info_frame, text=invoice_number, font=("Arial", 10),
                bg="white").grid(row=0, column=1, sticky="w", padx=(10, 0))

        # Customer Information
        tk.Label(info_frame, text="Customer Name:", font=(
            "Arial", 10, "bold"), bg="white").grid(row=1, column=0, sticky="w")
        tk.Label(info_frame, text=client_name, font=("Arial", 10), bg="white").grid(
            row=1, column=1, sticky="w", padx=(10, 0))

        tk.Label(info_frame, text="Contact:", font=("Arial", 10, "bold"),
                bg="white").grid(row=1, column=2, sticky="w", padx=(20, 0))
        tk.Label(info_frame, text=client_contact, font=("Arial", 10), bg="white").grid(
            row=1, column=3, sticky="w")

        tk.Label(info_frame, text="Address:", font=("Arial", 10, "bold"),
                bg="white").grid(row=2, column=0, sticky="w")
        tk.Label(info_frame, text=address, font=("Arial", 10), bg="white").grid(
            row=2, column=1, columnspan=3, sticky="w", padx=(10, 0))

        tk.Label(info_frame, text="PAN No:", font=("Arial", 10, "bold"),
                bg="white").grid(row=3, column=0, sticky="w")
        tk.Label(info_frame, text=pan_no, font=("Arial", 10), bg="white").grid(
            row=3, column=1, sticky="w", padx=(10, 0))

        # Item Table
        item_frame = tk.Frame(self.right_frame, bg="white")
        item_frame.pack(fill="x", padx=20, pady=20)

        # Headers for the table
        headers = ["S.N", "HS Code", "Description", "Quantity", "Rate", "Amount"]
        for i, header in enumerate(headers):
            tk.Label(item_frame, text=header, font=("Arial", 10, "bold"),
                    bg="white", anchor="w").grid(row=0, column=i, padx=5, pady=(0, 5))

        # Populate the table with items
        for index, item in enumerate(self.invoice_items, start=1):
            tk.Label(item_frame, text=index, bg="white").grid(
                row=index, column=0, padx=5, sticky="w")
            tk.Label(item_frame, text=item["hs_code"], bg="white").grid(
                row=index, column=1, padx=5, sticky="w")
            tk.Label(item_frame, text=item["product_name"], bg="white").grid(
                row=index, column=2, padx=5, sticky="w")
            tk.Label(item_frame, text=item["quantity"], bg="white").grid(
                row=index, column=3, padx=5, sticky="w")
            tk.Label(item_frame, text=f"Rs.{item['price_per_unit']:.2f}", bg="white").grid(
                row=index, column=4, padx=5, sticky="w")
            tk.Label(item_frame, text=f"Rs.{item['total_price']:.2f}", bg="white").grid(
                row=index, column=5, padx=5, sticky="w")

        # Summary Section
        summary_frame = tk.Frame(self.right_frame, bg="white")
        summary_frame.pack(anchor="e", padx=20, pady=20)

        subtotal = sum(item["total_price"] for item in self.invoice_items)
        discount_amount = subtotal * (discount / 100)
        price_after_discount = subtotal - discount_amount
        vat = price_after_discount * (vat_rate / 100)
        total = price_after_discount + vat
        total_in_words = self.total_in_words(total)

        # Subtotal
        tk.Label(summary_frame, text=f"Subtotal: Rs.{subtotal:.2f}", font=(
            "Arial", 10), bg="white").pack(anchor="e")
        tk.Label(summary_frame, text=f"Discount ({discount}%): Rs.{discount_amount:.2f}", font=(
            "Arial", 10), bg="white").pack(anchor="e")
        tk.Label(summary_frame, text=f"VAT ({vat_rate}%): Rs.{vat:.2f}", font=(
            "Arial", 10), bg="white").pack(anchor="e")
        tk.Label(summary_frame, text=f"Total: Rs.{total:.2f}", font=(
            "Arial", 12, "bold"), bg="white").pack(anchor="e", pady=(5, 0))
        tk.Label(summary_frame, text=f"Total in Words: {total_in_words}", font=(
            "Arial", 10, "italic"), bg="white").pack(anchor="e", padx=10, pady=5)
        tk.Label(summary_frame, text=f"Paid Amount: Rs.{paid_amount:.2f}", font=(
            "Arial", 10), bg="white").pack(anchor="e")
        tk.Label(summary_frame, text=f"Due Amount: Rs.{due_amount:.2f}", font=(
            "Arial", 10), bg="white").pack(anchor="e", pady=(0, 10))

        # Print Invoice Button
        tk.Button(self.right_frame, text="Print Invoice",
                command=lambda: self.print_invoice(invoice_number, client_name, client_contact, address, pan_no, vat_rate, discount, subtotal, paid_amount, date),
                bg="#FF9800", fg="white", width=15).pack(anchor="e", padx=20, pady=10)


    def show_final_invoice_view(self, invoice_id, client_name, client_contact, address, pan_no, vat_rate, discount, paid_amount, due_amount):
        """Display the finalized version of the invoice with all specified details."""

        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Invoice Title
        tk.Label(self.right_frame, text="INVOICE", font=(
            "Arial", 18, "bold"), bg="white").pack(anchor="n", pady=10)

        # Header Frame for Logo, Company Info, Date, and VAT
        header_frame = tk.Frame(self.right_frame, bg="white")
        header_frame.pack(fill="x", padx=20, pady=(5, 5))

        # Logo on the Left
        if self.logo_image:
            logo_label = tk.Label(
                header_frame, image=self.logo_image, bg="white")
            logo_label.grid(row=0, column=0, rowspan=2,
                            sticky="w", padx=(10, 20))

        # Company Name and Address in the Center
        company_info_frame = tk.Frame(header_frame, bg="white")
        company_info_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")

        tk.Label(company_info_frame, text="MOONAL UDHYOG PVT. LTD.", font=(
            "Arial", 14, "bold"), bg="white").pack(anchor="center")
        tk.Label(company_info_frame, text="Golbazar-4, Siraha, Madhesh Pradesh, Nepal",
                 font=("Arial", 10), bg="white").pack(anchor="center")

        # VAT and Date on the Right
        date_vat_frame = tk.Frame(header_frame, bg="white")
        date_vat_frame.grid(row=0, column=2, sticky="ne")

        # VAT Number
        tk.Label(date_vat_frame, text="VAT: 609764022", font=("Arial", 10),
                 bg="white").pack(anchor="e")

        # Date
        tk.Label(date_vat_frame, text=f"Date: {datetime.now().strftime("%Y-%m-%d")}", font=(
            "Arial", 10), bg="white").pack(anchor="e")

        # Adjust Column Weights for Proper Spacing
        header_frame.grid_columnconfigure(0, weight=1)  # Left (Logo)
        header_frame.grid_columnconfigure(1, weight=3)  # Center (Company Info)
        header_frame.grid_columnconfigure(2, weight=1)  # Right (VAT and Date)

        # Invoice Number and Customer Info
        info_frame = tk.Frame(self.right_frame, bg="white")
        info_frame.pack(fill="x", padx=20, pady=10)

        # Invoice Number
        invoice_number = self.invoice_number

        tk.Label(info_frame, text="Invoice Number:", font=(
            "Arial", 10, "bold"), bg="white").grid(row=0, column=0, sticky="w")
        tk.Label(info_frame, text=invoice_number, font=("Arial", 10),
                 bg="white").grid(row=0, column=1, sticky="w", padx=(10, 0))

        # Customer Information in a structured two-column format
        tk.Label(info_frame, text="Customer Name:", font=(
            "Arial", 10, "bold"), bg="white").grid(row=1, column=0, sticky="w")
        tk.Label(info_frame, text=client_name, font=("Arial", 10),
                 bg="white").grid(row=1, column=1, sticky="w", padx=(10, 0))

        tk.Label(info_frame, text="Contact:", font=("Arial", 10, "bold"),
                 bg="white").grid(row=1, column=2, sticky="w", padx=(20, 0))
        tk.Label(info_frame, text=client_contact, font=("Arial", 10),
                 bg="white").grid(row=1, column=3, sticky="w")

        tk.Label(info_frame, text="Address:", font=("Arial", 10, "bold"),
                 bg="white").grid(row=2, column=0, sticky="w")
        tk.Label(info_frame, text=address, font=("Arial", 10), bg="white").grid(
            row=2, column=1, columnspan=3, sticky="w", padx=(10, 0))

        tk.Label(info_frame, text="PAN No:", font=("Arial", 10, "bold"),
                 bg="white").grid(row=3, column=0, sticky="w")
        tk.Label(info_frame, text=pan_no, font=("Arial", 10), bg="white").grid(
            row=3, column=1, sticky="w", padx=(10, 0))

        # Item Table
        item_frame = tk.Frame(self.right_frame, bg="white")
        item_frame.pack(fill="x", padx=20, pady=20)

        # Headers for the table
        headers = ["S.N", "HS Code", "Description",
                   "Quantity", "Rate", "Amount"]
        for i, header in enumerate(headers):
            tk.Label(item_frame, text=header, font=("Arial", 10, "bold"),
                     bg="white", anchor="w").grid(row=0, column=i, padx=5, pady=(0, 5))

        # Populate the table with items
        for index, item in enumerate(self.invoice_items, start=1):
            tk.Label(item_frame, text=index, bg="white").grid(
                row=index, column=0, padx=5, sticky="w")
            tk.Label(item_frame, text=item["hs_code"], bg="white").grid(
                row=index, column=1, padx=5, sticky="w")
            tk.Label(item_frame, text=item["product_name"], bg="white").grid(
                row=index, column=2, padx=5, sticky="w")
            tk.Label(item_frame, text=item["quantity"], bg="white").grid(
                row=index, column=3, padx=5, sticky="w")
            tk.Label(item_frame, text=f"Rs.{item['price_per_unit']:.2f}", bg="white").grid(
                row=index, column=4, padx=5, sticky="w")
            tk.Label(item_frame, text=f"Rs.{item['total_price']:.2f}", bg="white").grid(
                row=index, column=5, padx=5, sticky="w")

        # Summary Section with Two-Column Layout
        summary_frame = tk.Frame(self.right_frame, bg="white")
        summary_frame.pack(anchor="e", padx=20, pady=20)

        subtotal = sum(item["total_price"] for item in self.invoice_items)
        discount_amount = subtotal * (discount / 100)
        price_after_discount = subtotal-discount_amount
        vat = price_after_discount * (vat_rate / 100)
        total = price_after_discount + vat
        total_in_words = self.total_in_words(total)

        # Label and Value for Subtotal
        tk.Label(summary_frame, text="Subtotal:", font=("Arial", 10),
                 bg="white").grid(row=0, column=0, sticky="w", padx=(0, 10))
        tk.Label(summary_frame, text=f"Rs.{subtotal:.2f}", font=(
            "Arial", 10), bg="white").grid(row=0, column=1, sticky="e")

        # Label and Value for Discount
        tk.Label(summary_frame, text=f"Discount ({discount}%):", font=(
            "Arial", 10), bg="white").grid(row=1, column=0, sticky="w", padx=(0, 10))
        tk.Label(summary_frame, text=f"Rs.{discount_amount:.2f}", font=(
            "Arial", 10), bg="white").grid(row=1, column=1, sticky="e")

        # Label and Value for VAT
        tk.Label(summary_frame, text=f"VAT ({vat_rate}%):", font=(
            "Arial", 10), bg="white").grid(row=2, column=0, sticky="w", padx=(0, 10))
        tk.Label(summary_frame, text=f"Rs.{vat:.2f}", font=(
            "Arial", 10), bg="white").grid(row=2, column=1, sticky="e")

        # Label and Value for Paid Amount
        tk.Label(summary_frame, text="Paid Amount:", font=("Arial", 10),
                 bg="white").grid(row=3, column=0, sticky="w", padx=(0, 10))
        tk.Label(summary_frame, text=f"Rs.{paid_amount:.2f}", font=(
            "Arial", 10), bg="white").grid(row=3, column=1, sticky="e")

        # Label and Value for Due Amount
        tk.Label(summary_frame, text="Due Amount:", font=("Arial", 10),
                 bg="white").grid(row=4, column=0, sticky="w", padx=(0, 10))
        tk.Label(summary_frame, text=f"Rs.{due_amount:.2f}", font=(
            "Arial", 10), bg="white").grid(row=4, column=1, sticky="e")

        # Label and Value for Total
        tk.Label(summary_frame, text="Total:", font=("Arial", 12, "bold"), bg="white").grid(
            row=5, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
        tk.Label(summary_frame, text=f"Rs.{total:.2f}", font=(
            "Arial", 12, "bold"), bg="white").grid(row=5, column=1, sticky="e", pady=(5, 0))

        # Total in Words spanning across columns 0 and 1
        tk.Label(summary_frame, text=f"Total in Words: {total_in_words}", font=(
            "Arial", 10, "italic"), bg="white").grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Signature section
        tk.Label(self.right_frame, text="Accountant:", font=(
            "Arial", 10), bg="white").pack(anchor="w", padx=20, pady=30)

        # Print Invoice Button
        tk.Button(self.right_frame, text="Print Invoice", command=self.print_invoice,
                  bg="#FF9800", fg="white", width=15).pack(anchor="e", padx=20, pady=10)

    def print_invoice(self, invoice_number=None, client_name=None, client_contact=None, address=None, pan_no=None, vat_rate=None, discount=None, subtotal=None, paid_amount=None, date=None):
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics

        # Register the JetBrainsMono-Bold font
        pdfmetrics.registerFont(
            TTFont("JetBrainsMono-Bold", "JetBrainsMono-Bold.ttf"))
        """Generate a PDF of the invoice, show a preview, and allow printing based on the OS."""

        # Set up the PDF file path
        pdf_file_path = "Invoice.pdf"

        # Create a canvas for PDF
        c = canvas.Canvas(pdf_file_path, pagesize=A4)
        width, height = A4

        # data to be displayed in the invoice
        invoice_number = invoice_number or self.invoice_number
        client_name = client_name or self.client_name_entry.get()
        client_contact = client_contact or self.client_contact_entry.get()
        address = address or self.address_entry.get()
        pan_no = pan_no or self.pan_no_entry.get()
        vat_rate = vat_rate or float(self.vat_rate_entry.get())
        discount = discount or float(self.discount_entry.get())
        paid_amount = paid_amount or float(self.paid_amount_entry.get())
        subtotal = subtotal or sum(item["total_price"]
                                   for item in self.invoice_items)
        date = date or datetime.now().strftime("%Y-%m-%d")

        def draw_invoice_content(c, start_y):
            """Draw a single copy of the invoice starting from the given y-coordinate."""
            # Company Logo
            logo_path = "moonal_blackwhite.png"
            logo_width = 145
            logo_height = 20
            logo_x = 20  # Small margin from the left edge
            logo_y = start_y

            try:
                c.drawImage(logo_path, logo_x, logo_y-5,
                            width=logo_width, height=logo_height, mask='auto')
            except Exception as e:
                print("Error loading logo image:", e)
                c.drawString(logo_x, logo_y + 20, "Logo not found")

            title_x = width / 2

            # Company Info
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, start_y-40, "Vat Reg. No: 609764022")
            c.setFont("JetBrainsMono-Bold", 14)
            c.drawCentredString(title_x, start_y, "MOONAL UDHYOG PVT. LTD.")
            c.setFont("Courier", 10)
            c.drawCentredString(title_x, start_y - 15,
                                "Golbazar-4, Siraha, Madhesh Pradesh, Nepal")

            c.setFont("Courier", 10)
            c.drawString(450, start_y, f"Date: {
                         date}")

            customer_info_y = start_y-70
            # Add the invoice title at the center
            invoice_title = "Tax Invoice"
            c.setFont("JetBrainsMono-Bold", 12)
            title_y = start_y - 40
            c.drawCentredString(title_x, title_y, invoice_title)

            # Customer Info
            c.setFont("Courier", 10)

            c.drawString(40, customer_info_y,
                         f"Bill No:{invoice_number}")

            c.drawString(200, customer_info_y, f"Contact: {client_contact}")
            c.drawString(380, customer_info_y, f"PAN No: {pan_no}")

            customer_info_y = start_y - 85
            c.drawString(40, customer_info_y, "Customer Name:")
            c.drawString(150, customer_info_y, client_name)
            customer_info_y -= 15
            c.drawString(40, customer_info_y, "Address:")
            c.drawString(150, customer_info_y, address)

            # Draw a dotted line after the customer information
            c.setDash(1, 2)
            line_y_position_after_customer_info = customer_info_y - 10
            c.line(40, line_y_position_after_customer_info,
                   width - 40, line_y_position_after_customer_info)
            c.setDash(1, 0)

            # Item table headers
            headers = ["S.N", "HS Code", "Description",
                       "Quantity", "Rate", "Amount"]
            x_positions = [40, 90, 160, 300, 370, 440]
            y_position = line_y_position_after_customer_info - 15
            c.setFont("JetBrainsMono-Bold", 10)
            for i, header in enumerate(headers):
                c.drawString(x_positions[i], y_position, header)

            # Populate the table with items
            c.setFont("Courier", 10)
            for index, item in enumerate(self.invoice_items, start=1):
                y_position -= 15
                c.drawString(x_positions[0], y_position, str(index))
                c.drawString(x_positions[1], y_position, item["hs_code"])
                c.drawString(x_positions[2], y_position, item["product_name"])
                c.drawString(x_positions[3], y_position, str(item["quantity"]))
                c.drawString(x_positions[4], y_position, f"Rs.{
                             item['price_per_unit']:.2f}")
                c.drawString(x_positions[5], y_position, f"Rs.{
                             item['total_price']:.2f}")

            # Draw a dotted line before the summary section
            y_position -= 10
            c.setDash(1, 2)
            c.line(40, y_position, width - 40, y_position)
            c.setDash(1, 0)

            # Summary Section
            y_position -= 15
            # subtotal =  sum(item["total_price"] for item in self.invoice_items)
            discount_amount = subtotal * \
                ((discount) / 100)
            price_after_discount = subtotal - discount_amount
            vat = price_after_discount * \
                (vat_rate / 100)
            total = price_after_discount + vat
            total_in_words = self.total_in_words(total)

            due_amount = total - paid_amount

            c.drawString(370, y_position, "Subtotal:")
            c.drawRightString(540, y_position, f"Rs.{subtotal:.2f}")
            y_position -= 15
            c.drawString(370, y_position, f"Discount ({
                         discount}%):")
            c.drawRightString(540, y_position, f"Rs.{discount_amount:.2f}")
            y_position -= 15
            c.drawString(370, y_position,
                         f"VAT ({vat_rate}%):")
            c.drawRightString(540, y_position, f"Rs.{vat:.2f}")
            y_position -= 15
            c.setFont("JetBrainsMono-Bold", 11)
            c.drawString(370, y_position, "Total:")
            c.setFont("Helvetica-Bold", 10)
            c.drawRightString(540, y_position, f"Rs.{total:.2f}")
            y_position -= 15
            c.setFont("Courier", 10)
            c.drawString(370, y_position, "Paid amount:")
            c.drawRightString(540, y_position, f"Rs.{paid_amount:.2f}")
            y_position -= 15
            c.drawString(370, y_position, "Due amount:")
            c.drawRightString(540, y_position, f"Rs.{due_amount:.2f}")

            # Total in Words
            max_width = 300
            y_position += 45
            text_width = c.stringWidth(
                f"Total in Words: {total_in_words}", "Courier", 10)

            if text_width > max_width:
                # Wrap the text if it exceeds the max width
                wrapped_lines = simpleSplit(
                    f"Total in Words: {total_in_words}", "Courier", 10, max_width)
                for line in wrapped_lines:
                    c.drawString(40, y_position, line)
                    y_position -= 15
            else:
                c.drawString(40, y_position, f"Total in Words: {
                             total_in_words}")

            # Signature Section
            y_position -= 30
            c.setFont("Courier", 10)
            c.drawString(40, y_position, "Accountant:")
            c.setDash(1, 2)
            c.line(120, y_position, 200, y_position)
            c.setDash(1, 0)

        # Draw the first copy
        draw_invoice_content(c, height - 50)

        # Draw the second copy below the first
        draw_invoice_content(c, height / 2 - 20)

        # Save the PDF
        c.save()

        # Show confirmation
        messagebox.showinfo(
            "Print Invoice", "Invoice with two copies has been generated.", parent=self)

        # Platform-specific preview and print
        current_platform = platform.system()
        try:
            if current_platform == "Windows":
                os.startfile(pdf_file_path)
            elif current_platform == "Linux":
                subprocess.run(["xdg-open", pdf_file_path])
            elif current_platform == "Darwin":
                subprocess.run(["open", pdf_file_path])
        except Exception as e:
            messagebox.showerror(
                "Error", f"Could not open the PDF for preview. {str(e)}")

        user_response = messagebox.askyesno(
            "Print Invoice", "Would you like to print the invoice?")
        if user_response:
            try:
                if current_platform == "Windows":
                    os.startfile(pdf_file_path, "print")
                elif current_platform in ["Linux", "Darwin"]:
                    subprocess.run(["lp", pdf_file_path])
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Could not print the PDF. {str(e)}")

    def on_closing(self):
        """Handle the window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
