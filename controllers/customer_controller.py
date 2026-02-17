from config.database import connect_db

class CustomerController:
    @staticmethod
    def add_customer(name, pan_vat, address, contact_person, mobile, email):
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO customers (name, pan_vat, address, contact_person, mobile, email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, pan_vat, address, contact_person, mobile, email))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def update_customer(customer_id, name, pan_vat, address, contact_person, mobile, email):
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE customers 
                SET name=?, pan_vat=?, address=?, contact_person=?, mobile=?, email=?
                WHERE id=?
            """, (name, pan_vat, address, contact_person, mobile, email, customer_id))
            conn.commit()
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete_customer(customer_id):
        conn = connect_db()
        try:
            conn.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            conn.commit()
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_all_customers():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def search_customers(query):
        conn = connect_db()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT * FROM customers 
            WHERE name LIKE ? OR pan_vat LIKE ? OR mobile LIKE ?
            ORDER BY name ASC
        """, (search_term, search_term, search_term))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_customer_by_id(customer_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()
        return row
