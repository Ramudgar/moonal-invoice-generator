import tkinter as tk
from tkinter import messagebox  # Import messagebox correctly
from models.client import Client

class ClientView(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

        self.COLORS = {
            "primary": "#D4AF37",
            "accent": "#E91E63",
            "bg": "white",
            "text": "#3E2723",
            "secondary": "#757575"
        }
        self.config(bg="white", padx=20, pady=20)

    def create_widgets(self):
        def create_entry(label, row):
            tk.Label(self, text=label, font=("Segoe UI", 9, "bold"), bg="white", fg=self.COLORS["secondary"]).grid(row=row*2, column=0, sticky="w", pady=(10, 0))
            e = tk.Entry(self, font=("Segoe UI", 10), bg="#F8F9FA", relief="flat", highlightthickness=1, highlightbackground="#D1D1D1")
            e.grid(row=row*2+1, column=0, sticky="ew", pady=(2, 5), ipady=3)
            return e

        self.client_type = create_entry("CLIENT TYPE", 0)
        self.client_name = create_entry("CLIENT NAME", 1)
        self.contact_number = create_entry("CONTACT NUMBER", 2)
        self.address = create_entry("ADDRESS", 3)

        self.save_button = tk.Button(
            self, 
            text="SAVE CLIENT", 
            command=self.save_client,
            font=("Segoe UI", 10, "bold"),
            bg=self.COLORS["primary"],
            fg="white",
            relief="flat",
            cursor="hand2",
            activebackground=self.COLORS["accent"],
            activeforeground="white"
        )
        self.save_button.grid(row=8, column=0, pady=20, sticky="ew")
        self.columnconfigure(0, weight=1)

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
