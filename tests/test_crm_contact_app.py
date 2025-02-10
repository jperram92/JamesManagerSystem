import unittest
import sqlite3
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.crm_contact_app import get_db_connection, is_valid_email, insert_contact

class TestCRMContactApp(unittest.TestCase):
    def setUp(self):
        """Set up test database connection"""
        self.conn = get_db_connection()
        
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'conn'):
            self.conn.close()

    def test_email_validation(self):
        """Test email validation function"""
        # Valid email cases
        self.assertTrue(is_valid_email("test@example.com"))
        self.assertTrue(is_valid_email("user.name+tag@example.co.uk"))
        
        # Invalid email cases
        self.assertFalse(is_valid_email("invalid.email"))
        self.assertFalse(is_valid_email("@example.com"))
        self.assertFalse(is_valid_email("test@.com"))

    def test_contact_insertion(self):
        """Test contact insertion with valid data"""
        result = insert_contact(
            "Mr.", "Male", "John Doe", 
            "john@example.com", "1234567890",
            "Test message", "123 Street", 
            "Sydney", "2000", "New South Wales", 
            "Australia"
        )

if __name__ == '__main__':
    unittest.main()