
import sqlite3


def connect_db():
    conn = sqlite3.connect('./db/moonal_udhyog.db')
    return conn


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

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
    conn.close()

