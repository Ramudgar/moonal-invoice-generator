import tkinter as tk
from config.database import create_tables
from views.dashboard_view import DashboardView

def main():
    # Initialize database tables
    create_tables()

    # Setup main Tkinter window
    root = DashboardView()
    root.title("Moonal Udhyog PVT. LTD. - Invoice Generator")
    root.geometry("800x600")
    root.mainloop()

if __name__ == "__main__":
    main()
