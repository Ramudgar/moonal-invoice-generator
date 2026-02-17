import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import Settings
from controllers.settings_controller import SettingsController

class SettingsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.C = Settings.COLORS
        self.F = Settings.FONTS
        self.configure(bg=self.C["bg"])
        
        self.settings = SettingsController.get_all_settings()
        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="white", padx=30, pady=20, 
                          highlightbackground=self.C["border"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="System Settings", font=self.F["h2"], 
                 bg="white", fg=self.C["primary"]).pack(side="left")

        # Form Card
        card = tk.Frame(self, bg="white", padx=40, pady=40,
                        highlightbackground=self.C["border"], highlightthickness=1)
        card.place(relx=0.5, rely=0.45, anchor="center", width=600)

        tk.Label(card, text="COMPANY CONFIGURATION", font=self.F["h3"],
                 bg="white", fg=self.C["primary"]).pack(anchor="w", pady=(0, 25))

        self.entries = {}
        fields = [
            ("company_name", "Company Name"),
            ("company_address", "Company Address"),
            ("company_contact", "Contact Number"),
            ("company_pan", "PAN / VAT Number"),
            ("default_vat", "Default VAT Rate (%)"),
        ]

        for key, label in fields:
            tk.Label(card, text=label.upper(), font=self.F["small_bold"],
                     bg="white", fg=self.C["secondary"]).pack(anchor="w")
            
            e = tk.Entry(card, font=self.F["body"], bg=self.C["input_bg"],
                         relief="flat", highlightthickness=2,
                         highlightbackground=self.C["input_border"],
                         highlightcolor=self.C["primary"])
            e.insert(0, self.settings.get(key, ""))
            e.pack(fill="x", pady=(2, 15), ipady=5)
            self.entries[key] = e

        # Save Button
        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Save Changes ✅", style="Gold.TButton",
                    command=self.save_settings).pack(side="right")
        
        ttk.Button(btn_frame, text="Cancel", style="Ghost.TButton",
                    command=self.controller.show_dashboard).pack(side="left")

    def save_settings(self):
        new_settings = {k: e.get().strip() for k, e in self.entries.items()}
        
        if not new_settings["company_name"]:
            return messagebox.showerror("Error", "Company Name is required")
            
        if SettingsController.save_settings(new_settings):
            messagebox.showinfo("Success", "Settings updated successfully!")
            # Update the global settings cache if necessary, though it's mostly fetched on demand
            self.controller.show_dashboard()
        else:
            messagebox.showerror("Error", "Failed to update settings")
