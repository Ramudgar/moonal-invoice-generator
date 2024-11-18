import tkinter as tk
from tkinter import messagebox  # Import messagebox correctly
from models.client import Client

class ClientView(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Client Type").grid(row=0, column=0)
        self.client_type = tk.Entry(self)
        self.client_type.grid(row=0, column=1)

        tk.Label(self, text="Client Name").grid(row=1, column=0)
        self.client_name = tk.Entry(self)
        self.client_name.grid(row=1, column=1)

        tk.Label(self, text="Contact Number").grid(row=2, column=0)
        self.contact_number = tk.Entry(self)
        self.contact_number.grid(row=2, column=1)

        tk.Label(self, text="Address").grid(row=3, column=0)
        self.address = tk.Entry(self)
        self.address.grid(row=3, column=1)

        self.save_button = tk.Button(self, text="Save Client", command=self.save_client)
        self.save_button.grid(row=4, column=1)

    def save_client(self):
        client_type = self.client_type.get()
        name = self.client_name.get()
        contact_number = self.contact_number.get()
        address = self.address.get()
        Client.add_client(client_type, name, contact_number, address)
        messagebox.showinfo("Success", "Client added successfully!")  # Use messagebox.showinfo
        self.clear_fields()

    def clear_fields(self):
        self.client_type.delete(0, tk.END)
        self.client_name.delete(0, tk.END)
        self.contact_number.delete(0, tk.END)
        self.address.delete(0, tk.END)
