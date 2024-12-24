import tkinter as tk
from tkinter import ttk, messagebox
from controllers.product_controller import ProductController


class ProductView(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Product Management Dashboard")
        
        # Manually maximize the window (cross-platform compatible)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")  # Set to full screen dimensions
        
        self.configure(bg="#F1C27D")  # Soft and appealing background

        # Title Label with improved appearance
        title_label = tk.Label(
            self,
           text="Product Management",
            font=("Arial", 18, "bold"),
            bg="#FFDAB9",
            fg="#333333",
            padx=20,
            pady=15,
            relief="ridge"
        )
        title_label.pack(fill="x", pady=(10, 20))
        
        # Form Frame
        form_frame = tk.Frame(self, bg="#FFF8E1", relief="solid", bd=1)
        form_frame.pack(padx=30, pady=20, fill="x", expand=True)

        tk.Label(form_frame, text="Product Name:", bg="#FFF8E1", font=("Helvetica", 12)).grid(
            row=0, column=0, padx=15, pady=10, sticky="w"
        )
        self.product_name_entry = tk.Entry(form_frame, font=("Helvetica", 12), width=30)
        self.product_name_entry.grid(row=0, column=1, pady=10)

        tk.Label(form_frame, text="Product Price:", bg="#FFF8E1", font=("Helvetica", 12)).grid(
            row=1, column=0, padx=15, pady=10, sticky="w"
        )
        self.product_price_entry = tk.Entry(form_frame, font=("Helvetica", 12), width=30)
        self.product_price_entry.grid(row=1, column=1, pady=10)

        tk.Label(form_frame, text="HS Code:", bg="#FFF8E1", font=("Helvetica", 12)).grid(
            row=2, column=0, padx=15, pady=10, sticky="w"
        )
        self.hs_code_entry = tk.Entry(form_frame, font=("Helvetica", 12), width=30)
        self.hs_code_entry.grid(row=2, column=1, pady=10)

        # Button Frame with no large gap
        button_frame = tk.Frame(self, bg="#FFF8E1")
        button_frame.pack(pady=15)

        style = ttk.Style()
        style.configure(
            "Product.TButton",
            font=("Helvetica", 12, "bold"),
            padding=10,
            width=18,
            foreground="#FFFFFF",
            background="#6B4226",  # Vibrant brown for buttons
            relief="solid",
        )
        style.map("Product.TButton", background=[("active", "#FF6F00")])  # Darker orange on hover

        ttk.Button(
            button_frame, text="Add Product", style="Product.TButton", command=self.add_product
        ).grid(row=0, column=0, padx=15)

        ttk.Button(
            button_frame, text="Update Product", style="Product.TButton", command=self.update_product
        ).grid(row=0, column=1, padx=15)

        ttk.Button(
            button_frame, text="Delete Product", style="Product.TButton", command=self.delete_product
        ).grid(row=0, column=2, padx=15)

        # Product List with visual improvement
        self.product_list = ttk.Treeview(
            self,
            columns=("ID", "Name", "Price", "HS Code"),
            show="headings",
            height=10,
        )
        self.product_list.heading("ID", text="ID")
        self.product_list.heading("Name", text="Name")
        self.product_list.heading("Price", text="Price")
        self.product_list.heading("HS Code", text="HS Code")
        self.product_list.column("ID", width=50, anchor="center")
        self.product_list.column("Name", width=200, anchor="w")
        self.product_list.column("Price", width=100, anchor="center")
        self.product_list.column("HS Code", width=150, anchor="center")
        self.product_list.pack(pady=20, padx=30, fill="both", expand=True)

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
