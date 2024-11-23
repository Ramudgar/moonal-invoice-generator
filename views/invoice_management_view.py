import tkinter as tk
from tkinter import ttk, messagebox
from controllers.invoice_controller import InvoiceController
from views.invoice_view import InvoiceView


class InvoiceManagementView(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Manage Invoices")
        # Manually maximize the window (cross-platform compatible)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")  # Set to full screen dimensions
        
        self.configure(bg="#f0f0f5")  # Light background

        # Heading
        heading_label = tk.Label(
            self,
            text="Invoice Management",
            font=("Arial", 16, "bold"),
            bg="#003366",
            fg="#ffffff",
            padx=10,
            pady=10,
            relief="ridge"
        )
        heading_label.pack(fill="x", pady=(0, 20))

        # Search Frame
        search_frame = tk.Frame(self, bg="#f0f0f5")
        search_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            search_frame,
            text="Search by Client Name or Invoice Number:",
            font=("Arial", 12),
            bg="#f0f0f5",
            fg="#003366"
        ).pack(side="left", padx=10)

        self.search_entry = tk.Entry(search_frame, font=("Arial", 12), width=30)
        self.search_entry.pack(side="left", padx=10)

        search_button = tk.Button(
            search_frame,
            text="Search",
            command=self.search_invoices,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            relief="groove",
            bd=2
        )
        search_button.pack(side="left", padx=10)

        refresh_button = tk.Button(
            search_frame,
            text="Refresh",
            command=self.load_invoices,
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            relief="groove",
            bd=2
        )
        refresh_button.pack(side="left", padx=10)

        # Main frame for table and buttons
        main_frame = tk.Frame(self, bg="#ffffff", relief="groove", bd=2)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Invoice Table Label
        tk.Label(
            main_frame,
            text="List of Invoices",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            fg="#003366"
        ).pack(pady=(10, 10))

        # Invoice Table
        self.invoice_table = ttk.Treeview(
            main_frame,
            columns=("ID", "Invoice Number", "Client", "Date", "Total"),
            show="headings",
            height=15
        )
        self.invoice_table.heading("ID", text="Invoice ID")
        self.invoice_table.heading("Invoice Number", text="Invoice Number")
        self.invoice_table.heading("Client", text="Client Name")
        self.invoice_table.heading("Date", text="Date")
        self.invoice_table.heading("Total", text="Total Amount")

        self.invoice_table.column("ID", width=80, anchor="center")
        self.invoice_table.column("Invoice Number", width=150, anchor="center")
        self.invoice_table.column("Client", width=200, anchor="w")
        self.invoice_table.column("Date", width=120, anchor="center")
        self.invoice_table.column("Total", width=100, anchor="e")

        self.invoice_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Style for Treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        style.configure("Treeview", font=("Arial", 11))

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
        view_button.pack(side="left", padx=10, pady=10)

        delete_button = tk.Button(
            action_frame,
            text="Delete Invoice",
            command=self.delete_invoice,
            bg="#F44336",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15
        )
        delete_button.pack(side="left", padx=10, pady=10)

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

    def search_invoices(self):
        """Search invoices based on user input."""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showinfo("Search", "Please enter a search term.", parent=self)
            return

        filtered_invoices = InvoiceController.search_invoices(query)
        self.invoice_table.delete(*self.invoice_table.get_children())
        for invoice in filtered_invoices:
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
            invoice_data, items = InvoiceController.get_invoice_details(
                invoice_id)

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

    def delete_invoice(self):
        """Delete the selected invoice."""
        selected_item = self.invoice_table.selection()
        if not selected_item:
            messagebox.showwarning(
                "No Selection", "Please select an invoice to delete.", parent=self)
            return

        invoice_id = self.invoice_table.item(selected_item, "values")[0]
        confirm = messagebox.askyesno(
            "Delete Invoice", f"Are you sure you want to delete Invoice ID {invoice_id}?", parent=self)
        if confirm:
            InvoiceController.delete_invoice(invoice_id)
            messagebox.showinfo("Deleted", f"Invoice ID {invoice_id} has been deleted.", parent=self)
            self.load_invoices()
