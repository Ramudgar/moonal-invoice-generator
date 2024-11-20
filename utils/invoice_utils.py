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
        """Retrieve the last invoice number from a file."""
        if not os.path.exists(invoice_file):
            return 0  # Start fresh if the file doesn't exist

        with open(invoice_file, "r") as file:
            data = file.read().strip()
            try:
                file_fiscal_year, invoice_number = data.split('-')
                # If the fiscal year matches, continue with the previous sequence
                if file_fiscal_year == current_fiscal_year:
                    return int(invoice_number)
            except ValueError:
                pass

        return 0  # Reset the sequence if the fiscal year has changed

    @staticmethod
    def generate_invoice_number(current_fiscal_year, invoice_file):
        """Generate a new invoice number."""
        # Retrieve the last invoice number
        last_invoice = InvoiceUtils.get_last_invoice(current_fiscal_year, invoice_file)

        # Increment the last invoice number
        last_invoice += 1

        # Save the last invoice number back to the file
        with open(invoice_file, "w") as file:
            file.write(f"{current_fiscal_year}-{last_invoice:03}")

        return f"# {last_invoice:03}"