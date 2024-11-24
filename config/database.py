import os
import sqlite3
import sys

def get_persistent_db_path():
    """Determine the database path based on the running environment."""
    # Check if running as a packaged app (PyInstaller sets `sys._MEIPASS`)
    if hasattr(sys, "_MEIPASS"):
        # Packaged app: Use AppData (Windows) or ~/.moonal_udhyog (Linux/Mac)
        if sys.platform == "win32":
            # For Windows, store in AppData
            base_dir = os.getenv("APPDATA", os.path.expanduser("~"))
            db_dir = os.path.join(base_dir, "MoonalUdhyog")
        else:
            # For Linux/macOS, store in the user's home directory
            base_dir = os.path.expanduser("~")
            db_dir = os.path.join(base_dir, ".moonal_udhyog")
    else:
        # Development mode: Store in the `db` folder outside the `config` folder
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_dir = os.path.join(base_dir, "db")

    # Ensure the directory exists
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # Return the full path to the database file
    return os.path.join(db_dir, "moonal_udhyog.db")

# Get the database path
DB_PATH = get_persistent_db_path()

def connect_db():
    """Connect to the SQLite database, creating it if necessary."""
    try:
        # Connect to the persistent SQLite database
        conn = sqlite3.connect(DB_PATH)
        print(f"Database connection successful! Database path: {DB_PATH}")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def connect_db():
    """Connect to the SQLite database, creating it if necessary."""
    try:
        # Connect to the persistent SQLite database
        conn = sqlite3.connect(DB_PATH)
        print(f"Database connection successful! Database path: {DB_PATH}")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None



def create_tables():

    conn = connect_db()
    if conn is None:
        print("Failed to connect to the database. Exiting.")
        return

    try:
        cursor = conn.cursor()

        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT,
                is_updated INTEGER DEFAULT 0
            )
        ''')

        # Products Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            hs_code TEXT
        )
        ''')

        # Invoices Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Invoices (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                client_contact TEXT,
                address TEXT,
                invoice_number TEXT,
                date TEXT,
                subtotal REAL,
                pan_no TEXT,
                vat_amount REAL,
                total_amount REAL,
                vat_rate REAL DEFAULT 13,
                discount REAL DEFAULT 0,
                paid_amount REAL DEFAULT 0,
                due_amount REAL DEFAULT 0
            )
        ''')

        # Invoice Items Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Invoice_Items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                price_per_unit REAL,
                total_price REAL,
                FOREIGN KEY (invoice_id) REFERENCES Invoices(invoice_id),
                FOREIGN KEY (product_id) REFERENCES Products(product_id)
            )
        ''')
        conn.commit()
        print("Tables created successfully!")

    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        return
    finally:
        conn.close()
