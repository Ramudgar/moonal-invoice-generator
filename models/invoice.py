from config.database import connect_db
from datetime import datetime

class Invoice:
    @staticmethod
    def create_invoice(client_name, client_contact, address, pan_no, subtotal, vat_rate=13, discount=0, paid_amount=0):
        conn = connect_db()
        cursor = conn.cursor()
        
        # Calculate VAT, discount, total, and due amount
        vat_amount = subtotal * (vat_rate / 100)
        discount_amount = subtotal * (discount / 100)
        total_amount = subtotal + vat_amount - discount_amount
        due_amount = total_amount - paid_amount

        # Generate unique invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        date = datetime.now().strftime("%Y-%m-%d")

        # Insert invoice data
        cursor.execute('''
            INSERT INTO Invoices (client_name, client_contact, address, pan_no, invoice_number, date, subtotal, vat_amount, discount, total_amount, vat_rate, paid_amount, due_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (client_name, client_contact, address, pan_no, invoice_number, date, subtotal, vat_amount, discount_amount, total_amount, vat_rate, paid_amount, due_amount))
        
        invoice_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return invoice_id

    @staticmethod
    def get_invoice(invoice_id):
        """Retrieve a single invoice by its ID."""
        conn = connect_db()
        cursor = conn.cursor()
        
        # Retrieve invoice data with relevant fields
        cursor.execute('''
            SELECT client_name, client_contact, address, pan_no, invoice_number, date, subtotal, vat_amount, discount, total_amount, vat_rate, paid_amount, due_amount
            FROM Invoices
            WHERE invoice_id = ?
        ''', (invoice_id,))
        
        invoice_data = cursor.fetchone()
        conn.close()

        if invoice_data:
            return {
                "client_name": invoice_data[0],
                "client_contact": invoice_data[1],
                "address": invoice_data[2],
                "pan_no": invoice_data[3],
                "invoice_number": invoice_data[4],
                "date": invoice_data[5],
                "subtotal": invoice_data[6],
                "vat_amount": invoice_data[7],
                "discount": invoice_data[8],
                "total_amount": invoice_data[9],
                "vat_rate": invoice_data[10],
                "paid_amount": invoice_data[11],
                "due_amount": invoice_data[12],
            }
        else:
            raise ValueError("Invoice not found")

    @staticmethod
    def delete_invoice(invoice_id):
        """Delete an invoice by its ID."""
        conn = connect_db()
        cursor = conn.cursor()
        
        # Delete the invoice from the database
        cursor.execute("DELETE FROM Invoices WHERE invoice_id = ?", (invoice_id,))
        conn.commit()
        conn.close()
