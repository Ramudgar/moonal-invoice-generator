# main.py
from config.database import create_tables
from controllers.authController import AuthController
from views.login_view import LoginView

def main():
    # Initialize all database tables
    # Initialize the database
    create_tables()

    # Insert default user credentials
    AuthController.initialize_users()

    # Launch the Login View
    app = LoginView()
    app.mainloop()

if __name__ == "__main__":
    main()
