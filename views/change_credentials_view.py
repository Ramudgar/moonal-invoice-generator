import tkinter as tk
from tkinter import messagebox
from controllers.authController import AuthController


class ChangeCredentialsView(tk.Toplevel):
    def __init__(self, master=None, is_default_user=False):
        super().__init__(master)
        self.is_default_user = is_default_user  # Flag to indicate if the current user is the default user
        self.title("Change Credentials")
        self.geometry("900x600")  # Increased window size for larger form
        self.configure(bg="#003366")  # Dark blue background for consistency

        # Title Label
        title_label = tk.Label(
            self,
            text="Change Your Credentials",
            font=("Helvetica", 24, "bold"),
            bg="#003366",
            fg="#f0f8ff"  # Contrasting white color for text
        )
        title_label.pack(pady=30)

        # Form Frame (Larger Size)
        form_frame = tk.Frame(self, bg="#f0f8ff", relief="raised", bd=2)
        form_frame.place(relx=0.5, rely=0.5, anchor="center", width=700, height=400)

        # Define a grid layout for the form
        form_frame.columnconfigure(0, weight=1)  # Label column
        form_frame.columnconfigure(1, weight=3)  # Entry column

        # Current Username
        tk.Label(
            form_frame, text="Current Username:", font=("Helvetica", 16), bg="#f0f8ff", fg="#003366"
        ).grid(row=0, column=0, padx=20, pady=15, sticky="e")
        self.current_username_entry = tk.Entry(form_frame, font=("Helvetica", 16), width=35)
        self.current_username_entry.grid(row=0, column=1, padx=20, pady=15, sticky="w")

        # Current Password
        tk.Label(
            form_frame, text="Current Password:", font=("Helvetica", 16), bg="#f0f8ff", fg="#003366"
        ).grid(row=1, column=0, padx=20, pady=15, sticky="e")
        self.current_password_entry = tk.Entry(form_frame, font=("Helvetica", 16), show="*", width=35)
        self.current_password_entry.grid(row=1, column=1, padx=20, pady=15, sticky="w")

        # New Username
        tk.Label(
            form_frame, text="New Username:", font=("Helvetica", 16), bg="#f0f8ff", fg="#003366"
        ).grid(row=2, column=0, padx=20, pady=15, sticky="e")
        self.new_username_entry = tk.Entry(form_frame, font=("Helvetica", 16), width=35)
        self.new_username_entry.grid(row=2, column=1, padx=20, pady=15, sticky="w")

        # New Password
        tk.Label(
            form_frame, text="New Password:", font=("Helvetica", 16), bg="#f0f8ff", fg="#003366"
        ).grid(row=3, column=0, padx=20, pady=15, sticky="e")
        self.new_password_entry = tk.Entry(form_frame, font=("Helvetica", 16), show="*", width=35)
        self.new_password_entry.grid(row=3, column=1, padx=20, pady=15, sticky="w")

        # Submit Button
        submit_button = tk.Button(
            form_frame,
            text="Change Credentials",
            command=self.change_credentials,
            font=("Helvetica", 16, "bold"),
            bg="#4CAF50",  # Green button
            fg="white",
            width=25,
            relief="groove",
            bd=2
        )
        submit_button.grid(row=4, column=0, columnspan=2, pady=30)

        # Footer Label
        footer_label = tk.Label(
            self,
            text="Moonal Udhyog PVT. LTD. © 2024 | All Rights Reserved",
            font=("Helvetica", 12),
            bg="#003366",
            fg="#f0f8ff"
        )
        footer_label.pack(side="bottom", pady=10)

    def change_credentials(self):
        """Handle changing user credentials."""
        current_username = self.current_username_entry.get()
        current_password = self.current_password_entry.get()
        new_username = self.new_username_entry.get()
        new_password = self.new_password_entry.get()

        try:
            # Attempt to change credentials
            AuthController.change_credentials(
                current_username, current_password, new_username, new_password
            )
            messagebox.showinfo(
                "Success", "Credentials updated successfully.", parent=self
            )

            # Handle default user flow
            if self.is_default_user:
                self.destroy()  # Close the ChangeCredentialsView
                self.open_dashboard()  # Open the dashboard for the updated user
            else:
                # Simply destroy the ChangeCredentialsView for non-default users
                self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def open_dashboard(self):
        """Open the dashboard view for the updated user."""
        from views.dashboard_view import DashboardView
        dashboard = DashboardView()
        dashboard.mainloop()
