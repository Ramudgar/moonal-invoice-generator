import tkinter as tk
from tkinter import ttk, messagebox
from controllers.invoice_controller import InvoiceController
from views.invoice_view import InvoiceView


class InvoiceManagementView(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Manage Invoices")

        # Set window size to a maximum of 80% screen width and height (ensures visibility on 14-inch screens)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{int(screen_width * 0.8)}x{int(screen_height * 0.8)}")  # 80% of screen size
        
        self.configure(bg="#f0f0f5")  # Light background

        # Heading
        heading_label = tk.Label(
            self,
            text="Invoice Management",
            font=("Arial", 14, "bold"),
            bg="#003366",
            fg="#ffffff",
            padx=10,
            pady=10,
            relief="ridge"
        )
        heading_label.pack(fill="x", pady=(0, 10))

        # Main frame for table and buttons
        main_frame = tk.Frame(self, bg="#ffffff", relief="groove", bd=2)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Invoice Table Label
        tk.Label(
            main_frame,
            text="List of Invoices",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#003366"
        ).pack(pady=(10, 5))

        # Invoice Table
        self.invoice_table = ttk.Treeview(
            main_frame,
            columns=("ID", "Invoice Number", "Client", "Date", "Total"),
            show="headings",
            height=12  # Reduced the number of visible rows for compactness
        )
        self.invoice_table.heading("ID", text="Invoice ID")
        self.invoice_table.heading("Invoice Number", text="Invoice Number")
        self.invoice_table.heading("Client", text="Client Name")
        self.invoice_table.heading("Date", text="Date")
        self.invoice_table.heading("Total", text="Total Amount")

        self.invoice_table.column("ID", width=70, anchor="center")
        self.invoice_table.column("Invoice Number", width=130, anchor="center")
        self.invoice_table.column("Client", width=180, anchor="w")
        self.invoice_table.column("Date", width=110, anchor="center")
        self.invoice_table.column("Total", width=90, anchor="e")

        self.invoice_table.pack(fill="both", expand=True, padx=5, pady=5)

        # Style for Treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        style.configure("Treeview", font=("Arial", 10))

        # Scrollbars for Treeview
        scrollbar_y = ttk.Scrollbar(
            main_frame, orient="vertical", command=self.invoice_table.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.invoice_table.configure(yscrollcommand=scrollbar_y.set)

        # Action Buttons Frame
        action_frame = tk.Frame(main_frame, bg="#f0f0f5")
        action_frame.pack(fill="x", pady=10)

        view_button = tk.Button(
            action_frame,
            text="View Invoice",
            command=self.view_invoice,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15
        )
        view_button.pack(side="left", padx=5, pady=5, fill="x")

        # Load invoices
        self.load_invoices()

    def load_invoices(self):
        """Load invoices into the table."""
        for item in self.invoice_table.get_children():
            self.invoice_table.delete(item)

        invoices = InvoiceController.get_all_invoices()
        for invoice in invoices:
            self.invoice_table.insert(
                "",
                "end",
                values=(
                    invoice["invoice_id"],
                    invoice["invoice_number"],
                    invoice["client_name"],
                    invoice["date"],
                    f"Rs.{invoice['total_amount']:.2f}"
                )
            )

    def view_invoice(self):
        """Open the Invoice View with the selected invoice ID."""
        selected_item = self.invoice_table.selection()
        if selected_item:
            invoice_id = self.invoice_table.item(selected_item, "values")[0]

            # Fetch invoice details and items
            invoice_data, items = InvoiceController.get_invoice_details(invoice_id)

            # Create a simplified InvoiceView
            invoice_view = InvoiceView(self, invoice_id=invoice_id, invoice_number=invoice_data["invoice_number"],
                                       client_name=invoice_data["client_name"],
                                       client_contact=invoice_data["client_contact"],
                                       address=invoice_data["address"],
                                       pan_no=invoice_data["pan_no"],
                                       vat_rate=invoice_data["vat_rate"],
                                       discount=invoice_data["discount"],
                                       subtotal=invoice_data["subtotal"],
                                       paid_amount=invoice_data["paid_amount"],
                                       due_amount=invoice_data["due_amount"],
                                       date=invoice_data["date"])
            invoice_view.invoice_items = items
            invoice_view.show_invoice_bill_only(
                invoice_id=invoice_id,
                invoice_number=invoice_data["invoice_number"],
                client_name=invoice_data["client_name"],
                client_contact=invoice_data["client_contact"],
                address=invoice_data["address"],
                pan_no=invoice_data["pan_no"],
                vat_rate=invoice_data["vat_rate"],
                discount=invoice_data["discount"],
                subtotal=invoice_data["subtotal"],
                paid_amount=invoice_data["paid_amount"],
                due_amount=invoice_data["due_amount"],
                date=invoice_data["date"]
            )
            invoice_view.grab_set()  # Ensure modal-like behavior
        else:
            messagebox.showwarning(
                "No Selection", "Please select an invoice to view.", parent=self)
