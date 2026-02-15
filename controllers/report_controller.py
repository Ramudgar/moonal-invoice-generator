import sqlite3
import csv
from datetime import datetime
from config.database import connect_db

class ReportController:
    
    @staticmethod
    def get_sales_register(start_date, end_date):
        """
        Fetch sales register data for VAT reporting.
        Includes both Invoices (Positive) and Credit Notes (Negative).
        """
        conn = connect_db()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                date,
                invoice_number,
                client_name,
                pan_no,
                subtotal as taxable_amount,
                vat_amount,
                total_amount,
                is_credit_note,
                status
            FROM Invoices
            WHERE date BETWEEN ? AND ?
            AND status != 'CANCELLED' 
            ORDER BY date ASC, invoice_id ASC
        """
        # Note: We exclude 'CANCELLED' status for original invoices because 
        # the Credit Note (active) negates them. 
        # WAIT. IRD rules: 
        # 1. Original Invoice (Active -> Cancelled) is still part of the sequential history?
        #    Usually, a Cancelled invoice should appear in the register but with distinct marking, 
        #    or the Credit Note acts as the reversal.
        #    If we hide 'CANCELLED', the original sale disappears.
        #    But the Credit Note (also 'ACTIVE' record) appears with negative amount.
        #    So Net Effect = 0.
        #    However, if we hide 'CANCELLED', then we only have the Credit Note (Negative).
        #    Net Effect = Negative! That is wrong.
        #    Correction: We must INCLUDE 'CANCELLED' invoices in the report to show the original sale,
        #    AND the Credit Note to show the reversal.
        #    Both sum up to 0.
        
        query = """
            SELECT 
                date,
                invoice_number,
                client_name,
                pan_no,
                subtotal as taxable_amount,
                vat_amount,
                total_amount,
                is_credit_note,
                status
            FROM Invoices
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC, invoice_id ASC
        """
        
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            # If it's a Credit Note, amounts are already negative in DB?
            # Let's check create_credit_note... 
            # Yes, we store negative quantities in items, so totals are negative.
            # So simple summation works.
            
            data.append({
                "Date": row[0],
                "Invoice No": row[1],
                "Customer": row[2],
                "PAN": row[3],
                "Taxable": row[4],
                "VAT": row[5],
                "Total": row[6],
                "Type": "Credit Note" if row[7] else \
                        ("Cancelled" if row[8] == 'CANCELLED' else "Invoice")
            })
            
        conn.close()
        return data

    @staticmethod
    def get_monthly_summary(fiscal_year):
        """Aggregate sales by month for the dashboard."""
        conn = connect_db()
        cursor = conn.cursor()
        
        # We need to filter by fiscal year pattern in invoice_number "MU/081-82/..."
        # Or just use date range if we knew it. 
        # Let's use the fiscal year string "081-82" in invoice_number for accuracy
        
        query = """
            SELECT strftime('%Y-%m', date) as month, SUM(total_amount)
            FROM Invoices
            WHERE invoice_number LIKE ?
            GROUP BY month
            ORDER BY month ASC
        """
        pattern = f"%/{fiscal_year}/%"
        cursor.execute(query, (pattern,))
        results = cursor.fetchall()
        conn.close()
        
        # Convert to dictionary {Month: Total}
        return {row[0]: row[1] for row in results}

    @staticmethod
    def export_to_excel(data, filename):
        """Export list of dicts to CSV (Excel compatible)."""
        if not data:
            return False
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
