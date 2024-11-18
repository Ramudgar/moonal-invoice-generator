from models.product import Product


class ProductController:
    @staticmethod
    def add_product(name, price, hs_code):
        """Add a new product to the database."""
        if name and price >= 0:
            Product.add_product(name, price, hs_code)
        else:
            raise ValueError(
                "Product name and price must be provided, and price must be non-negative.")

    @staticmethod
    def get_all_products():
        """Retrieve all products from the database."""
        return Product.get_all_products()

    @staticmethod
    def update_product(product_id, name, price, hs_code):
        """Update an existing product's name and price."""
        if product_id and name and price >= 0:
            Product.update_product(product_id, name, price, hs_code)
        else:
            raise ValueError(
                "Product ID, name, and price must be provided, and price must be non-negative.")

    @staticmethod
    def delete_product(product_id):
        """Delete a product from the database."""
        if product_id:
            Product.delete_product(product_id)
        else:
            raise ValueError(
                "Product ID must be provided to delete a product.")
