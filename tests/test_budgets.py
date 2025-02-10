import pytest
import sqlite3
from unittest.mock import patch, MagicMock, call
from datetime import date, datetime
import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pages.budgets import (
    get_db_connection,
    get_contacts,
    create_budget,
    get_budgets_for_contact,
    update_budget,
    delete_budget
)

class TestBudgetManagement:
    @pytest.fixture
    def mock_db(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    def test_get_db_connection(self):
        with patch('sqlite3.connect') as mock_connect:
            conn = get_db_connection()
            mock_connect.assert_called_once()
            assert conn is not None

    def test_get_contacts_empty(self, mock_db):
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = []
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            contacts = get_contacts()
            assert len(contacts) == 0

    def test_get_contacts_multiple(self, mock_db):
        mock_conn, mock_cursor = mock_db
        mock_data = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            contacts = get_contacts()
            assert len(contacts) == 2
            assert contacts[0]["email"] == "john@example.com"
            assert contacts[1]["name"] == "Jane Smith"

    def test_create_budget_invalid_dates(self, mock_db):
        mock_conn, mock_cursor = mock_db
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            with patch('streamlit.error') as mock_error:
                # Test end date before start date
                create_budget(
                    contact_id=1,
                    budget_name="Test Budget",
                    total_budget=1000.0,
                    start_date=date(2025, 12, 31),
                    end_date=date(2025, 1, 1),
                    currency="USD"
                )
                mock_error.assert_called_once()

    def test_create_budget_with_validation(self, mock_db):
        mock_conn, mock_cursor = mock_db
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            with patch('streamlit.success'):
                # Test with minimum budget amount
                create_budget(
                    contact_id=1,
                    budget_name="Test Budget",
                    total_budget=0.01,
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 12, 31),
                    currency="USD"
                )
                mock_cursor.execute.assert_called_once()

    def test_update_budget_all_fields(self, mock_db):
        mock_conn, mock_cursor = mock_db
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            with patch('streamlit.success'):
                update_budget(
                    budget_id=1,
                    budget_name="Updated Budget",
                    total_budget=2000.0,
                    start_date=date(2025, 2, 1),
                    end_date=date(2025, 12, 31),
                    currency="EUR"
                )
                assert mock_cursor.execute.call_count == 1

    def test_delete_budget_nonexistent(self, mock_db):
        mock_conn, mock_cursor = mock_db
        mock_cursor.rowcount = 0
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            with patch('streamlit.error') as mock_error:
                delete_budget(999)
                mock_cursor.execute.assert_called_once()

    def test_get_budgets_for_contact_with_filtering(self, mock_db):
        mock_conn, mock_cursor = mock_db
        mock_data = [
            {
                "id": 1,
                "contact_id": 1,
                "budget_name": "Budget 1",
                "total_budget": 1000.0,
                "current_spent": 500.0,
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "currency": "USD",
                "status": "active"
            },
            {
                "id": 2,
                "contact_id": 1,
                "budget_name": "Budget 2",
                "total_budget": 2000.0,
                "current_spent": 0.0,
                "start_date": "2025-02-01",
                "end_date": "2025-12-31",
                "currency": "EUR",
                "status": "pending"
            }
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            budgets = get_budgets_for_contact(1)
            assert len(budgets) == 2
            assert budgets[0]["current_spent"] == 500.0
            assert budgets[1]["currency"] == "EUR"

    @pytest.mark.parametrize("currency", ["USD", "EUR", "GBP", "AUD"])
    def test_create_budget_different_currencies(self, mock_db, currency):
        mock_conn, mock_cursor = mock_db
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            with patch('streamlit.success'):
                create_budget(
                    contact_id=1,
                    budget_name=f"Test Budget {currency}",
                    total_budget=1000.0,
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 12, 31),
                    currency=currency
                )
                mock_cursor.execute.assert_called_once()

    def test_database_connection_error(self):
        with patch('sqlite3.connect', side_effect=sqlite3.Error):
            with pytest.raises(sqlite3.Error):
                get_db_connection()