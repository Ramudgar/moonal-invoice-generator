"""
InvoiceManagementView — Invoice history with light golden theme.
Renders inside AppShell content area.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import Settings
from controllers.invoice_controller import InvoiceController


class InvoiceManagementView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.C = Settings.COLORS
        self.F = Settings.FONTS
        self.configure(bg=self.C["bg"])
        self._build_ui()
        self.load_invoices()

    def _build_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg="white", padx=20, pady=12,
                           highlightbackground=self.C["border"], highlightthickness=1)
        toolbar.pack(fill="x", padx=24, pady=(16, 0))

        tk.Label(toolbar, text="🔍", font=("Segoe UI", 11),
                 bg="white", fg=self.C["muted"]).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.load_invoices())
        tk.Entry(toolbar, textvariable=self.search_var, font=self.F["body"],
                 bg=self.C["input_bg"], relief="flat", highlightthickness=2,
                 highlightbackground=self.C["input_border"],
                 highlightcolor=self.C["primary"]).pack(
            side="left", fill="x", expand=True, ipady=5, padx=(8, 16))

        ttk.Button(toolbar, text="📄 View", style="Gold.TButton",
                    command=self.view_invoice).pack(side="right", padx=(4, 0))
        ttk.Button(toolbar, text="❌ Cancel", style="Danger.TButton",
                    command=self.cancel_invoice).pack(side="right", padx=(4, 0))

        # Table
        table_frame = tk.Frame(self, bg="white",
                               highlightbackground=self.C["border"], highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=24, pady=16)

        cols = ("ID", "Invoice #", "Client", "Total", "Paid", "Due", "Status", "Date")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                  style="Custom.Treeview")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        widths = {"ID": 50, "Invoice #": 120, "Client": 160, "Total": 100,
                  "Paid": 100, "Due": 100, "Status": 80, "Date": 100}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=widths.get(c, 100))

        self.tree.bind("<Double-1>", lambda e: self.view_invoice())

    def load_invoices(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            invoices = InvoiceController.get_all_invoices()
        except Exception:
            invoices = []

        search = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        for inv in invoices:
            # Check if search term matches any visible text in the row
            if search:
                row_str = f"{inv['invoice_number']} {inv['client_name']} {inv['status']}".lower()
                if search not in row_str:
                    continue
            
            status = inv.get("status", "ACTIVE")
            tag = "cancelled" if status == "CANCELLED" else ""
            
            # Format row for treeview: (id, num, client, total, paid, due, status, date)
            # Note: The controller only returns a partial dict in get_all_invoices
            self.tree.insert("", "end", values=(
                inv["invoice_id"], inv["invoice_number"], inv["client_name"],
                f"Rs. {inv['total_amount']:,.2f}", 
                f"Rs. {inv.get('paid_amount', 0):,.2f}",
                f"Rs. {inv.get('due_amount', 0):,.2f}",
                status, inv["date"]
            ), tags=(tag,))

        self.tree.tag_configure("cancelled", foreground=self.C["danger"])

    def view_invoice(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showinfo("Select", "Select an invoice first.")
        inv_id = self.tree.item(sel[0])["values"][0]
        self.controller.show_invoice_generator(invoice_id=inv_id)

    def cancel_invoice(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showinfo("Select", "Select an invoice to cancel.")
        inv_id = self.tree.item(sel[0])["values"][0]

        # Cancel dialog
        dialog = tk.Toplevel(self)
        dialog.title("Cancel Invoice")
        dialog.geometry("420x350")
        dialog.configure(bg="white")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Cancel Invoice", font=self.F["h3"],
                 bg="white", fg=self.C["danger"]).pack(pady=(20, 8))
        tk.Label(dialog, text="This action cannot be undone.", font=self.F["small"],
                 bg="white", fg=self.C["secondary"]).pack()

        tk.Label(dialog, text="REASON FOR CANCELLATION", font=self.F["small_bold"],
                 bg="white", fg=self.C["secondary"]).pack(anchor="w", padx=30, pady=(16, 4))
        
        reason_var = tk.StringVar()
        reason_combo = ttk.Combobox(dialog, textvariable=reason_var, state="readonly", font=self.F["body"])
        reason_combo['values'] = InvoiceController.CANCELLATION_REASONS
        reason_combo.pack(fill="x", padx=30, ipady=3)
        reason_combo.set("Select a reason...")

        tk.Label(dialog, text="COMMENT (OPTIONAL)", font=self.F["small_bold"],
                 bg="white", fg=self.C["secondary"]).pack(anchor="w", padx=30, pady=(12, 4))
        comment_entry = tk.Entry(dialog, font=self.F["body"], bg=self.C["input_bg"],
                                  relief="flat", highlightthickness=2,
                                  highlightbackground=self.C["input_border"],
                                  highlightcolor=self.C["primary"])
        comment_entry.pack(fill="x", padx=30, ipady=5)

        btn_frame = tk.Frame(dialog, bg="white")
        btn_frame.pack(fill="x", padx=30, pady=20)

        def do_cancel():
            reason = reason_var.get().strip()
            if not reason or reason == "Select a reason...":
                return messagebox.showerror("Required", "Please select a cancellation reason.")
            try:
                InvoiceController.cancel_invoice(inv_id, reason, comment_entry.get().strip())
                dialog.destroy()
                messagebox.showinfo("Cancelled", "Invoice has been cancelled.")
                self.load_invoices()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(btn_frame, text="Confirm Cancel", style="Danger.TButton",
                    command=do_cancel).pack(side="right")
        ttk.Button(btn_frame, text="Go Back", style="Ghost.TButton",
                    command=dialog.destroy).pack(side="left")
