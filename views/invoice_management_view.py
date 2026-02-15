import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from controllers.invoice_controller import InvoiceController


class CancelInvoiceDialog(tk.Toplevel):
    """Custom dialog for IRD-compliant invoice cancellation."""
    def __init__(self, parent, invoice_number):
        super().__init__(parent)
        self.title("Cancel Invoice & Issue Credit Note")
        self.geometry("500x450")
        self.resizable(False, False)
        self.result = None
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        # UI Elements
        tk.Label(self, text=f"Cancel Invoice: {invoice_number}", 
                 font=("Segoe UI", 12, "bold"), fg="#D32F2F").pack(pady=15)
        
        tk.Label(self, text="Select Reason (IRD Requirement):", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=30)
        self.reason_var = tk.StringVar()
        self.reason_combo = ttk.Combobox(self, textvariable=self.reason_var, 
                                         values=InvoiceController.CANCELLATION_REASONS, 
                                         state="readonly", width=50)
        self.reason_combo.pack(padx=30, pady=(5, 15))
        
        tk.Label(self, text="Additional Comments (Optional):", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=30)
        self.comment_text = tk.Text(self, height=5, width=50, font=("Segoe UI", 9))
        self.comment_text.pack(padx=30, pady=(5, 15))
        
        tk.Label(self, text="⚠️ Action will issue a Credit Note and cannot be undone.", 
                 font=("Segoe UI", 9), fg="#D32F2F").pack(pady=10)
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Confirm Cancellation", command=self.on_confirm).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side="left", padx=10)

    def on_confirm(self):
        reason = self.reason_var.get()
        if not reason:
            messagebox.showerror("Error", "Please select a cancellation reason.", parent=self)
            return
        self.result = (reason, self.comment_text.get("1.0", "end-1c").strip())
        self.destroy()


class InvoiceManagementView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.COLORS = controller.COLORS
        self.configure(bg=self.COLORS["bg"])

        self._apply_styles()
        self._build_header()
        self._build_toolbar()
        self._build_table()
        self._build_footer()
        self.load_invoices()

    def _apply_styles(self):
        style = ttk.Style()
        style.configure("History.TButton", font=("Segoe UI", 10, "bold"),
                         background=self.COLORS["primary"], foreground="white", padding=8)
        style.map("History.TButton", background=[("active", "#B8960E")])
        style.configure("Cancel.TButton", font=("Segoe UI", 10, "bold"),
                         background="#D32F2F", foreground="white", padding=8)
        style.map("Cancel.TButton", background=[("active", "#B71C1C")])
        style.configure("Inv.Treeview", rowheight=32, font=("Segoe UI", 10))
        style.configure("Inv.Treeview.Heading", font=("Segoe UI", 9, "bold"),
                         background=self.COLORS["primary"], foreground="white",
                         relief="flat", padding=6)
        style.map("Inv.Treeview.Heading", background=[("active", "#B8960E")])
        style.map("Inv.Treeview",
                   background=[("selected", "#D4AF37")],
                   foreground=[("selected", "white")])

    def _build_header(self):
        header = tk.Frame(self, bg=self.COLORS["primary"], padx=20, pady=12)
        header.pack(fill="x")

        left = tk.Frame(header, bg=self.COLORS["primary"])
        left.pack(side="left")
        ttk.Button(left, text="← DASHBOARD",
                   command=self.controller.show_dashboard).pack(side="left", padx=(0, 15))
        tk.Label(left, text="INVOICE HISTORY", font=("Segoe UI", 16, "bold"),
                 bg=self.COLORS["primary"], fg="white").pack(side="left")

        # Invoice count badge
        self.count_label = tk.Label(header, text="0 invoices", font=("Segoe UI", 9),
                                    bg=self.COLORS["primary"], fg="#FFF9C4")
        self.count_label.pack(side="right")

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg="white", padx=20, pady=10)
        toolbar.pack(fill="x")

        # Status filter
        tk.Label(toolbar, text="FILTER:", font=("Segoe UI", 9, "bold"),
                 bg="white", fg=self.COLORS["secondary"]).pack(side="left", padx=(0, 8))

        self.filter_var = tk.StringVar(value="ALL")
        filters = [("All", "ALL"), ("Active", "ACTIVE"), ("Cancelled", "CANCELLED"), ("Credit Notes", "CREDIT_NOTE")]
        for text, val in filters:
            rb = tk.Radiobutton(toolbar, text=text, variable=self.filter_var, value=val,
                                font=("Segoe UI", 9), bg="white", fg=self.COLORS["text"],
                                selectcolor="white", activebackground="white",
                                command=self.load_invoices)
            rb.pack(side="left", padx=5)

        # Action buttons on right
        btn_frame = tk.Frame(toolbar, bg="white")
        btn_frame.pack(side="right")

        ttk.Button(btn_frame, text="👁️ VIEW INVOICE", style="History.TButton",
                   command=self.view_invoice).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="❌ CANCEL INVOICE", style="Cancel.TButton",
                   command=self.cancel_invoice).pack(side="left")

        # Divider
        tk.Frame(self, height=1, bg="#E0E0E0").pack(fill="x")

    def _build_table(self):
        table_frame = tk.Frame(self, bg="white", padx=15, pady=15)
        table_frame.pack(fill="both", expand=True)

        columns = ("S.N.", "Invoice #", "Customer", "Date", "Total", "Status")
        self.invoice_table = ttk.Treeview(table_frame, columns=columns, show="headings",
                                           style="Inv.Treeview", height=18)

        self.invoice_table.heading("S.N.", text="S.N.")
        self.invoice_table.heading("Invoice #", text="INVOICE NO.")
        self.invoice_table.heading("Customer", text="CUSTOMER")
        self.invoice_table.heading("Date", text="DATE")
        self.invoice_table.heading("Total", text="TOTAL AMOUNT")
        self.invoice_table.heading("Status", text="STATUS")

        self.invoice_table.column("S.N.", width=50, anchor="center", minwidth=40)
        self.invoice_table.column("Invoice #", width=160, anchor="center", minwidth=120)
        self.invoice_table.column("Customer", width=220, anchor="w", minwidth=150)
        self.invoice_table.column("Date", width=110, anchor="center", minwidth=90)
        self.invoice_table.column("Total", width=130, anchor="e", minwidth=100)
        self.invoice_table.column("Status", width=100, anchor="center", minwidth=80)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                  command=self.invoice_table.yview)
        self.invoice_table.configure(yscrollcommand=scrollbar.set)

        self.invoice_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Tag styles
        self.invoice_table.tag_configure("active", background="white")
        self.invoice_table.tag_configure("active_odd", background="#F9F9F9")
        self.invoice_table.tag_configure("cancelled", background="#FFEBEE", foreground="#B71C1C")
        self.invoice_table.tag_configure("cancelled_odd", background="#FFE0E0", foreground="#B71C1C")
        self.invoice_table.tag_configure("credit_note", background="#FFFDE7", foreground="#F57F17")
        self.invoice_table.tag_configure("credit_note_odd", background="#FFF9C4", foreground="#F57F17")

    def _build_footer(self):
        footer = tk.Frame(self, bg="white", height=40)
        footer.pack(fill="x", side="bottom")
        tk.Label(footer, text="Powered by Nexpioneer Technologies Pvt. Ltd.",
                 font=("Segoe UI", 9), bg="white", fg="#9E9E9E").pack(pady=10)

    def load_invoices(self):
        """Load invoices into the table with filter support."""
        for item in self.invoice_table.get_children():
            self.invoice_table.delete(item)

        invoices = InvoiceController.get_all_invoices()
        filter_val = self.filter_var.get()

        # Store invoice_ids mapped by iid for selection
        self._invoice_map = {}
        sn = 0

        for invoice in invoices:
            status = invoice.get("status", "ACTIVE")
            is_cn = invoice.get("is_credit_note", 0)
            
            # Filter logic
            if filter_val == "CREDIT_NOTE":
                if not is_cn: continue
            elif filter_val != "ALL" and status != filter_val:
                continue
            
            # Hide Credit Notes from "ACTIVE" filter to avoid confusion? 
            # No, Credit Notes are technically active records. 
            # But "Cancelled" filter should only show original cancelled invoices.

            sn += 1
            iid = str(invoice["invoice_id"])
            is_cancelled = (status == "CANCELLED")
            
            if is_cn:
                tag = "credit_note_odd" if sn % 2 != 0 else "credit_note"
                status_display = "🧾 CREDIT NOTE"
            else:
                tag = ("cancelled" if sn % 2 != 0 else "cancelled_odd") if is_cancelled else \
                      ("active_odd" if sn % 2 == 0 else "active")
                status_display = "✅ ACTIVE" if not is_cancelled else "❌ CANCELLED"

            self.invoice_table.insert("", "end", iid=iid, values=(
                sn,
                invoice["invoice_number"],
                invoice["client_name"],
                invoice["date"],
                f"Rs. {invoice['total_amount']:,.2f}",
                status_display
            ), tags=(tag,))

            self._invoice_map[iid] = invoice

        self.count_label.config(text=f"{sn} record{'s' if sn != 1 else ''}")

    def view_invoice(self):
        """Open the Invoice View with the selected invoice ID."""
        selected = self.invoice_table.selection()
        if not selected:
            return messagebox.showwarning("No Selection", "Please select an invoice to view.")
        invoice_id = int(selected[0])
        self.controller.show_invoice_generator(invoice_id=invoice_id)

    def cancel_invoice(self):
        """Cancel the selected invoice per Nepal IRD rules."""
        selected = self.invoice_table.selection()
        if not selected:
            return messagebox.showwarning("No Selection", "Please select an invoice to cancel.")

        invoice_id = int(selected[0])
        invoice = self._invoice_map.get(selected[0])

        if invoice and invoice.get("status") == "CANCELLED":
            return messagebox.showinfo("Already Cancelled",
                                       "This invoice is already cancelled.")

        inv_num = invoice["invoice_number"] if invoice else f"#{invoice_id}"

        # Open Custom Dialog
        dialog = CancelInvoiceDialog(self, inv_num)
        self.wait_window(dialog)
        
        if not dialog.result:
            return  # User cancelled

        reason, comment = dialog.result

        try:
            InvoiceController.create_credit_note(invoice_id, reason, comment)
            self.load_invoices()
            messagebox.showinfo("Success",
                                f"Invoice {inv_num} cancelled.\n"
                                "Credit Note has been issued successfully.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel invoice: {e}")
