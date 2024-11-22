# controllers/auth_controller.py

from models.user import User


class AuthController:
    @staticmethod
    def initialize_users():
        """Insert default user credentials if no users exist."""
        if not User.get_user("moonal@invoice"):
            User.add_user("moonal@invoice", "invoice@user")
            print("Default user created.")

    @staticmethod
    def authenticate(username, password):
        """Authenticate user credentials."""
        user = User.get_user(username)
        if user and user[2] == password:  # Assuming user[2] is the password column
            return True
        return False

    @staticmethod
    def is_default_user():
        """
        Check if the current logged-in user is using the default credentials.

        Returns:
            bool: True if the default username and password are being used, False otherwise.
        """
        user = User.get_user("moonal@invoice")
        if user and user[2] == "invoice@user" and user[3] == 0:  # Check if is_updated is 0
            return True
        return False

    @staticmethod
    def change_credentials(current_username, current_password, new_username, new_password):
        """Change user credentials if current credentials are correct."""
        if AuthController.authenticate(current_username, current_password):
            User.update_user(current_username, new_username, new_password)
            print("User credentials updated successfully.")
            return True
        else:
            raise ValueError("Current username or password is incorrect.")
