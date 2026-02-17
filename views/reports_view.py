"""
ReportsView — Sales reports with light golden theme.
Renders inside AppShell content area.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from config.settings import Settings
from controllers.report_controller import ReportController
import csv
import os

try:
    from tkcalendar import DateEntry
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False


class ReportsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.C = Settings.COLORS
        self.F = Settings.FONTS
        self.configure(bg=self.C["bg"])
        self._build_ui()

    def _build_ui(self):
        # Filters bar
        filters = tk.Frame(self, bg="white", padx=20, pady=14,
                           highlightbackground=self.C["border"], highlightthickness=1)
        filters.pack(fill="x", padx=24, pady=(16, 0))

        tk.Label(filters, text="Date Range:", font=self.F["body_bold"],
                 bg="white", fg=self.C["text"]).pack(side="left")

        if HAS_CALENDAR:
            self.start_date = DateEntry(filters, font=self.F["body"], width=12)
            self.start_date.pack(side="left", padx=(8, 4))
            tk.Label(filters, text="to", bg="white", fg=self.C["secondary"],
                     font=self.F["body"]).pack(side="left")
            self.end_date = DateEntry(filters, font=self.F["body"], width=12)
            self.end_date.pack(side="left", padx=(4, 12))
        else:
            tk.Label(filters, text="From:", bg="white", fg=self.C["secondary"],
                     font=self.F["small"]).pack(side="left", padx=(8, 2))
            self.start_date = tk.Entry(filters, font=self.F["body"], width=12,
                                        bg=self.C["input_bg"], relief="flat",
                                        highlightthickness=2,
                                        highlightbackground=self.C["input_border"],
                                        highlightcolor=self.C["primary"])
            self.start_date.pack(side="left", padx=(0, 4), ipady=3)
            self.start_date.insert(0, "2024-01-01")

            tk.Label(filters, text="To:", bg="white", fg=self.C["secondary"],
                     font=self.F["small"]).pack(side="left", padx=(4, 2))
            self.end_date = tk.Entry(filters, font=self.F["body"], width=12,
                                      bg=self.C["input_bg"], relief="flat",
                                      highlightthickness=2,
                                      highlightbackground=self.C["input_border"],
                                      highlightcolor=self.C["primary"])
            self.end_date.pack(side="left", padx=(0, 12), ipady=3)
            self.end_date.insert(0, "2025-12-31")

        ttk.Button(filters, text="Generate Report", style="Gold.TButton",
                    command=self.generate_report).pack(side="left", padx=4)
        ttk.Button(filters, text="📥 Export CSV", style="Ghost.TButton",
                    command=self.export_csv).pack(side="right")

        # Stats cards
        self.stats_frame = tk.Frame(self, bg=self.C["bg"], padx=24, pady=12)
        self.stats_frame.pack(fill="x")

        # Table
        table_frame = tk.Frame(self, bg="white",
                               highlightbackground=self.C["border"], highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        cols = ("Date", "Invoice #", "Customer", "PAN", "Taxable", "VAT", "Total", "Type")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                  style="Custom.Treeview")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100 if len(c) < 5 else 125)

    def generate_report(self):
        try:
            if HAS_CALENDAR:
                start = self.start_date.get_date().strftime("%Y-%m-%d")
                end = self.end_date.get_date().strftime("%Y-%m-%d")
            else:
                start = self.start_date.get().strip()
                end = self.end_date.get().strip()

            data = ReportController.get_sales_register(start, end)

            # Clear table
            for i in self.tree.get_children():
                self.tree.delete(i)

            total_revenue = 0
            total_vat = 0
            total_taxable = 0

            for row in data:
                # row is a dict: {"Date", "Invoice No", "Customer", "PAN", "Taxable", "VAT", "Total", "Type"}
                self.tree.insert("", "end", values=(
                    row["Date"], row["Invoice No"], row["Customer"], row["PAN"],
                    f"Rs. {row['Taxable']:,.2f}", f"Rs. {row['VAT']:,.2f}",
                    f"Rs. {row['Total']:,.2f}", row["Type"]
                ))
                try:
                    total_revenue += float(row["Total"])
                    total_vat += float(row["VAT"])
                    total_taxable += float(row["Taxable"])
                except (ValueError, TypeError):
                    pass

            # Update stats
            for w in self.stats_frame.winfo_children():
                w.destroy()

            stats = [
                ("Total Revenue", f"Rs. {total_revenue:,.0f}", self.C["primary"]),
                ("Taxable Amount", f"Rs. {total_taxable:,.0f}", self.C["info"]),
                ("VAT Collected", f"Rs. {total_vat:,.0f}", self.C["success"]),
                ("Record Count", str(len(data)), self.C["warning"]),
            ]

            for i, (lbl, val, color) in enumerate(stats):
                card = tk.Frame(self.stats_frame, bg="white", padx=16, pady=12,
                               highlightbackground=self.C["border"], highlightthickness=1)
                card.pack(side="left", fill="x", expand=True,
                          padx=(0 if i == 0 else 6, 0))
                tk.Frame(card, bg=color, height=3).pack(fill="x", pady=(0, 8))
                tk.Label(card, text=val, font=("Segoe UI", 16, "bold"),
                         bg="white", fg=self.C["text"]).pack(anchor="w")
                tk.Label(card, text=lbl, font=self.F["small"],
                         bg="white", fg=self.C["secondary"]).pack(anchor="w")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_csv(self):
        items = self.tree.get_children()
        if not items:
            return messagebox.showinfo("No Data", "Generate a report first.")
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                cols = [self.tree.heading(c)["text"] for c in self.tree["columns"]]
                writer.writerow(cols)
                for item in items:
                    writer.writerow(self.tree.item(item)["values"])
            messagebox.showinfo("Exported", f"Report saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
