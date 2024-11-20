import tkinter as tk
from tkinter import ttk, messagebox
from controllers.invoice_controller import InvoiceController
from views.invoice_view import InvoiceView

class InvoiceManagementView(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Manage Invoices")
        self.geometry("900x500")

        # Invoice List Label
        tk.Label(self, text="List of Invoices", font=("Arial", 14, "bold")).pack(pady=10)

        # Invoice Table with additional columns for ID and Invoice Number
        self.invoice_table = ttk.Treeview(self, columns=("ID", "Invoice Number", "Client", "Date", "Total"), show="headings")
        self.invoice_table.heading("ID", text="Invoice ID")
        self.invoice_table.heading("Invoice Number", text="Invoice Number")
        self.invoice_table.heading("Client", text="Client Name")
        self.invoice_table.heading("Date", text="Date")
        self.invoice_table.heading("Total", text="Total Amount")
        self.invoice_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons
        action_frame = tk.Frame(self)
        action_frame.pack(pady=10)

        view_button = tk.Button(action_frame, text="View Invoice", command=self.view_invoice)
        view_button.grid(row=0, column=0, padx=10)

        # Load invoices
        self.load_invoices()

    def load_invoices(self):
        """Load invoices into the table."""
        for item in self.invoice_table.get_children():
            self.invoice_table.delete(item)

        invoices = InvoiceController.get_all_invoices()
        for invoice in invoices:
            self.invoice_table.insert("", "end", values=(invoice["invoice_id"], invoice["invoice_number"], invoice["client_name"],
                                                         invoice["date"], f"Rs.{invoice['total_amount']:.2f}"))

    def view_invoice(self):
        """Open the Invoice View with the selected invoice ID."""
        selected_item = self.invoice_table.selection()
        if selected_item:
            invoice_id = self.invoice_table.item(selected_item, "values")[0]

            # Fetch invoice details and items
            invoice_data, items = InvoiceController.get_invoice_details(invoice_id)

            # Create a simplified InvoiceView
            invoice_view = InvoiceView(self)
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
                due_amount=invoice_data["due_amount"]
            )
            invoice_view.grab_set()  # Ensure modal-like behavior
        else:
            messagebox.showwarning("No Selection", "Please select an invoice to view.", parent=self)

