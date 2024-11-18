from config.database import connect_db


class Product:
    @staticmethod
    def add_product(name, price, hs_code):
        """Add a new product to the database."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Products (name, price, hs_code)
            VALUES (?, ?, ?)
        ''', (name, price, hs_code))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_products():
        """Retrieve all products from the database."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()
        conn.close()
        return products

    @staticmethod
    def update_product(product_id, name, price, hs_code):
        """Update an existing product's name,price and hs_code."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Products
            SET name = ?, price = ?, hs_code = ?
            WHERE product_id = ?
        ''', (name, price, hs_code, product_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_product(product_id):
        """Delete a product from the database."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM Products
            WHERE product_id = ?
        ''', (product_id,))
        conn.commit()
        conn.close()
