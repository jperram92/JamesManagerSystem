import streamlit as st
import sqlite3
from sqlite3 import Error

# Function to connect to the database
def get_db_connection():
    try:
        conn = sqlite3.connect(r'C:\Users\james\OneDrive\Desktop\JamesManagerSystem\crm.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        print(e)
        return None

# Function to fetch all contacts from the database
def fetch_contacts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts')
    contacts = cursor.fetchall()
    conn.close()
    return contacts

# Function to insert the new application data into the database
def insert_application(contact_id, interest, reason, skillsets):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO applications (contact_id, interest, reason, skillsets)
        VALUES (?, ?, ?, ?)
    ''', (contact_id, interest, reason, skillsets))  # Insert the new data
    conn.commit()
    conn.close()

# Streamlit interface
def application_form():
    st.title("New Application Form")

    # Fetch existing contacts from the database
    contacts = fetch_contacts()

    if contacts:
        # Select an existing contact
        contact_names = [f"{contact['name']} ({contact['email']})" for contact in contacts]
        contact_index = st.selectbox("Select an Existing Contact", contact_names)

        # Fetch the selected contact's ID
        selected_contact = contacts[contact_names.index(contact_index)]
        contact_id = selected_contact['id']
        
        # Display the contact's information
        st.write(f"Selected Contact: {selected_contact['name']}")
        st.write(f"Email: {selected_contact['email']}")
        st.write(f"Phone: {selected_contact['phone']}")

        # Now show the application questions
        st.subheader("Application Form")

        # Collect new application data
        interest = st.text_area("What are you interested in doing?")
        reason = st.text_area("What is your primary reason for engaging?")
        skillsets = st.text_area("What skillsets do you bring?")

        # When the form is completed, save the new application data to the database
        if st.button("Submit Application"):
            if interest and reason and skillsets:
                insert_application(contact_id, interest, reason, skillsets)
                st.success("Application submitted successfully!")
            else:
                st.error("Please fill out all fields before submitting.")
    else:
        st.write("No contacts available. Please add contacts to proceed.")

# Run the application form function
if __name__ == "__main__":
    application_form()
