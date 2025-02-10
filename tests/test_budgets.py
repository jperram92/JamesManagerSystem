import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from datetime import date
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

# Fixture for mocking database connection
@pytest.fixture
def mock_db():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

def test_get_contacts(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "John Doe", "email": "john@example.com"}
    ]
    
    with patch('pages.budgets.get_db_connection', return_value=mock_conn):
        contacts = get_contacts()
        assert len(contacts) == 1
        assert contacts[0]["name"] == "John Doe"

def test_create_budget(mock_db):
    mock_conn, mock_cursor = mock_db
    
    with patch('pages.budgets.get_db_connection', return_value=mock_conn):
        with patch('streamlit.success'):
            create_budget(
                contact_id=1,
                budget_name="Test Budget",
                total_budget=1000.0,
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                currency="USD"
            )
            
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()

def test_get_budgets_for_contact(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [
        {
            "id": 1,
            "contact_id": 1,
            "budget_name": "Test Budget",
            "total_budget": 1000.0,
        }
    ]
    
    with patch('pages.budgets.get_db_connection', return_value=mock_conn):
        budgets = get_budgets_for_contact(1)
        assert len(budgets) == 1
        assert budgets[0]["budget_name"] == "Test Budget"

def test_update_budget(mock_db):
    mock_conn, mock_cursor = mock_db
    
    with patch('pages.budgets.get_db_connection', return_value=mock_conn):
        with patch('streamlit.success'):
            update_budget(
                budget_id=1,
                budget_name="Updated Budget",
                total_budget=2000.0
            )
            
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()

def test_delete_budget(mock_db):
    mock_conn, mock_cursor = mock_db
    
    with patch('pages.budgets.get_db_connection', return_value=mock_conn):
        with patch('streamlit.success'):
            delete_budget(1)
            
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()