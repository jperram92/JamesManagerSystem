import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to connect to the database
def get_db_connection():
    db_path = os.getenv('DATABASE_PATH', 'crm.db')  # Falls back to 'crm.db' if env var not found
    db_path = os.path.abspath(db_path)  # Convert to absolute path
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Function to get all contacts
def get_contacts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT * FROM contacts
    ''')
    contacts = cursor.fetchall()
    conn.close()
    return contacts

# Function to create a new budget for a contact
def create_budget(contact_id, budget_name, total_budget, start_date, end_date, currency):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO budgets (contact_id, budget_name, total_budget, start_date, end_date, currency)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (contact_id, budget_name, total_budget, start_date, end_date, currency))
    conn.commit()
    conn.close()
    st.success("Budget created successfully!")

# Function to update an existing budget
def update_budget(budget_id, budget_name=None, total_budget=None, start_date=None, end_date=None, currency=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    values = []

    if budget_name:
        updates.append("budget_name = ?")
        values.append(budget_name)
    if total_budget:
        updates.append("total_budget = ?")
        values.append(total_budget)
    if start_date:
        updates.append("start_date = ?")
        values.append(start_date)
    if end_date:
        updates.append("end_date = ?")
        values.append(end_date)
    if currency:
        updates.append("currency = ?")
        values.append(currency)

    updates_str = ", ".join(updates)
    values.append(budget_id)

    cursor.execute(f'''
        UPDATE budgets SET {updates_str} WHERE id = ?
    ''', tuple(values))
    conn.commit()
    conn.close()
    st.success("Budget updated successfully!")

# Function to get all budgets for a contact
def get_budgets_for_contact(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT * FROM budgets WHERE contact_id = ?
    ''', (contact_id,))
    budgets = cursor.fetchall()
    conn.close()
    return budgets

# Function to delete a budget
def delete_budget(budget_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM budgets WHERE id = ?', (budget_id,))
    conn.commit()
    conn.close()
    st.success("Budget deleted successfully!")

# Streamlit UI for budget management
st.title("Budget Management for Contacts")

# Select contact by name
contacts = get_contacts()
contact_names = [f"{contact['name']} ({contact['email']})" for contact in contacts]
contact_selection = st.selectbox("Select a Contact by Name", contact_names)

# Get selected contact_id from selected contact name
contact_id = None
for contact in contacts:
    if f"{contact['name']} ({contact['email']})" == contact_selection:
        contact_id = contact['id']
        break

# Display existing budgets for the selected contact
if contact_id:
    budgets = get_budgets_for_contact(contact_id)
    if budgets:
        st.subheader(f"Existing Budgets for Contact: {contact_selection}")
        
        # Create a dataframe to display budgets
        budgets_df = pd.DataFrame(budgets)
        
        # First, let's check what columns we actually have
        #st.write("Debug: Available columns", budgets_df.columns)
        
        # Update the columns based on what's actually in the database
        column_mapping = {
            0: 'id',
            1: 'contact_id',
            2: 'budget_name',
            3: 'total_budget',
            4: 'current_spent',
            5: 'start_date',
            6: 'end_date',
            7: 'currency',
            8: 'status'
        }
        
        budgets_df.rename(columns=column_mapping, inplace=True)
        
        # Select only the columns we want to display
        display_columns = ['id', 'budget_name', 'total_budget', 'current_spent', 
                         'start_date', 'end_date', 'currency', 'status']
        budgets_df = budgets_df[display_columns]
        
        # Display the dataframe
        st.dataframe(budgets_df)
    else:
        st.write("No budgets found for this contact.")

    # Add buttons below the table
    create_col, update_col, delete_col = st.columns(3)

    # Create New Budget Button
    with create_col:
        with st.expander("Create New Budget"):
            with st.form(key="create_budget_form"):
                budget_name = st.text_input("Budget Name")
                total_budget = st.number_input("Total Budget", min_value=0.0, step=0.01)
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
                currency = st.selectbox("Currency", ["USD", "AUD", "EUR", "GBP"])
                submit_button = st.form_submit_button("Create Budget")
                if submit_button:
                    create_budget(contact_id, budget_name, total_budget, start_date, end_date, currency)

    # Update Budget Button
    with update_col:
        with st.expander("Update Budget"):
            with st.form(key="update_budget_form"):
                budget_names = [budget['budget_name'] for budget in budgets]
                selected_budget = st.selectbox("Select Budget to Update", budget_names)
                
                budget_id_to_update = None
                for budget in budgets:
                    if budget['budget_name'] == selected_budget:
                        budget_id_to_update = budget['id']
                        break

                budget_name_to_update = st.text_input("New Budget Name")
                total_budget_to_update = st.number_input("New Total Budget", min_value=0.0, step=0.01)
                start_date_to_update = st.date_input("New Start Date")
                end_date_to_update = st.date_input("New End Date")
                currency_to_update = st.selectbox("New Currency", ["USD", "AUD", "EUR", "GBP"])
                update_submit = st.form_submit_button("Update Budget")
                if update_submit and budget_id_to_update:
                    update_budget(budget_id_to_update, budget_name_to_update, total_budget_to_update, 
                                start_date_to_update, end_date_to_update, currency_to_update)

    # Delete Budget Button
    with delete_col:
        with st.expander("Delete Budget"):
            with st.form(key="delete_budget_form"):
                budget_names = [budget['budget_name'] for budget in budgets]
                selected_budget = st.selectbox("Select Budget to Delete", budget_names)
                
                budget_id_to_delete = None
                for budget in budgets:
                    if budget['budget_name'] == selected_budget:
                        budget_id_to_delete = budget['id']
                        break

                delete_submit = st.form_submit_button("Confirm Delete")
                if delete_submit and budget_id_to_delete:
                    delete_budget(budget_id_to_delete)