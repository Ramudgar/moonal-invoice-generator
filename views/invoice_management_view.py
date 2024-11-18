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
        tk.Label(self, text="List of Invoices", font=("Arial", 14)).pack(pady=10)

        # Invoice List Table
        self.invoice_table = ttk.Treeview(self, columns=("ID", "Client", "Date", "Subtotal", "VAT", "Discount", "Total", "Paid", "Due"), show="headings")
        self.invoice_table.heading("ID", text="Invoice ID")
        self.invoice_table.heading("Client", text="Client Name")
        self.invoice_table.heading("Date", text="Date")
        self.invoice_table.heading("Subtotal", text="Subtotal")
        self.invoice_table.heading("VAT", text="VAT Amount")
        self.invoice_table.heading("Discount", text="Discount Amount")
        self.invoice_table.heading("Total", text="Total Amount")
        self.invoice_table.heading("Paid", text="Paid Amount")
        self.invoice_table.heading("Due", text="Due Amount")
        self.invoice_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Action Buttons
        action_frame = tk.Frame(self)
        action_frame.pack(pady=10)

        view_button = tk.Button(action_frame, text="View Invoice", command=self.view_invoice)
        view_button.grid(row=0, column=0, padx=10)

        delete_button = tk.Button(action_frame, text="Delete Invoice", command=self.delete_invoice)
        delete_button.grid(row=0, column=1, padx=10)

        # Load invoices on initialization
        self.load_invoices()

    def load_invoices(self):
        """Load all invoices into the invoice table."""
        for item in self.invoice_table.get_children():
            self.invoice_table.delete(item)
        
        invoices = InvoiceController.get_all_invoices()  # Make sure this method retrieves all relevant fields
        for invoice in invoices:
            self.invoice_table.insert("", "end", values=(invoice["invoice_id"], invoice["client_name"], invoice["date"],
                                                         invoice["subtotal"], invoice["vat_amount"], invoice["discount"],
                                                         invoice["total_amount"], invoice["paid_amount"], invoice["due_amount"]))

    def view_invoice(self):
        """View the selected invoice details."""
        selected_item = self.invoice_table.selection()
        if selected_item:
            invoice_id = self.invoice_table.item(selected_item, "values")[0]
            # Open InvoiceView with the selected invoice_id
            InvoiceView(self, invoice_id=invoice_id)
        else:
            messagebox.showwarning("No selection", "Please select an invoice to view.", parent=self)

    def delete_invoice(self):
        """Delete the selected invoice."""
        selected_item = self.invoice_table.selection()
        if not selected_item:
            messagebox.showwarning("No selection", "Please select an invoice to delete.", parent=self)
            return

        invoice_id = self.invoice_table.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Delete Invoice", f"Are you sure you want to delete Invoice ID: {invoice_id}?", parent=self)
        if confirm:
            InvoiceController.delete_invoice(invoice_id)  # Make sure this method properly deletes associated items if needed
            self.load_invoices()
            messagebox.showinfo("Success", "Invoice deleted successfully.", parent=self)
