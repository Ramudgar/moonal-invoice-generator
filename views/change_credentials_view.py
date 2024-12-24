import tkinter as tk
from tkinter import messagebox
from controllers.authController import AuthController


class ChangeCredentialsView(tk.Toplevel):
    def __init__(self, master=None, is_default_user=False):
        super().__init__(master)
        self.is_default_user = is_default_user
        self.title("Change Credentials")
        self.geometry("900x600")
        self.configure(bg="#E8B74D")  # Golden hue for the main background

        # Title Label
        tk.Label(
            self,
            text="Change Your Credentials",
            font=("Helvetica", 24, "bold"),
            bg="#E8B74D",  # Matches the main background
            fg="#6B4226"  # Dark brown for readability
        ).pack(pady=30)

        # Form Frame
        form_frame = tk.Frame(self, bg="#FFF8E1", relief="raised", bd=2)  # Light cream frame
        form_frame.place(relx=0.5, rely=0.5, anchor="center", width=700, height=400)

        # Form Fields
        labels = [
            "Current Username:",
            "Current Password:",
            "New Username:",
            "New Password:"
        ]
        entries = []
        for i, label_text in enumerate(labels):
            tk.Label(
                form_frame, 
                text=label_text, 
                font=("Helvetica", 16), 
                bg="#FFF8E1",  # Matches the frame background
                fg="#6B4226"  # Dark brown for labels
            ).grid(row=i, column=0, padx=20, pady=15, sticky="e")
            
            entry = tk.Entry(form_frame, font=("Helvetica", 16), width=35)
            if "Password" in label_text:
                entry.config(show="*")  # Mask password fields
            entry.grid(row=i, column=1, padx=20, pady=15, sticky="w")
            entries.append(entry)

        (
            self.current_username_entry,
            self.current_password_entry,
            self.new_username_entry,
            self.new_password_entry
        ) = entries

        # Submit Button
        tk.Button(
            form_frame,
            text="Change Credentials",
            command=self.change_credentials,
            font=("Helvetica", 16, "bold"),
            bg="#6B4226",  # Dark brown for button background
            fg="white",  # White text for contrast
            width=25,
            relief="groove",
            bd=2
        ).grid(row=len(labels), column=0, columnspan=2, pady=30)

        # Footer Label
        tk.Label(
            self,
            text="Moonal Udhyog PVT. LTD. © 2024 | All Rights Reserved",
            font=("Helvetica", 12),
            bg="#E8B74D",  # Matches the main background
            fg="#4B3E2F"  # Darker brown for footer text
        ).pack(side="bottom", pady=10)

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

            if self.is_default_user:
                self.destroy()
                self.open_dashboard()
            else:
                self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def open_dashboard(self):
        """Open the dashboard view for the updated user."""
        from views.dashboard_view import DashboardView
        dashboard = DashboardView()
        dashboard.mainloop()
