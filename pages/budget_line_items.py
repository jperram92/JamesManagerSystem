import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect(r'C:\Users\james\OneDrive\Desktop\JamesManagerSystem\crm.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to add a new budget line item
def create_budget_line_item(budget_id, line_item_name, allocated_amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO budget_line_items (budget_id, line_item_name, allocated_amount)
    VALUES (?, ?, ?)
    ''', (budget_id, line_item_name, allocated_amount))
    line_item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return line_item_id

# Function to add a new product
def create_product(line_item_id, product_name, product_group, rate, frequency, service_name, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO products (line_item_id, product_name, product_group, rate, frequency, service_name, description)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (line_item_id, product_name, product_group, rate, frequency, service_name, description))
    conn.commit()
    conn.close()

# Function to get all line items for a budget
def get_budget_line_items(budget_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            bli.id,
            bli.line_item_name,
            bli.allocated_amount,
            COALESCE(SUM(e.amount * e.quantity), 0) as spent_amount,
            bli.status,
            b.currency
        FROM budget_line_items bli
        JOIN budgets b ON b.id = bli.budget_id
        LEFT JOIN expenses e ON bli.id = e.line_item_id
        WHERE bli.budget_id = ?
        GROUP BY bli.id, bli.line_item_name, bli.allocated_amount, bli.status, b.currency
    ''', (budget_id,))
    line_items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return line_items

# Function to get all products for a line item
def get_line_item_products(line_item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            id,
            product_name,
            product_group,
            rate,
            frequency,
            service_name,
            description,
            status
        FROM products 
        WHERE line_item_id = ?
    ''', (line_item_id,))
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

# Function to update a budget line item
def update_budget_line_item(line_item_id, line_item_name=None, allocated_amount=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    values = []

    if line_item_name:
        updates.append("line_item_name = ?")
        values.append(line_item_name)
    if allocated_amount:
        updates.append("allocated_amount = ?")
        values.append(allocated_amount)

    if updates:
        updates_str = ", ".join(updates)
        values.append(line_item_id)
        cursor.execute(f'''
            UPDATE budget_line_items SET {updates_str} WHERE id = ?
        ''', tuple(values))
        conn.commit()
    conn.close()

# Function to update a product
def update_product(product_id, product_name=None, product_group=None, rate=None, 
                  frequency=None, service_name=None, description=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    values = []

    if product_name:
        updates.append("product_name = ?")
        values.append(product_name)
    if product_group:
        updates.append("product_group = ?")
        values.append(product_group)
    if rate:
        updates.append("rate = ?")
        values.append(rate)
    if frequency:
        updates.append("frequency = ?")
        values.append(frequency)
    if service_name:
        updates.append("service_name = ?")
        values.append(service_name)
    if description:
        updates.append("description = ?")
        values.append(description)

    if updates:
        updates_str = ", ".join(updates)
        values.append(product_id)
        cursor.execute(f'''
            UPDATE products SET {updates_str} WHERE id = ?
        ''', tuple(values))
        conn.commit()
    conn.close()

# Function to delete a budget line item (and associated products)
def delete_budget_line_item(line_item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete associated products first
    cursor.execute('DELETE FROM products WHERE line_item_id = ?', (line_item_id,))
    # Then delete the line item
    cursor.execute('DELETE FROM budget_line_items WHERE id = ?', (line_item_id,))
    conn.commit()
    conn.close()

# Function to delete a product
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

# Function to validate budget allocation
def validate_budget_allocation(budget_id, new_allocation, line_item_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get total budget amount
    cursor.execute('SELECT total_budget FROM budgets WHERE id = ?', (budget_id,))
    total_budget = cursor.fetchone()['total_budget']
    
    # Get sum of existing allocations, excluding the current line item if updating
    if line_item_id:
        cursor.execute('''
            SELECT SUM(allocated_amount) as total_allocated 
            FROM budget_line_items 
            WHERE budget_id = ? AND id != ?
        ''', (budget_id, line_item_id))
    else:
        cursor.execute('''
            SELECT SUM(allocated_amount) as total_allocated 
            FROM budget_line_items 
            WHERE budget_id = ?
        ''', (budget_id,))
    
    current_total = cursor.fetchone()['total_allocated'] or 0
    conn.close()
    
    return (current_total + new_allocation) <= total_budget

# Add new function to get budget details
def get_budget_details(budget_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        WITH budget_summary AS (
            SELECT 
                b.id,
                b.budget_name,
                b.total_budget,
                b.currency,
                COALESCE(SUM(bli.allocated_amount), 0) as total_allocated
            FROM budgets b
            LEFT JOIN budget_line_items bli ON b.id = bli.budget_id
            WHERE b.id = ?
            GROUP BY b.id, b.budget_name, b.total_budget, b.currency
        ),
        expense_summary AS (
            SELECT 
                b.id,
                COALESCE(SUM(e.amount * e.quantity), 0) as total_spent
            FROM budgets b
            LEFT JOIN budget_line_items bli ON b.id = bli.budget_id
            LEFT JOIN expenses e ON bli.id = e.line_item_id
            WHERE b.id = ?
            GROUP BY b.id
        )
        SELECT 
            bs.*,
            es.total_spent,
            CASE 
                WHEN bs.total_allocated > bs.total_budget THEN 0
                ELSE bs.total_budget - bs.total_allocated
            END as remaining_budget
        FROM budget_summary bs
        LEFT JOIN expense_summary es ON bs.id = es.id
    ''', (budget_id, budget_id))
    budget = dict(cursor.fetchone())
    conn.close()
    return budget

# Add function to get all budgets for a contact
def get_contact_budgets(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            b.id,
            b.budget_name,
            b.total_budget,
            b.currency,
            b.start_date,
            b.end_date
        FROM budgets b
        WHERE b.contact_id = ?
    ''', (contact_id,))
    budgets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return budgets

def display_budget_line_items(budget_id, budget_name):
    st.subheader(f"Line Items for Budget: {budget_name}")
    
    # Get all line items for this budget
    line_items = get_budget_line_items(budget_id)
    
    if line_items:
        # Create a dataframe for line items
        line_items_df = pd.DataFrame(line_items)
        
        # Format currency values
        currency = line_items_df['currency'].iloc[0] if 'currency' in line_items_df.columns else 'USD'
        
        # Define display columns and their formats
        display_columns = {
            'line_item_name': 'Line Item',
            'allocated_amount': f'Allocated ({currency})',
            'spent_amount': f'Spent ({currency})',
        }
        
        # Create display dataframe
        display_df = pd.DataFrame()
        
        for db_col, display_name in display_columns.items():
            if db_col in line_items_df.columns:
                display_df[display_name] = line_items_df[db_col]
        
        # Calculate remaining amount
        if 'allocated_amount' in line_items_df.columns and 'spent_amount' in line_items_df.columns:
            display_df[f'Remaining ({currency})'] = (
                line_items_df['allocated_amount'] - 
                line_items_df['spent_amount'].fillna(0)
            )
        
        # Add status if available
        if 'status' in line_items_df.columns:
            display_df['Status'] = line_items_df['status']
        
        # Display the dataframe
        st.dataframe(
            display_df,
            column_config={
                f'Allocated ({currency})': st.column_config.NumberColumn(format="%.2f"),
                f'Spent ({currency})': st.column_config.NumberColumn(format="%.2f"),
                f'Remaining ({currency})': st.column_config.NumberColumn(format="%.2f"),
            },
            hide_index=True
        )
    else:
        st.write("No line items found for this budget.")

    # Add Line Item Management Section
    col1, col2, col3 = st.columns(3)

    # Create Line Item Button
    with col1:
        with st.expander("Create Line Item"):
            with st.form(key="create_line_item_form"):
                line_item_name = st.text_input("Line Item Name")
                allocated_amount = st.number_input("Allocated Amount", min_value=0.0, step=0.01)
                create_submit = st.form_submit_button("Create Line Item")
                
                if create_submit:
                    if validate_budget_allocation(budget_id, allocated_amount):
                        create_budget_line_item(budget_id, line_item_name, allocated_amount)
                        st.success("Line item created successfully!")
                        st.rerun()  # Changed from st.experimental_rerun()
                    else:
                        st.error("Allocation exceeds available budget!")

    # Update Line Item Button
    with col2:
        with st.expander("Update Line Item"):
            with st.form(key="update_line_item_form"):
                if line_items:
                    line_item_names = [item['line_item_name'] for item in line_items]
                    selected_line_item = st.selectbox("Select Line Item", line_item_names)
                    
                    line_item_id = None
                    for item in line_items:
                        if item['line_item_name'] == selected_line_item:
                            line_item_id = item['id']
                            break
                    
                    new_name = st.text_input("New Name")
                    new_amount = st.number_input("New Amount", min_value=0.0, step=0.01)
                    update_submit = st.form_submit_button("Update Line Item")
                    
                    if update_submit and line_item_id:
                        if validate_budget_allocation(budget_id, new_amount, line_item_id):
                            update_budget_line_item(line_item_id, new_name, new_amount)
                            st.success("Line item updated successfully!")
                            st.rerun()
                        else:
                            st.error("New allocation would exceed available budget!")

    # Product Management Section
    st.subheader("Product Management")
    
    # Select Line Item for Product Management
    if line_items:
        selected_line_item_for_products = st.selectbox(
            "Select Line Item for Product Management",
            [item['line_item_name'] for item in line_items]
        )
        
        line_item_id = None
        for item in line_items:
            if item['line_item_name'] == selected_line_item_for_products:
                line_item_id = item['id']
                break
        
        if line_item_id:
            # Display Products
            products = get_line_item_products(line_item_id)
            if products:
                products_df = pd.DataFrame(products)
                
                # Define display columns for products
                product_columns = {
                    'product_name': 'Product Name',
                    'product_group': 'Group',
                    'rate': 'Rate',
                    'frequency': 'Frequency',
                    'service_name': 'Service'
                }
                
                # Create display dataframe for products
                display_products_df = pd.DataFrame()
                
                for db_col, display_name in product_columns.items():
                    if db_col in products_df.columns:
                        display_products_df[display_name] = products_df[db_col]
                
                # Display the products dataframe
                st.dataframe(
                    display_products_df,
                    column_config={
                        'Rate': st.column_config.NumberColumn(format="%.2f"),
                    },
                    hide_index=True
                )
            else:
                st.write("No products found for this line item.")
            
            # Product Management Buttons
            prod_col1, prod_col2, prod_col3 = st.columns(3)
            
            # Create Product
            with prod_col1:
                with st.expander("Add Product"):
                    with st.form(key="create_product_form"):
                        product_name = st.text_input("Product Name")
                        product_group = st.text_input("Product Group")
                        rate = st.number_input("Rate", min_value=0.0, step=0.01)
                        frequency = st.selectbox("Frequency", ["hourly", "daily", "weekly", "monthly", "yearly"])
                        service_name = st.text_input("Service Name")
                        description = st.text_area("Description")
                        
                        create_product_submit = st.form_submit_button("Add Product")
                        if create_product_submit:
                            create_product(line_item_id, product_name, product_group, rate, 
                                        frequency, service_name, description)
                            st.success("Product added successfully!")
                            st.rerun()  # Changed from st.experimental_rerun()
            
            # Update Product
            with prod_col2:
                with st.expander("Update Product"):
                    if products:
                        with st.form(key="update_product_form"):
                            product_names = [prod['product_name'] for prod in products]
                            selected_product = st.selectbox("Select Product", product_names)
                            
                            product_id = None
                            for prod in products:
                                if prod['product_name'] == selected_product:
                                    product_id = prod['id']
                                    break
                            
                            new_product_name = st.text_input("New Product Name")
                            new_product_group = st.text_input("New Product Group")
                            new_rate = st.number_input("New Rate", min_value=0.0, step=0.01)
                            new_frequency = st.selectbox("New Frequency", 
                                                       ["hourly", "daily", "weekly", "monthly", "yearly"])
                            new_service_name = st.text_input("New Service Name")
                            new_description = st.text_area("New Description")
                            
                            update_product_submit = st.form_submit_button("Update Product")
                            if update_product_submit and product_id:
                                update_product(product_id, new_product_name, new_product_group,
                                            new_rate, new_frequency, new_service_name, new_description)
                                st.success("Product updated successfully!")
                                st.rerun()  # Changed from st.experimental_rerun()

            # Add Expenses Section
            st.subheader(f"Expenses for {selected_line_item_for_products}")
            expenses = get_line_item_expenses(line_item_id)
            if expenses:
                expenses_df = pd.DataFrame(expenses)
                st.dataframe(
                    expenses_df[[
                        'date_incurred', 'product_name', 'service_name',
                        'amount', 'quantity', 'total_amount', 'description'
                    ]],
                    column_config={
                        'date_incurred': 'Date',
                        'product_name': 'Product',
                        'service_name': 'Service',
                        'amount': st.column_config.NumberColumn('Rate', format="%.2f"),
                        'quantity': st.column_config.NumberColumn('Quantity', format="%.2f"),
                        'total_amount': st.column_config.NumberColumn('Total', format="%.2f"),
                        'description': 'Description'
                    },
                    hide_index=True
                )
                
                # Show totals
                totals = calculate_line_item_totals(line_item_id)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Allocated Budget", f"{currency} {totals['allocated_amount']:,.2f}")
                with col2:
                    st.metric("Total Spent", f"{currency} {totals['total_spent']:,.2f}")
                with col3:
                    st.metric("Remaining", f"{currency} {totals['remaining']:,.2f}")

            # Add Expense Button
            with st.expander("Add New Expense"):
                with st.form(key="add_expense_form"):
                    line_item_products = get_line_item_products(line_item_id)
                    if line_item_products:
                        product_options = [p['product_name'] for p in line_item_products]
                        selected_product = st.selectbox("Select Product", product_options)
                        
                        # Get product_id and rate from selection
                        product_id = None
                        default_rate = 0.0
                        for prod in line_item_products:
                            if prod['product_name'] == selected_product:
                                product_id = prod['id']
                                default_rate = float(prod['rate'])  # Convert to float
                                break
                        
                        # Expense details - ensure all numeric values are float
                        expense_amount = st.number_input(
                            "Amount", 
                            min_value=0.0,  # Float
                            value=default_rate,  # Already float
                            step=0.01,  # Float
                            format="%.2f"  # Format as float
                        )
                        
                        expense_quantity = st.number_input(
                            "Quantity", 
                            min_value=0.1,  # Float
                            value=1.0,  # Float
                            step=0.1,  # Float
                            format="%.1f"  # Format as float
                        )
                        
                        expense_date = st.date_input("Date Incurred")
                        expense_description = st.text_area("Description")
                        
                        # Show total calculation
                        total_expense = float(expense_amount) * float(expense_quantity)
                        st.write(f"Total Expense: {currency} {total_expense:,.2f}")
                        
                        # Submit button
                        submit_expense = st.form_submit_button("Add Expense")
                        
                        if submit_expense and product_id:
                            totals = calculate_line_item_totals(line_item_id)
                            if float(totals['total_spent'] + total_expense) <= float(totals['allocated_amount']):
                                add_expense(
                                    line_item_id=line_item_id,
                                    product_id=product_id,
                                    amount=float(expense_amount),
                                    quantity=float(expense_quantity),
                                    date_incurred=expense_date,
                                    description=expense_description
                                )
                                st.success("Expense added successfully!")
                                st.rerun()
                            else:
                                st.error("This expense would exceed the allocated budget!")
                    else:
                        st.warning("Please add products to this line item before adding expenses.")

# Add after the existing functions

def add_expense(line_item_id, product_id, amount, quantity, date_incurred, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate total expense amount
    total_amount = amount * quantity
    
    # Add the expense
    cursor.execute('''
    INSERT INTO expenses (line_item_id, product_id, amount, quantity, date_incurred, description)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (line_item_id, product_id, amount, quantity, date_incurred, description))
    
    # Update the spent_amount in budget_line_items
    cursor.execute('''
    UPDATE budget_line_items 
    SET spent_amount = COALESCE(spent_amount, 0) + ?
    WHERE id = ?
    ''', (total_amount, line_item_id))
    
    conn.commit()
    conn.close()

def get_line_item_expenses(line_item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            e.id,
            e.amount,
            e.quantity,
            e.amount * e.quantity as total_amount,
            e.date_incurred,
            e.description,
            p.product_name,
            p.frequency,
            p.service_name
        FROM expenses e
        JOIN products p ON e.product_id = p.id
        WHERE e.line_item_id = ?
        ORDER BY e.date_incurred DESC
    ''', (line_item_id,))
    expenses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return expenses

def calculate_line_item_totals(line_item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        WITH expense_totals AS (
            SELECT 
                line_item_id,
                SUM(amount * quantity) as total_spent
            FROM expenses
            WHERE line_item_id = ?
            GROUP BY line_item_id
        )
        SELECT 
            bli.allocated_amount,
            COALESCE(et.total_spent, 0) as total_spent,
            bli.allocated_amount - COALESCE(et.total_spent, 0) as remaining
        FROM budget_line_items bli
        LEFT JOIN expense_totals et ON bli.id = et.line_item_id
        WHERE bli.id = ?
    ''', (line_item_id, line_item_id))
    
    result = cursor.fetchone()
    totals = {
        'allocated_amount': float(result['allocated_amount']),
        'total_spent': float(result['total_spent']),
        'remaining': float(result['allocated_amount'] - result['total_spent'])
    }
    conn.close()
    return totals

# Update the manage_budget_line_items function
def manage_budget_line_items():
    st.title("Budget Line Items Management")

    # Get contacts for selection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email FROM contacts')
    contacts = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Contact selection
    contact_options = [f"{c['name']} ({c['email']})" for c in contacts]
    selected_contact = st.selectbox("Select Contact", contact_options)
    
    # Get contact_id from selection
    contact_id = None
    for contact in contacts:
        if f"{contact['name']} ({contact['email']})" == selected_contact:
            contact_id = contact['id']
            break

    if contact_id:
        # Get budgets for selected contact
        budgets = get_contact_budgets(contact_id)
        
        if budgets:
            # Create budget selection
            budget_options = [f"{b['budget_name']} ({b['currency']} {b['total_budget']:,.2f})" for b in budgets]
            selected_budget = st.selectbox("Select Budget", budget_options)
            
            # Get budget_id from selection
            budget_id = None
            for budget in budgets:
                if f"{budget['budget_name']} ({budget['currency']} {budget['total_budget']:,.2f})" == selected_budget:
                    budget_id = budget['id']
                    break

            # Update the metrics display section in manage_budget_line_items
            if budget_id:
                # Display budget summary
                budget_details = get_budget_details(budget_id)
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Budget", 
                        f"{budget_details['currency']} {budget_details['total_budget']:,.2f}"
                    )
                
                with col2:
                    st.metric(
                        "Total Allocated", 
                        f"{budget_details['currency']} {budget_details['total_allocated']:,.2f}"
                    )
                
                with col3:
                    st.metric(
                        "Total Spent", 
                        f"{budget_details['currency']} {budget_details['total_spent']:,.2f}"
                    )
                
                with col4:
                    st.metric(
                        "Available to Allocate", 
                        f"{budget_details['currency']} {budget_details['remaining_budget']:,.2f}"
                    )

                # Display line items and products
                display_budget_line_items(budget_id, budget_details['budget_name'])
        else:
            st.warning("No budgets found for selected contact.")
    else:
        st.info("Please select a contact to view their budgets.")

# Update the main section
if __name__ == "__main__":
    st.set_page_config(page_title="Budget Line Items Management", layout="wide")
    manage_budget_line_items()