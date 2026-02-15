from config.database import connect_db
from datetime import datetime
from utils.invoice_utils import InvoiceUtils
 

class InvoiceController:
    
    CANCELLATION_REASONS = [
        "Business permanently closed",
        "Business sold, transferred, or merged",
        "Business no longer VAT-eligible",
        "Registered by mistake",
        "Duplicate VAT registration",
        "Wrong PAN/VAT number",
        "Invoice issued by mistake",
        "Customer returned goods",
        "Incorrect VAT calculation",
        "Discount applied after invoice"
    ]

    @staticmethod
    def create_invoice(invoice_number, client_name, client_contact, address, pan_no, items, vat_rate, discount, paid_amount, is_credit_note=False, original_invoice_id=None, cancellation_comment=''):
        conn = connect_db()
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d")
        
        # Convert and validate item data to ensure proper calculations
        for item in items:
            item['quantity'] = int(item['quantity'])
            item['price_per_unit'] = float(item['price_per_unit'])

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

        # Insert invoice data
        cursor.execute('''
            INSERT INTO Invoices (client_name, client_contact, address, pan_no, invoice_number, date, subtotal, vat_amount, discount, total_amount, vat_rate, paid_amount, due_amount, status, is_credit_note, credit_note_number, cancellation_comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?, ?)
        ''', (client_name, client_contact, address, pan_no, invoice_number, date, subtotal, vat_amount, discount, total_amount, vat_rate, paid_amount, due_amount, 1 if is_credit_note else 0, invoice_number if is_credit_note else None, cancellation_comment))
        
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
        """Retrieve all invoices with status for management view."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT invoice_id, invoice_number, client_name, date, total_amount,
                   COALESCE(status, 'ACTIVE') as status,
                   is_credit_note
            FROM Invoices
            ORDER BY invoice_id DESC
        """)
        invoices = [{
            "invoice_id": row[0],
            "invoice_number": row[1],
            "client_name": row[2],
            "date": row[3],
            "total_amount": row[4],
            "status": row[5],
            "is_credit_note": row[6]
        } for row in cursor.fetchall()]
        conn.close()
        return invoices

    
    @staticmethod
    def get_invoice_details(invoice_id):
        """Retrieve invoice details and items from the database by invoice_id."""
        conn = connect_db()
        cursor = conn.cursor()

        # Fetch invoice data with all relevant fields including status
        cursor.execute("""
            SELECT invoice_number, client_name, client_contact, address, pan_no, date,
                   subtotal, vat_amount, discount, total_amount, vat_rate, paid_amount, due_amount,
                   COALESCE(status, 'ACTIVE'), COALESCE(cancel_reason, ''), COALESCE(cancelled_date, ''),
                   is_credit_note, credit_note_number, COALESCE(cancellation_comment, '')
            FROM Invoices
            WHERE invoice_id = ?
        """, (invoice_id,))
        invoice_data = cursor.fetchone()
        
        if invoice_data:
            invoice_data = {
                "invoice_number": invoice_data[0],
                "client_name": invoice_data[1],
                "client_contact": invoice_data[2],
                "address": invoice_data[3],
                "pan_no": invoice_data[4],
                "date": invoice_data[5],
                "subtotal": invoice_data[6],
                "vat_amount": invoice_data[7],
                "discount": invoice_data[8],
                "total_amount": invoice_data[9],
                "vat_rate": invoice_data[10],
                "paid_amount": invoice_data[11],
                "due_amount": invoice_data[12],
                "status": invoice_data[13],
                "cancel_reason": invoice_data[14],
                "cancelled_date": invoice_data[15],
                "is_credit_note": invoice_data[16],
                "credit_note_number": invoice_data[17],
                "cancellation_comment": invoice_data[18]
            }

            # Fetch invoice items along with hs_code
            cursor.execute("""
                SELECT Products.name, Products.hs_code, Invoice_Items.quantity,
                       Invoice_Items.price_per_unit, Invoice_Items.total_price
                FROM Invoice_Items
                JOIN Products ON Invoice_Items.product_id = Products.product_id
                WHERE Invoice_Items.invoice_id = ?
            """, (invoice_id,))
            items = [{
                "product_name": item[0],
                "hs_code": item[1],
                "quantity": item[2],
                "price_per_unit": item[3],
                "total_price": item[4]
            } for item in cursor.fetchall()]

            conn.close()
            return invoice_data, items
        else:
            conn.close()
            raise ValueError("Invoice not found")


    @staticmethod
    def create_credit_note(original_invoice_id, reason, comment):
        """
        Create a Credit Note to cancel an existing invoice per Nepal IRD rules.
        1. Marks original invoice as CANCELLED.
        2. Creates a new invoice record with negative amounts (Credit Note).
        """
        if not reason:
            raise ValueError("Cancellation reason is required.")
        
        conn = connect_db()
        cursor = conn.cursor()

        # Get original invoice details
        cursor.execute("SELECT * FROM Invoices WHERE invoice_id = ?", (original_invoice_id,))
        # Convert row to dict for easier access (assuming row order matches columns but better to select specific columns)
        # Using get_invoice_details to act as a helper is cleaner but circular import risk.
        # Let's fetch raw data. Need enough info to replicate.
        pass # Actual logic below

        # Fetch full details using existing helper logic (re-implemented to stay within method)
        # Using get_invoice_details logic inline to avoid double connection
        # Re-using create_invoice logic? No, create_invoice opens its own connection.
        conn.close() # Close to use high-level methods

        # 1. Get original data
        original_data, original_items = InvoiceController.get_invoice_details(original_invoice_id)
        
        if original_data['status'] == 'CANCELLED':
            raise ValueError("This invoice is already cancelled.")

        # 2. Prepare negative items for Credit Note
        cn_items = []
        for item in original_items:
            # Need product_id. get_invoice_details doesn't return it.
            # We need to fetch product_id for these items. 
            # This is tricky. Let's do a direct query for items with product_ids.
            pass

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, quantity, price_per_unit FROM Invoice_Items WHERE invoice_id = ?", (original_invoice_id,))
        raw_items = cursor.fetchall()

        if not raw_items:
             conn.close()
             raise ValueError("Original invoice has no items.")

        cn_items = []
        for pid, qty, price in raw_items:
            cn_items.append({
                'product_id': pid,
                'quantity': -qty,          # Negative quantity
                'price_per_unit': price,
                'total_price': -qty * price
            })
        
        # 3. Mark original as CANCELLED
        cancelled_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        full_reason = f"{reason}" + (f" | {comment}" if comment else "")
        cursor.execute("""
            UPDATE Invoices
            SET status = 'CANCELLED', cancel_reason = ?, cancelled_date = ?
            WHERE invoice_id = ?
        """, (full_reason, cancelled_date, original_invoice_id))
        conn.commit()
        conn.close()

        # 4. Generate Credit Note Number (using same sequence but different prefix? No, same sequence usually)
        # IRD allows CN to have its own sequence or share sequence. Let's use standard sequence with CN prefix for clarity?
        # Actually standard practice is Credit Notes have their own separate sequence.
        # For simplicity in this app, we will use the MAIN sequence but label it clearly.
        # Or better: "CN/081-82/xxxx"
        
        fiscal_year = InvoiceUtils.get_fiscal_year_nepali()
        cn_number = InvoiceController.get_next_invoice_number(fiscal_year).replace("MU/", "CN/") 
        # Note: referencing get_next_invoice_number might return MU/... so we replace it.
        # But wait, get_next_invoice_number looks at "MU/" pattern. 
        # We need a separate sequence for CN.
        
        conn = connect_db()
        cursor = conn.cursor()
        # Find next CN number
        pattern = f"CN/{fiscal_year}/%"
        cursor.execute("SELECT credit_note_number FROM Invoices WHERE credit_note_number LIKE ? ORDER BY invoice_id DESC LIMIT 1", (pattern,))
        last_cn = cursor.fetchone()
        if last_cn:
            try:
                last_num = int(last_cn[0].split('/')[-1])
                new_num = last_num + 1
            except: new_num = 1
        else:
            new_num = 1
        cn_number = f"CN/{fiscal_year}/{new_num:04d}"
        conn.close()

        # 5. Create Credit Note Record
        # We pass negative quantities, so totals will be negative automatically
        InvoiceController.create_invoice(
            invoice_number=cn_number,
            client_name=original_data['client_name'],
            client_contact=original_data['client_contact'],
            address=original_data['address'],
            pan_no=original_data['pan_no'],
            items=cn_items,
            vat_rate=original_data['vat_rate'],
            discount=original_data['discount'],
            paid_amount=0, # CN is not "paid", it's an adjustment
            is_credit_note=True,
            original_invoice_id=original_invoice_id,
            cancellation_comment=comment
        )


    @staticmethod
    def get_next_invoice_number(fiscal_year):
        """
        Get the next strictly sequential invoice number for the fiscal year.
        Uses a transaction to prevent race conditions in multi-user environments.
        """
        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            # Begin exclusive transaction to lock the table
            cursor.execute("BEGIN EXCLUSIVE")
            
            # Search for max invoice number in current fiscal year (MU/FY/XXXX)
            pattern = f"MU/{fiscal_year}/%"
            cursor.execute("""
                SELECT invoice_number FROM Invoices 
                WHERE invoice_number LIKE ? 
                ORDER BY invoice_id DESC LIMIT 1
            """, (pattern,))
            
            last_invoice = cursor.fetchone()
            
            if last_invoice:
                try:
                    # Extract number part (MU/081-82/0005 -> 5)
                    last_num = int(last_invoice[0].split('/')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
                
            return f"MU/{fiscal_year}/{new_num:04d}"
            
        except Exception as e:
            print(f"Error generating invoice number: {e}")
            return f"MU/{fiscal_year}/ERROR"
        finally:
            conn.close()
