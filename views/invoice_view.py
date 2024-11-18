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


class InvoiceView(tk.Toplevel):
    def __init__(self, master=None, invoice_id=None):
        super().__init__(master)
        self.title("Invoice Details" if invoice_id else "Generate Invoice")
        self.geometry("1000x700")
        self.configure(bg="#f0f0f5")
        self.invoice_id = invoice_id
        self.invoice_items = []  # Holds the items added to the invoice

        # Generate a consistent invoice number
        # self.invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

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

        # If an existing invoice_id is provided, load details
        if self.invoice_id:
            self.load_invoice_details()
        else:
            self.create_invoice_form()

        self.invoice_file = "last_invoice.txt"
        self.current_fiscal_year = self.get_fiscal_year_nepali()
        self.last_invoice = self.get_last_invoice()
        self.invoice_number = self.generate_invoice_number()

   # Function to check if a year is a leap year

    def is_leap_year(self, year):
        # A year is a leap year if it is divisible by 4, but not divisible by 100,
        # unless it is divisible by 400.
        return (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))

    # Function to calculate the Nepali fiscal year considering leap years
    def get_fiscal_year_nepali(self):
        today = datetime.now()
        year = today.year
        month = today.month
        day = today.day

        # Check if the current year is a leap year
        leap_year = self.is_leap_year(year)

        # Adjust logic for Shrawan 1 based on whether it's a leap year
        if leap_year:
            shrawan_start_day = 16  # In a leap year, Shrawan 1 starts on July 16
        else:
            shrawan_start_day = 17  # In a normal year, Shrawan 1 starts on July 17

        # Approximate Shrawan 1 (mid-July) to determine fiscal year
        if month < 7 or (month == 7 and day < shrawan_start_day):  # Before Shrawan 1
            nepali_year = year + 57  # Adjust to Nepali year
            fiscal_year = f"{nepali_year}/{nepali_year + 1}"
        else:
            nepali_year = year + 57
            fiscal_year = f"{nepali_year}/{nepali_year + 1}"

        return fiscal_year

    def get_last_invoice(self):
        """Retrieve the last invoice number from a file."""
        if not os.path.exists(self.invoice_file):
            return 0  # Start fresh if the file doesn't exist

        with open(self.invoice_file, "r") as file:
            data = file.read().strip()
            try:
                file_fiscal_year, invoice_number = data.split('-')
                # If the fiscal year matches, continue with the previous sequence
                if file_fiscal_year == self.current_fiscal_year:
                    return int(invoice_number)
            except ValueError:
                pass

        return 0  # Reset the sequence if the fiscal year has changed

    def save_last_invoice(self, number):
        """Save the last invoice number to a file."""
        with open(self.invoice_file, "w") as file:
            file.write(f"{self.current_fiscal_year}-{number:03}")

    def generate_invoice_number(self):
        """Generate a new invoice number."""
        # Increment the last invoice number or start from 1
        self.last_invoice += 1
        self.save_last_invoice(self.last_invoice)
        return f"# {self.last_invoice:03}"

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
        # Convert to Decimal to handle fractions accurately
        total = Decimal(total)

        # Separate the integer part (rupees) and the fractional part (paisa)
        rupees = int(total)
        # Get the fractional part as an integer
        paisa = int((total - rupees) * 100)

       # Convert rupees and paisa to words
        rupees_in_words = num2words.num2words(rupees, lang='en_IN').title()
        if paisa > 0:
            paisa_in_words = f"{num2words.num2words(paisa, lang='en_IN').title()} Paisa"
        else:
            paisa_in_words = ""

        # Combine into a single grammatically correct string
        if paisa > 0:
            total_in_words = f"{rupees_in_words} Rupees and {paisa_in_words}"
        else:
            total_in_words = f"{rupees_in_words} Rupees"

        # Combine the rupees and paisa
        total_in_words = f"{rupees_in_words}{paisa_in_words}"
        return total_in_words

    def create_invoice_form(self):
        """Create fields for generating a new invoice."""

        # Heading for Client Details
        tk.Label(self.left_frame, text="Enter Client Details Here", bg="#f0f0f5", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=(10, 20), sticky="w"
        )

        # Client Information Section
        tk.Label(self.left_frame, text="Client Name", bg="#f0f0f5").grid(
            row=1, column=0, padx=10, pady=10, sticky="w")
        self.client_name_entry = tk.Entry(self.left_frame, width=25)
        self.client_name_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.left_frame, text="Client Contact", bg="#f0f0f5").grid(
            row=2, column=0, padx=10, pady=10, sticky="w")
        self.client_contact_entry = tk.Entry(self.left_frame, width=25)
        self.client_contact_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.left_frame, text="Address", bg="#f0f0f5").grid(
            row=3, column=0, padx=10, pady=10, sticky="w")
        self.address_entry = tk.Entry(self.left_frame, width=25)
        self.address_entry.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(self.left_frame, text="PAN No", bg="#f0f0f5").grid(
            row=4, column=0, padx=10, pady=10, sticky="w")
        self.pan_no_entry = tk.Entry(self.left_frame, width=25)
        self.pan_no_entry.grid(row=4, column=1, padx=10, pady=10)

        # Product Selection Section
        tk.Label(self.left_frame, text="Select Product", bg="#f0f0f5").grid(
            row=5, column=0, padx=10, pady=10, sticky="w")
        self.product_list = ProductController.get_all_products()
        self.product_dropdown = ttk.Combobox(self.left_frame, values=[
                                             f"{p[1]} - {p[3]}" for p in self.product_list], width=23)
        self.product_dropdown.grid(row=5, column=1, padx=10, pady=10)

        tk.Label(self.left_frame, text="Quantity", bg="#f0f0f5").grid(
            row=6, column=0, padx=10, pady=10, sticky="w")
        self.quantity_entry = tk.Entry(self.left_frame, width=25)
        self.quantity_entry.grid(row=6, column=1, padx=10, pady=10)

        tk.Button(self.left_frame, text="Add Product", command=self.add_product,
                  bg="#4CAF50", fg="white", width=15).grid(row=7, column=1, padx=10, pady=10)

        # VAT and Discount Section
        tk.Label(self.left_frame, text="VAT Rate (%)", bg="#f0f0f5").grid(
            row=8, column=0, padx=10, pady=10, sticky="w")
        self.vat_rate_entry = tk.Entry(self.left_frame, width=25)
        self.vat_rate_entry.insert(0, "13")  # Default VAT
        self.vat_rate_entry.grid(row=8, column=1, padx=10, pady=10)

        tk.Label(self.left_frame, text="Discount (%)", bg="#f0f0f5").grid(
            row=9, column=0, padx=10, pady=10, sticky="w")
        self.discount_entry = tk.Entry(self.left_frame, width=25)
        self.discount_entry.insert(0, "0")  # Default discount
        self.discount_entry.grid(row=9, column=1, padx=10, pady=10)

        # Product List Section
        tk.Label(self.left_frame, text="Added Products", bg="#f0f0f5", font=("Arial", 10, "bold")).grid(
            row=10, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="w"
        )
        self.item_list = tk.Listbox(self.left_frame, width=50, height=5)
        self.item_list.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

        # Generate Invoice Preview Button
        tk.Button(self.left_frame, text="Generate Invoice Preview", command=self.generate_invoice_preview,
                  bg="#2196F3", fg="white", width=20).grid(row=12, column=1, padx=10, pady=(10, 20))

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

    def add_product(self):
        """Add a selected product to the invoice."""
        product_name = self.product_dropdown.get()
        quantity = int(self.quantity_entry.get())
        selected_product = next((p for p in self.product_list if f"{
                                p[1]} - {p[3]}" == product_name), None)

        if selected_product:
            product_id, name, price_per_unit, hs_code = selected_product
            total_price = price_per_unit * quantity
            self.invoice_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "price_per_unit": price_per_unit,
                "total_price": total_price,
                "product_name": name,
                "hs_code": hs_code
            })
            self.item_list.insert(
                tk.END, f"{name} - HS Code:{hs_code} - Qty: {quantity} - Price: Rs.{total_price}")

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

        # Invoice Number
        tk.Label(info_frame, text="Invoice Number:", font=(
            "Arial", 10, "bold"), bg="white").grid(row=0, column=0, sticky="w")
        tk.Label(info_frame, text=self.invoice_number, font=("Arial", 10),
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
        # Add entry field for paid amount and finalize the invoice
        self.paid_amount_entry = tk.Entry(self.left_frame, width=25)
        self.paid_amount_entry.grid(row=13, column=1, padx=10, pady=10)
        tk.Label(self.left_frame, text="Enter Paid Amount", bg="#f0f0f5", font=(
            "Arial", 10, "bold")).grid(row=13, column=0, padx=10, pady=10, sticky="w")

        # Button to finalize and save the invoice
        tk.Button(self.left_frame, text="Finalize Invoice", command=lambda: self.finalize_invoice(
            total_amount), bg="#4CAF50", fg="white", width=15).grid(row=14, column=1, padx=10, pady=10)

    def finalize_invoice(self, total_amount):
        """Finalize the invoice by saving it to the database and printing."""
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
                client_name, client_contact, address, pan_no, self.invoice_items, vat_rate, discount, paid_amount
            )
            messagebox.showinfo("Success", f"Invoice {
                                invoice_id} created successfully with due amount Rs.{due_amount:.2f}.", parent=self)
            self.show_final_invoice_view(invoice_id, client_name, client_contact,
                                         address, pan_no, vat_rate, discount, paid_amount, due_amount)
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

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
        date_str = datetime.now().strftime("%Y-%m-%d")
        tk.Label(date_vat_frame, text=f"Date: {date_str}", font=(
            "Arial", 10), bg="white").pack(anchor="e")

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
        tk.Label(info_frame, text=self.invoice_number, font=("Arial", 10),
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
        tk.Label(summary_frame, text=f"-Rs.{discount_amount:.2f}", font=(
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

    def print_invoice(self):
        """Generate a PDF of the invoice, show a preview, and allow printing based on the OS."""

        # Set up the PDF file path
        pdf_file_path = "Invoice.pdf"

        # Create a canvas for PDF
        c = canvas.Canvas(pdf_file_path, pagesize=A4)
        width, height = A4

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
            c.setFont("Courier-Bold", 10)
            c.drawString(40, start_y-40, "Vat Reg. No: 609764022")
            c.setFont("Courier-Bold", 12)
            c.drawCentredString(title_x, start_y, "MOONAL UDHYOG PVT. LTD.")
            c.setFont("Courier", 10)
            c.drawCentredString(title_x, start_y - 15,
                                "Golbazar-4, Siraha, Madhesh Pradesh, Nepal")

            c.setFont("Courier", 10)
            c.drawString(450, start_y, f"Date: {
                         datetime.now().strftime('%Y-%m-%d')}")

            customer_info_y = start_y-70
            # Add the invoice title at the center
            invoice_title = "Tax Invoice"
            c.setFont("Courier-Bold", 12)
            title_y = start_y - 40
            c.drawCentredString(title_x, title_y, invoice_title)

            # Customer Info
            c.setFont("Courier", 10)
            c.drawString(40, customer_info_y,
                         f"Bill No:{self.invoice_number}")

            c.drawString(200, customer_info_y, f"Contact: {
                         self.client_contact_entry.get()}")
            c.drawString(380, customer_info_y, f"PAN No: {
                         self.pan_no_entry.get()}")

            customer_info_y = start_y - 85
            c.drawString(40, customer_info_y, "Customer Name:")
            c.drawString(150, customer_info_y, self.client_name_entry.get())
            customer_info_y -= 15
            c.drawString(40, customer_info_y, "Address:")
            c.drawString(150, customer_info_y, self.address_entry.get())

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
            c.setFont("Courier-Bold", 10)
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
            subtotal = sum(item["total_price"] for item in self.invoice_items)
            discount_amount = subtotal * \
                (float(self.discount_entry.get()) / 100)
            price_after_discount = subtotal - discount_amount
            vat = price_after_discount * \
                (float(self.vat_rate_entry.get()) / 100)
            total = price_after_discount + vat
            total_in_words = self.total_in_words(total)
            paid_amount = float(self.paid_amount_entry.get())
            due_amount = total - paid_amount

            c.drawString(390, y_position, "Subtotal:")
            c.drawRightString(540, y_position, f"Rs.{subtotal:.2f}")
            y_position -= 15
            c.drawString(390, y_position, f"Discount ({
                         self.discount_entry.get()}%):")
            c.drawRightString(540, y_position, f"Rs.{discount_amount:.2f}")
            y_position -= 15
            c.drawString(390, y_position,
                         f"VAT ({self.vat_rate_entry.get()}%):")
            c.drawRightString(540, y_position, f"Rs.{vat:.2f}")
            y_position -= 15
            c.setFont("Courier-Bold", 10)
            c.drawString(390, y_position, "Total:")
            c.drawRightString(540, y_position, f"Rs.{total:.2f}")
            y_position -= 15
            c.setFont("Courier", 10)
            c.drawString(390, y_position, "Paid amount:")
            c.drawRightString(540, y_position, f"Rs.{paid_amount:.2f}")
            y_position -= 15
            c.drawString(390, y_position, "Due amount:")
            c.drawRightString(540, y_position, f"Rs.{due_amount:.2f}")

            # Total in Words
            max_width = 300
            y_position += 45
            text_width = c.stringWidth(
                f"Total in Words: {total_in_words}", "Courier-Oblique", 10)

            if text_width > max_width:
                # Wrap the text if it exceeds the max width
                wrapped_lines = simpleSplit(
                    f"Total in Words: {total_in_words}", "Courier-Oblique", 10, max_width)
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
