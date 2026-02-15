import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry  # Try to use tkcalendar if available
from datetime import datetime, timedelta
from controllers.report_controller import ReportController
import csv

class ReportsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.COLORS = controller.COLORS
        self.configure(bg=self.COLORS["bg"])
        
        # Date defaults (Current Month)
        today = datetime.now()
        self.start_date = (today.replace(day=1)).strftime("%Y-%m-%d")
        self.end_date = today.strftime("%Y-%m-%d")

        self.style_setup()
        self._build_header()
        self._build_filters()
        self._build_stats_summary()
        self._build_table()
        self.load_report()

    def style_setup(self):
        style = ttk.Style()
        style.configure("Report.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), padding=5)

    def _build_header(self):
        header = tk.Frame(self, bg=self.COLORS["primary"], padx=20, pady=15)
        header.pack(fill="x")
        
        ttk.Button(header, text="← DASHBOARD", command=self.controller.show_dashboard).pack(side="left")
        tk.Label(header, text="📊 REPORTS & ANALYTICS", font=("Segoe UI", 16, "bold"), 
                 bg=self.COLORS["primary"], fg="white").pack(side="left", padx=20)

    def _build_filters(self):
        bar = tk.Frame(self, bg="white", padx=20, pady=15)
        bar.pack(fill="x")
        
        # Date Range
        tk.Label(bar, text="From:", bg="white", font=("Segoe UI", 10)).pack(side="left")
        self.start_entry = tk.Entry(bar, width=12, font=("Segoe UI", 10))
        self.start_entry.insert(0, self.start_date)
        self.start_entry.pack(side="left", padx=5)
        
        tk.Label(bar, text="To:", bg="white", font=("Segoe UI", 10)).pack(side="left", padx=(10, 0))
        self.end_entry = tk.Entry(bar, width=12, font=("Segoe UI", 10))
        self.end_entry.insert(0, self.end_date)
        self.end_entry.pack(side="left", padx=5)
        
        ttk.Button(bar, text="Apply Filter", command=self.load_report).pack(side="left", padx=15)
        
        # Exports
        ttk.Button(bar, text="⬇ Export Excel", command=self.export_excel).pack(side="right")

    def _build_stats_summary(self):
        self.stats_frame = tk.Frame(self, bg="white", padx=20, pady=10)
        self.stats_frame.pack(fill="x", pady=(1, 0))
        
        self.lbl_sales = self._make_card("NET SUBSALES", "Rs. 0.00")
        self.lbl_vat = self._make_card("NET VAT", "Rs. 0.00")
        self.lbl_total = self._make_card("GRAND TOTAL", "Rs. 0.00")

    def _make_card(self, title, val):
        f = tk.Frame(self.stats_frame, bg="#F5F5F5", padx=20, pady=10, relief="flat")
        f.pack(side="left", padx=10, fill="x", expand=True)
        tk.Label(f, text=title, font=("Segoe UI", 8, "bold"), bg="#F5F5F5", fg=self.COLORS["secondary"]).pack(anchor="w")
        l = tk.Label(f, text=val, font=("Segoe UI", 14, "bold"), bg="#F5F5F5", fg=self.COLORS["primary"])
        l.pack(anchor="w")
        return l

    def _build_table(self):
        frame = tk.Frame(self, bg="white", padx=20, pady=10)
        frame.pack(fill="both", expand=True)
        
        cols = ("Date", "Inv No", "Customer", "PAN", "Type", "Taxable", "VAT", "Total")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)
        
        self.tree.heading("Date", text="DATE"); self.tree.column("Date", width=90)
        self.tree.heading("Inv No", text="INVOICE NO"); self.tree.column("Inv No", width=120)
        self.tree.heading("Customer", text="CUSTOMER"); self.tree.column("Customer", width=180)
        self.tree.heading("PAN", text="PAN NO"); self.tree.column("PAN", width=100)
        self.tree.heading("Type", text="TYPE"); self.tree.column("Type", width=80, anchor="center")
        self.tree.heading("Taxable", text="TAXABLE"); self.tree.column("Taxable", width=100, anchor="e")
        self.tree.heading("VAT", text="VAT"); self.tree.column("VAT", width=90, anchor="e")
        self.tree.heading("Total", text="TOTAL"); self.tree.column("Total", width=110, anchor="e")
        
        sc = ttk.Scrollbar(frame, command=self.tree.yview)
        self.tree.config(yscrollcommand=sc.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        
        self.tree.tag_configure("cn", background="#FFFDE7", foreground="#E65100")

    def load_report(self):
        s = self.start_entry.get()
        e = self.end_entry.get()
        
        try:
            # Validate dates
            datetime.strptime(s, "%Y-%m-%d")
            datetime.strptime(e, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return

        for i in self.tree.get_children(): self.tree.delete(i)
        
        data = ReportController.get_sales_register(s, e)
        
        t_sub = 0; t_vat = 0; t_tot = 0
        
        for row in data:
            # row is dict
            total = float(row.get("Total", 0))
            sub = float(row.get("Taxable", 0))
            vat = float(row.get("VAT", 0))
            
            # Since Credit Notes are stored as negative in DB items, their totals should be negative.
            # However, ensure get_sales_register logic handles it. 
            # In InvoiceController.create_credit_note, we use negative quantities.
            # So sums stored in Invoices table should be negative.
            
            t_sub += sub; t_vat += vat; t_tot += total
            
            tag = "cn" if row["Type"] == "Credit Note" else ""
            self.tree.insert("", "end", values=(
                row["Date"], row["Invoice No"], row["Customer"], row["PAN"], row["Type"],
                f"{sub:,.2f}", f"{vat:,.2f}", f"{total:,.2f}"
            ), tags=(tag,))
            
        self.lbl_sales.config(text=f"Rs. {t_sub:,.2f}")
        self.lbl_vat.config(text=f"Rs. {t_vat:,.2f}")
        self.lbl_total.config(text=f"Rs. {t_tot:,.2f}")
        
        self.current_data = data

    def export_excel(self):
        if not hasattr(self, 'current_data') or not self.current_data:
            return messagebox.showwarning("No Data", "Generate a report first.")
            
        fn = filedialog.asksaveasfilename(defaultextension=".csv", 
                                          filetypes=[("CSV File", "*.csv"), ("Excel File", "*.xlsx")])
        if not fn: return
        
        # Use CSV for robust fallback without dependencies
        try:
            with open(fn, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=self.current_data[0].keys())
                w.writeheader()
                w.writerows(self.current_data)
            messagebox.showinfo("Export Successful", f"Report saved to {fn}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
