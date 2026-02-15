from models.product import Product


class ProductController:
    # Predefined options for dropdowns
    UNITS = ['Ltr', 'Kg', 'Pcs', 'Box', 'Drum', 'Barrel', 'Gallon', 'Pack']
    CATEGORIES = ['Lubricant', 'Engine Oil', 'Gear Oil', 'Hydraulic Oil', 'Grease', 'Coolant', 'Brake Fluid', 'Transmission Fluid', 'Other']

    @staticmethod
    def add_product(name, price, hs_code, description='', unit='Ltr', category='Lubricant'):
        """Add a new product to the database with full validation."""
        name = name.strip()
        if not name:
            raise ValueError("Product name is required.")
        price = float(price)
        if price < 0:
            raise ValueError("Price must be non-negative.")
        Product.add_product(name, price, hs_code.strip(), description.strip(), unit, category)

    @staticmethod
    def get_all_products():
        """Retrieve all products from the database."""
        return Product.get_all_products()

    @staticmethod
    def search_products(keyword):
        """Search products by name, HS code, or category."""
        return Product.search_products(keyword.strip())

    @staticmethod
    def update_product(product_id, name, price, hs_code, description='', unit='Ltr', category='Lubricant'):
        """Update an existing product with full validation."""
        name = name.strip()
        if not product_id:
            raise ValueError("Product ID is required.")
        if not name:
            raise ValueError("Product name is required.")
        price = float(price)
        if price < 0:
            raise ValueError("Price must be non-negative.")
        Product.update_product(product_id, name, price, hs_code.strip(), description.strip(), unit, category)

    @staticmethod
    def delete_product(product_id):
        """Delete a product from the database."""
        if not product_id:
            raise ValueError("Product ID is required to delete a product.")
        Product.delete_product(product_id)

    @staticmethod
    def get_stats():
        """Return (total_count, category_count, avg_price) for the stats bar."""
        return (
            Product.get_product_count(),
            Product.get_category_count(),
            Product.get_average_price()
        )
