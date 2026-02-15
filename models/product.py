from config.database import connect_db


class Product:
    @staticmethod
    def add_product(name, price, hs_code, description='', unit='Ltr', category='Lubricant'):
        """Add a new product to the database."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Products (name, price, hs_code, description, unit, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, price, hs_code, description, unit, category))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_products():
        """Retrieve all products from the database."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, name, price, hs_code, description, unit, category FROM Products ORDER BY name")
        products = cursor.fetchall()
        conn.close()
        return products

    @staticmethod
    def get_product_by_id(product_id):
        """Retrieve a single product by its ID."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, name, price, hs_code, description, unit, category FROM Products WHERE product_id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        return product

    @staticmethod
    def search_products(keyword):
        """Search products by name, HS code, or category."""
        conn = connect_db()
        cursor = conn.cursor()
        like = f"%{keyword}%"
        cursor.execute('''
            SELECT product_id, name, price, hs_code, description, unit, category
            FROM Products
            WHERE name LIKE ? OR hs_code LIKE ? OR category LIKE ?
            ORDER BY name
        ''', (like, like, like))
        products = cursor.fetchall()
        conn.close()
        return products

    @staticmethod
    def update_product(product_id, name, price, hs_code, description='', unit='Ltr', category='Lubricant'):
        """Update an existing product."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Products
            SET name = ?, price = ?, hs_code = ?, description = ?, unit = ?, category = ?
            WHERE product_id = ?
        ''', (name, price, hs_code, description, unit, category, product_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_product(product_id):
        """Delete a product from the database."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Products WHERE product_id = ?', (product_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_product_count():
        """Get the total number of products."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Products")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    @staticmethod
    def get_category_count():
        """Get the number of distinct categories."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT category) FROM Products")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    @staticmethod
    def get_average_price():
        """Get the average product price."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(price) FROM Products")
        avg = cursor.fetchone()[0]
        conn.close()
        return avg if avg else 0.0
