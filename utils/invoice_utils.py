import os
from datetime import datetime


class InvoiceUtils:
    @staticmethod
    def is_leap_year(year):
        """Check if a given year is a leap year."""
        return (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))

    @staticmethod
    def get_fiscal_year_nepali():
        """Calculate the current Nepali fiscal year."""
        today = datetime.now()
        year = today.year
        month = today.month
        day = today.day

        # Determine if the current year is a leap year
        leap_year = InvoiceUtils.is_leap_year(year)

        # Shrawan start day varies between leap and non-leap years
        shrawan_start_day = 16 if leap_year else 17

        # Approximate fiscal year based on Nepali calendar
        if month < 7 or (month == 7 and day < shrawan_start_day):
            nepali_year = year + 57  # Convert to Nepali year
            fiscal_year = f"{nepali_year - 1}/{nepali_year}"
        else:
            nepali_year = year + 57
            fiscal_year = f"{nepali_year}/{nepali_year + 1}"

        return fiscal_year

    @staticmethod
    def get_last_invoice(current_fiscal_year, invoice_file):
        """Retrieve the last invoice number from a file (Deprecated)."""
        if not os.path.exists(invoice_file):
            return 0

        with open(invoice_file, "r") as file:
            data = file.read().strip()
            try:
                file_fiscal_year, invoice_number = data.split('-')
                if file_fiscal_year == current_fiscal_year:
                    return int(invoice_number)
            except ValueError:
                pass

        return 0

    @staticmethod
    def generate_invoice_number(current_fiscal_year):
        """Generate a new invoice number using the database."""
        from controllers.invoice_controller import InvoiceController
        return InvoiceController.get_next_invoice_number(current_fiscal_year)