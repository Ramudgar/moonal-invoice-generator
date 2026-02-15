
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock the database connection before importing controller
sys.modules['config.database'] = MagicMock()
from controllers.invoice_controller import InvoiceController

class TestInvoiceNumbering(unittest.TestCase):
    @patch('controllers.invoice_controller.connect_db')
    def test_get_next_invoice_number_first(self, mock_connect):
        # Case: No invoices in the system for this fiscal year
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        next_num = InvoiceController.get_next_invoice_number("81-82")
        self.assertEqual(next_num, "MU/81-82/0001")

    @patch('controllers.invoice_controller.connect_db')
    def test_get_next_invoice_number_increment(self, mock_connect):
        # Case: Existing invoice 0005
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("MU/81-82/0005",)
        
        next_num = InvoiceController.get_next_invoice_number("81-82")
        self.assertEqual(next_num, "MU/81-82/0006")

    @patch('controllers.invoice_controller.connect_db')
    def test_get_next_invoice_number_pads_correctly(self, mock_connect):
        # Case: Existing invoice 0099
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("MU/81-82/0099",)
        
        next_num = InvoiceController.get_next_invoice_number("81-82")
        self.assertEqual(next_num, "MU/81-82/0100")

if __name__ == "__main__":
    unittest.main()
