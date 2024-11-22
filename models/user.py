# models/user.py

from config.database import connect_db

class User:
    @staticmethod
    def add_user(username, password):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user(username):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def update_user(username, new_username, new_password):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Users SET username = ?, password = ? WHERE username = ?",
            (new_username, new_password, username)
        )
        conn.commit()
        conn.close()
