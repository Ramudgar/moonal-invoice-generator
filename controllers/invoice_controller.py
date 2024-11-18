from config.database import connect_db
from datetime import datetime

class InvoiceController:
    @staticmethod
    def create_invoice(client_name, client_contact, address, pan_no, items, vat_rate, discount, paid_amount):
        conn = connect_db()
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate subtotal, VAT, discount, and due amount
        subtotal = sum(item['price_per_unit'] * item['quantity'] for item in items)
        discount = float(discount)

        # Validate discount rate
        if discount > 100 or discount < 0:
            raise ValueError("Discount must be between 0 and 100%")

        discount_amount = subtotal * (discount / 100)
        price_after_discount = subtotal - discount_amount
        vat_amount = price_after_discount * (vat_rate / 100)
        total_amount = price_after_discount + vat_amount 
        due_amount = total_amount - paid_amount

        # Generate unique invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Insert invoice data
        cursor.execute('''
            INSERT INTO Invoices (client_name, client_contact, address, pan_no, invoice_number, date, subtotal, vat_amount, discount, total_amount, vat_rate, paid_amount, due_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (client_name, client_contact, address, pan_no, invoice_number, date, subtotal, vat_amount, discount_amount, total_amount, vat_rate, paid_amount, due_amount))
        
        invoice_id = cursor.lastrowid

        # Insert invoice items
        for item in items:
            cursor.execute('''
                INSERT INTO Invoice_Items (invoice_id, product_id, quantity, price_per_unit, total_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (invoice_id, item['product_id'], item['quantity'], item['price_per_unit'], item['quantity'] * item['price_per_unit']))

        conn.commit()
        conn.close()
        return invoice_id
    
    @staticmethod
    def get_all_invoices():
        """Retrieve all invoices from the database."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT invoice_id, client_name, date, total_amount FROM Invoices")
        invoices = cursor.fetchall()
        conn.close()
        return invoices
    
    @staticmethod
    def get_invoice_details(invoice_id):
        """Retrieve invoice details and items from the database by invoice_id."""
        conn = connect_db()
        cursor = conn.cursor()

        # Fetch invoice data with all relevant fields
        cursor.execute("""
            SELECT client_name, client_contact, address, pan_no, date, subtotal, vat_amount, discount, total_amount, vat_rate, paid_amount, due_amount
            FROM Invoices
            WHERE invoice_id = ?
        """, (invoice_id,))
        invoice_data = cursor.fetchone()
        
        if invoice_data:
            # Prepare the invoice data dictionary
            invoice_data = {
                "client_name": invoice_data[0],
                "client_contact": invoice_data[1],
                "address": invoice_data[2],
                "pan_no": invoice_data[3],
                "date": invoice_data[4],
                "subtotal": invoice_data[5],
                "vat_amount": invoice_data[6],
                "discount": invoice_data[7],
                "total_amount": invoice_data[8],
                "vat_rate": invoice_data[9],
                "paid_amount": invoice_data[10],
                "due_amount": invoice_data[11]
            }

            # Fetch invoice items
            cursor.execute("""
                SELECT Products.name, Invoice_Items.quantity, Invoice_Items.price_per_unit, Invoice_Items.total_price
                FROM Invoice_Items
                JOIN Products ON Invoice_Items.product_id = Products.product_id
                WHERE Invoice_Items.invoice_id = ?
            """, (invoice_id,))
            items = [{
                "product_name": item[0],
                "quantity": item[1],
                "price_per_unit": item[2],
                "total_price": item[3]
            } for item in cursor.fetchall()]

            conn.close()
            return invoice_data, items
        else:
            conn.close()
            raise ValueError("Invoice not found")

    @staticmethod
    def delete_invoice(invoice_id):
        """Delete an invoice and its items by its ID."""
        conn = connect_db()
        cursor = conn.cursor()
        
        # Delete associated items first to maintain referential integrity
        cursor.execute("DELETE FROM Invoice_Items WHERE invoice_id = ?", (invoice_id,))
        cursor.execute("DELETE FROM Invoices WHERE invoice_id = ?", (invoice_id,))
        
        conn.commit()
        conn.close()
