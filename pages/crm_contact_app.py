import streamlit as st
import sqlite3
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# Function to validate email using regex
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(r'C:\Users\james\OneDrive\Desktop\JamesManagerSystem\crm.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to insert a new contact
def insert_contact(title, gender, name, email, phone, message, address_line, suburb, postcode, state, country):
    if not is_valid_email(email):
        st.error("Invalid email address!")
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
    INSERT INTO contacts (title, gender, name, email, phone, message, address_line, suburb, postcode, state, country)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, gender, name, email, phone, message, address_line, suburb, postcode, state, country))  # 11 values
    conn.commit()
    conn.close()
    return True

# Function to update an existing contact by ID
def update_contact(contact_id, title, gender, name, email, phone, message, address_line, suburb, postcode, state, country):
    if not is_valid_email(email):
        st.error("Invalid email address!")
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
    UPDATE contacts
    SET title = ?, gender = ?, name = ?, email = ?, phone = ?, message = ?, address_line = ?, suburb = ?, postcode = ?, state = ?, country = ?
    WHERE id = ?
    ''', (title, gender, name, email, phone, message, address_line, suburb, postcode, state, country, contact_id))
    conn.commit()
    conn.close()
    return True

# Function to send email using SMTP
def send_email(to_email, subject, body):
    from_email = "8542f6001@smtp-brevo.com"  # Replace with your email
    password = ""
    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject
    # Attach the body with the msg instance
    message.attach(MIMEText(body, 'plain'))
    # Establish a secure session with Gmail's SMTP server
    try:
        server = smtplib.SMTP('smtp-relay.brevo.com', 587)  # For Gmail
        server.starttls()  # Secure connection
        server.login(from_email, password)  # Log in to your email
        text = message.as_string()  # Convert the message to string
        server.sendmail(from_email, to_email, text)  # Send the email
        server.quit()  # Close the connection
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
# Streamlit interface
st.title('Contact Management Tool')

# Create the right-hand email module in a sidebar
with st.sidebar:
    st.header("Email Client")
    
    # Email form fields
    to_email = st.text_input("To (Email Address)")
    subject = st.text_input("Subject")
    body = st.text_area("Body")
    send_button = st.button("Send Email")
    # Handle the Send button click
    if send_button and to_email and subject and body:
        if send_email(to_email, subject, body):
            st.success("Email sent successfully!")
        else:
            st.error("Failed to send email. Please check your credentials.")

# Function to delete a contact by ID
def delete_contact(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
    conn.commit()
    conn.close()

# Function to search for contacts by name
def search_contact_by_name(search_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE name LIKE ?', ('%' + search_name + '%',))
    contacts = cursor.fetchall()
    conn.close()
    return contacts

# Function to display contacts
def display_contacts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts')
    contacts = cursor.fetchall()
    conn.close()
    return contacts

# Get the contacts and convert them to a dataframe for display
contacts = display_contacts()
if contacts:
    # Convert the list of contacts into a DataFrame
    contacts_df = pd.DataFrame(contacts, columns=['id', 'title', 'gender', 'name', 'email', 'phone', 'message', 'address_line', 'suburb', 'postcode', 'state', 'country'])
    # Display the DataFrame as a table
    st.subheader('Existing Contacts')
    st.dataframe(contacts_df)  # This will display the contacts in a table format with custom size
else:
    st.write("No contacts available.")

# Mapping of full state names to abbreviations (and vice versa)
state_mapping = {
    "New South Wales": "NSW",
    "Victoria": "VIC",
    "Queensland": "QLD",
    "South Australia": "SA",
    "Western Australia": "WA",
    "Tasmania": "TAS",
    "Australian Capital Territory": "ACT",
    "Northern Territory": "NT",
    "Jervis Bay Territory": "JBT"
}

# Contact form to add a new contact
st.subheader('Add New Contact')
with st.form(key='contact_form'):
    # Title picklist
    title = st.selectbox("Title", ["Mr.", "Ms.", "Mrs.", "Dr.", "Prof."])
    
    # Gender picklist
    gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
    
    # Name input
    name = st.text_input("Name")
    
    # Email input
    email = st.text_input("Email")
    
    # Phone input
    phone = st.text_input("Phone")
    
    # Message input
    message = st.text_area("Message")
    
    # Address fields
    address_line = st.text_input("Address Line")
    suburb = st.text_input("Suburb")
    postcode = st.text_input("Postcode")
    
    # State picklist (Australia)
    state = st.selectbox("State", [
        "New South Wales", "Victoria", "Queensland", "South Australia", 
        "Western Australia", "Tasmania", "Australian Capital Territory", 
        "Northern Territory", "Jervis Bay Territory"
    ])
    
    # Country input (auto-fill with Australia for consistency)
    country = st.text_input("Country", value="Australia", disabled=True)
    
    submit_button = st.form_submit_button(label="Add Contact")
    
    if submit_button:
        # Email validation
        if not is_valid_email(email):
            st.error("Invalid email address!")
        else:
            # Insert the contact only if the email is valid
            if insert_contact(title, gender, name, email, phone, message, address_line, suburb, postcode, state, country):
                st.success("Contact added successfully!")
                st.rerun()  # Refresh the app to show the new contact

# Search for existing contacts to update
st.subheader('Search for Contact to Update')
search_name = st.text_input("Enter the contact name to search for")

if search_name:
    search_results = search_contact_by_name(search_name)
    if search_results:
        for contact in search_results:
            #st.write(f"ID: {contact['id']}, Name: {contact['name']}, Email: {contact['email']}, Phone: {contact['phone']}, Message: {contact['message']}, Address: {contact['address_line']}, Suburb: {contact['suburb']}, Postcode: {contact['postcode']}, State: {contact['state']}, Country: {contact['country']}")

            # Update the update contact form to handle state correctly
            with st.form(key=f'update_form_{contact["id"]}'):
                # Title picklist
                update_title = st.selectbox("Update Title", ["Mr.", "Ms.", "Mrs.", "Dr.", "Prof."], index=["Mr.", "Ms.", "Mrs.", "Dr.", "Prof."].index(contact['title']))
                # Gender picklist
                update_gender = st.selectbox("Update Gender", ["Male", "Female", "Non-binary", "Prefer not to say"], index=["Male", "Female", "Non-binary", "Prefer not to say"].index(contact['gender']))
                # Name input
                update_name = st.text_input("Update Name", value=contact['name'])
                # Email input
                update_email = st.text_input("Update Email", value=contact['email'])
                update_phone = st.text_input("Update Phone", value=contact['phone'])
                update_message = st.text_area("Update Message", value=contact['message'])
                update_address_line = st.text_input("Update Address Line", value=contact['address_line'])
                update_suburb = st.text_input("Update Suburb", value=contact['suburb'])
                update_postcode = st.text_input("Update Postcode", value=contact['postcode'])

                # For the state dropdown, use the mapping to find the correct index
                state_abbreviation = state_mapping.get(contact['state'], None)
                update_state = st.selectbox("Update State", list(state_mapping.keys()), index=list(state_mapping.values()).index(state_abbreviation) if state_abbreviation else 0)

                # Country input (auto-fill with Australia for consistency)
                update_country = st.text_input("Update Country", value=contact['country'], disabled=True)

                # Add the submit button for the form
                update_button = st.form_submit_button(label="Update Contact")

                if update_button:
                    # Email validation
                    if not is_valid_email(update_email):
                        st.error("Invalid email address!")
                    else:
                        # Update the contact only if the email is valid
                        if update_contact(contact['id'], update_title, update_gender, update_name, update_email, update_phone, update_message, update_address_line, update_suburb, update_postcode, update_state, update_country):
                            st.success(f"Contact '{contact['name']}' updated successfully!")
                            st.rerun()  # Refresh the app to show the updated contact

# Search for existing contacts to delete
st.subheader('Search for Contact to Delete')
delete_name = st.text_input("Enter the contact name to delete")

if delete_name:
    search_results_to_delete = search_contact_by_name(delete_name)
    if search_results_to_delete:
        for contact in search_results_to_delete:
            #st.write(f"ID: {contact['id']}, Name: {contact['name']}, Email: {contact['email']}, Phone: {contact['phone']}, Message: {contact['message']}")

            # Give each delete button a unique key based on the contact's ID
            delete_button = st.button(f"Delete {contact['name']}", key=f"delete_{contact['id']}")

            if delete_button:
                delete_contact(contact['id'])  # Use ID for deletion
                st.success(f"Contact '{contact['name']}' deleted successfully!")
                st.rerun()  # Refresh the app to remove the deleted contact
    else:
        st.warning(f"No contact found with the name '{delete_name}'.")
