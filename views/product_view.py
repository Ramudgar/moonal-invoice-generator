import tkinter as tk
from tkinter import ttk, messagebox
from controllers.product_controller import ProductController

class ProductView(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Product Management")
        self.geometry("850x450")

        # Product Form
        tk.Label(self, text="Product Name").grid(row=0, column=0, padx=10, pady=10)
        self.product_name_entry = tk.Entry(self)
        self.product_name_entry.grid(row=0, column=1, pady=10, ipadx=50)

        tk.Label(self, text="Product Price").grid(row=1, column=0, padx=10, pady=10)
        self.product_price_entry = tk.Entry(self)
        self.product_price_entry.grid(row=1, column=1, pady=10, ipadx=50)

        tk.Label(self, text="HS Code").grid(row=2, column=0, padx=10, pady=10)
        self.hs_code_entry = tk.Entry(self)
        self.hs_code_entry.grid(row=2, column=1, pady=10, ipadx=50)

        # Buttons for Add, Update, Delete
        self.add_button = tk.Button(self, text="Add Product", command=self.add_product)
        self.add_button.grid(row=3, column=0, padx=10, pady=10)
        
        self.update_button = tk.Button(self, text="Update Product", command=self.update_product)
        self.update_button.grid(row=3, column=1, padx=10, pady=10)

        self.delete_button = tk.Button(self, text="Delete Product", command=self.delete_product)
        self.delete_button.grid(row=3, column=2, padx=10, pady=10)

        # Product List Display
        self.product_list = ttk.Treeview(self, columns=("ID", "Name", "Price", "HS Code"), show="headings")
        self.product_list.heading("ID", text="ID")
        self.product_list.heading("Name", text="Name")
        self.product_list.heading("Price", text="Price")
        self.product_list.heading("HS Code", text="HS Code")
        self.product_list.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        self.product_list.bind("<Double-1>", self.load_product_data)

        # Load Products
        self.load_products()

    def add_product(self):
        name = self.product_name_entry.get()
        price = self.product_price_entry.get()
        hs_code = self.hs_code_entry.get()
        
        if not name or not price or not hs_code:
            messagebox.showerror("Error", "Please fill all fields before adding.", parent=self)
            return
        
        try:
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for price.", parent=self)
            return

        ProductController.add_product(name, price, hs_code)
        messagebox.showinfo("Success", "Product added successfully.", parent=self)
        self.clear_form()
        self.load_products()

    def update_product(self):
        selected_item = self.product_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to update.", parent=self)
            return

        product_id = self.product_list.item(selected_item, "values")[0]
        name = self.product_name_entry.get()
        price = self.product_price_entry.get()
        hs_code = self.hs_code_entry.get()

        if not name or not price or not hs_code:
            messagebox.showerror("Error", "Please fill all fields before updating.", parent=self)
            return

        try:
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for price.", parent=self)
            return

        ProductController.update_product(product_id, name, price, hs_code)
        messagebox.showinfo("Success", "Product updated successfully.", parent=self)
        self.clear_form()
        self.load_products()

    def delete_product(self):
        selected_item = self.product_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to delete.", parent=self)
            return

        product_id = self.product_list.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?", parent=self)
        if confirm:
            ProductController.delete_product(product_id)
            messagebox.showinfo("Success", "Product deleted successfully.", parent=self)
            self.clear_form()
            self.load_products()

    def load_products(self):
        for item in self.product_list.get_children():
            self.product_list.delete(item)  # Clear existing entries in the TreeView
        
        products = ProductController.get_all_products()
        for product in products:
            self.product_list.insert("", "end", values=(product[0], product[1], product[2], product[3]))

    def load_product_data(self, event):
        selected_item = self.product_list.selection()
        if selected_item:
            product_id, name, price, hs_code = self.product_list.item(selected_item, "values")
            self.product_name_entry.delete(0, tk.END)
            self.product_name_entry.insert(0, name)
            self.product_price_entry.delete(0, tk.END)
            self.product_price_entry.insert(0, price)
            self.hs_code_entry.delete(0, tk.END)
            self.hs_code_entry.insert(0, hs_code)

    def clear_form(self):
        self.product_name_entry.delete(0, tk.END)
        self.product_price_entry.delete(0, tk.END)
        self.hs_code_entry.delete(0, tk.END)
