from config.database import connect_db

class Client:
    @staticmethod
    def add_client(name, contact_number, address):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Clients (name, contact_number, address)
            VALUES (?, ?, ?)
        ''', (name, contact_number, address))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_clients():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Clients")
        clients = cursor.fetchall()
        conn.close()
        return clients
