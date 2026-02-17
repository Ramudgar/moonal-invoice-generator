import os
import sqlite3
import sys
import platform

def get_persistent_db_path():
    """Determine the database path based on the running environment."""
    # Check if running as a packaged app (PyInstaller sets `sys._MEIPASS`)
    """
    Returns a secure, OS-specific path for the database.
    Linux: ~/.local/share/MoonalInvoiceApp/
    Windows: %LOCALAPPDATA%/MoonalInvoiceApp/
    """
    home = os.path.expanduser("~")
    
    if platform.system() == "Windows":
        base_dir = os.path.join(os.environ.get("LOCALAPPDATA", home), "MoonalInvoiceApp")
    else:
        # Linux/Mac default XDG location
        base_dir = os.path.join(home, ".local", "share", "MoonalInvoiceApp")
    
    # Create directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir, mode=0o700)  # Secure permissions
        
    db_path = os.path.join(base_dir, "moonal_invoice.db")
    
    # LEGACY MIGRATION: Check if old DB exists in project root and new DB doesn't
    # If so, move it to secure location to preserve data.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    old_db_path = os.path.join(project_root, "moonal_invoice.db")
    
    if os.path.exists(old_db_path) and not os.path.exists(db_path):
        import shutil
        try:
            print(f"Migrating database from {old_db_path} to {db_path}...")
            shutil.copy2(old_db_path, db_path)
            print("Migration successful.")
            # Optional: Rename old DB to .bak to avoid confusion
            os.rename(old_db_path, old_db_path + ".bak")
        except Exception as e:
            print(f"Error migrating database: {e}")
            
    return db_path

DB_NAME = get_persistent_db_path()

def connect_db():
    """Connect to the SQLite database, creating it if necessary."""
    try:
        conn = sqlite3.connect(DB_NAME, timeout=30)
        conn.row_factory = sqlite3.Row
        # Enable Write-Ahead Logging for concurrency and safety
        conn.execute("PRAGMA journal_mode=WAL;")
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

        # Users Table (RBAC)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT CHECK(role IN ('admin','user')) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Products Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT,
            viscosity TEXT,
            category TEXT DEFAULT 'Lubricant',
            unit TEXT DEFAULT 'Ltr',
            price REAL NOT NULL DEFAULT 0,
            purchase_price REAL DEFAULT 0,
            stock_quantity INTEGER DEFAULT 0,
            min_stock_alert INTEGER DEFAULT 10,
            hs_code TEXT,
            description TEXT DEFAULT '',
            batch_number TEXT
        )
        ''')



        # Audit Log Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            performed_by TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Invoices Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Invoices (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE,
                client_name TEXT,
                client_contact TEXT,
                address TEXT,
                pan_no TEXT,
                date TEXT,
                subtotal REAL DEFAULT 0,
                vat_amount REAL DEFAULT 0,
                total_amount REAL DEFAULT 0,
                vat_rate REAL DEFAULT 13,
                discount REAL DEFAULT 0,
                paid_amount REAL DEFAULT 0,
                due_amount REAL DEFAULT 0,
                status TEXT DEFAULT 'ACTIVE',
                cancel_reason TEXT DEFAULT '',
                cancelled_date TEXT DEFAULT '',
                is_credit_note INTEGER DEFAULT 0,
                credit_note_number TEXT,
                cancellation_comment TEXT DEFAULT ''
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
        # Customers Table (CRM)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                pan_vat TEXT UNIQUE,
                address TEXT,
                contact_person TEXT,
                mobile TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Global Settings Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        print("Tables created successfully!")

        # Migrate existing tables to add new columns if missing
        _migrate_products_table(conn)
        _migrate_invoices_table(conn)

    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        return
    finally:
        if conn:
            _seed_default_settings(conn)
            conn.close()


def _seed_default_settings(conn):
    """Seed the settings table with default company info if empty."""
    cursor = conn.cursor()
    defaults = [
        ('company_name', 'MOONAL UDHYOG PVT. LTD.'),
        ('company_address', 'Golbazar-4, Siraha, Nepal'),
        ('company_contact', '9844000000'),
        ('company_pan', '123456789'),
        ('default_vat', '13'),
        ('currency_symbol', 'Rs.')
    ]
    for key, value in defaults:
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()


def _migrate_products_table(conn):
    """Add new columns to existing Products table if they don't exist."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Products)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    migrations = [
        ("description", "TEXT DEFAULT ''"),
        ("unit", "TEXT DEFAULT 'Ltr'"),
        ("category", "TEXT DEFAULT 'Lubricant'"),
        ("brand", "TEXT DEFAULT ''"),
        ("viscosity", "TEXT DEFAULT ''"),
        ("purchase_price", "REAL DEFAULT 0"),
        ("stock_quantity", "INTEGER DEFAULT 0"),
        ("min_stock_alert", "INTEGER DEFAULT 10"),
        ("batch_number", "TEXT DEFAULT ''")
    ]
    for col_name, col_type in migrations:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE Products ADD COLUMN {col_name} {col_type}")
            print(f"Migrated Products table: added '{col_name}' column.")
    conn.commit()


def _migrate_invoices_table(conn):
    """Add status/cancellation columns to existing Invoices table if missing."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Invoices)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    migrations = [
        ("status", "TEXT DEFAULT 'ACTIVE'"),
        ("cancel_reason", "TEXT DEFAULT ''"),
        ("cancelled_date", "TEXT DEFAULT ''"),
        ("is_credit_note", "INTEGER DEFAULT 0"),
        ("credit_note_number", "TEXT"),
        ("cancellation_comment", "TEXT DEFAULT ''"),
        ("subtotal", "REAL DEFAULT 0"),
        ("vat_amount", "REAL DEFAULT 0"),
        ("vat_rate", "REAL DEFAULT 13"),
        ("discount", "REAL DEFAULT 0"),
        ("paid_amount", "REAL DEFAULT 0"),
        ("due_amount", "REAL DEFAULT 0")
    ]
    for col_name, col_type in migrations:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE Invoices ADD COLUMN {col_name} {col_type}")
            print(f"Migrated Invoices table: added '{col_name}' column.")
    conn.commit()
