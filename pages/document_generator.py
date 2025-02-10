import streamlit as st
import sqlite3
from fpdf import FPDF
import base64
from io import BytesIO
from datetime import datetime
from sqlite3 import Error
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import tempfile

# Function to connect to the database
def get_db_connection():
    try:
        conn = sqlite3.connect(r'C:\Users\james\OneDrive\Desktop\JamesManagerSystem\crm.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None
    
# Function to save the signature to the database
def save_signature_to_db(contact_id, signature_image):
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    # Convert image to bytes and store it in the database
    with BytesIO() as buffer:
        signature_image.save(buffer, format="PNG")
        signature_bytes = buffer.getvalue()

    # Get the current timestamp when the signature is applied
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(''' 
        UPDATE application_documents
        SET signature = ?, timestamp = ?
        WHERE contact_id = ?
    ''', (sqlite3.Binary(signature_bytes), timestamp, contact_id))
    
    conn.commit()
    conn.close()
    st.success(f"Signature saved successfully! Applied on {timestamp}")

# Function to create the signature canvas
def draw_signature(contact_id):
    # Title for the signature page
    st.title("Draw Your Signature")

    # Display the canvas to draw the signature
    st.subheader("Use your mouse to draw your signature.")
    
    # Create canvas with 500x200 dimensions
    canvas_result = st_canvas(
        stroke_width=3,
        stroke_color="black",
        background_color="white",
        height=200,
        width=500,
        drawing_mode="freedraw",
        key="signature_canvas"
    )

    # After the user finishes drawing the signature
    if canvas_result.image_data is not None:
        # Convert the image to PIL format for saving
        signature_image = Image.fromarray(canvas_result.image_data.astype('uint8'))

        # Button to save the drawn signature
        if st.button("Save Signature"):
            # Save the signature to the database
            save_signature_to_db(contact_id, signature_image)
            st.image(signature_image, caption="Your Signature", use_column_width=True)
            # Reset the drawing flag
            st.session_state.drawing_signature = False

# Function to fetch signature and timestamp from the database
def fetch_signature_and_timestamp_from_db(contact_id):
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT signature, timestamp
        FROM application_documents
        WHERE contact_id = ?
    ''', (contact_id,))
    
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        signature_image = BytesIO(result[0])  # Convert the binary data into BytesIO object for FPDF
        timestamp = result[1]  # The timestamp when the signature was applied
        return signature_image, timestamp
    return None, None

# Function to fetch signature from the database
def fetch_signature_from_db(contact_id):
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT signature
        FROM application_documents
        WHERE contact_id = ?
    ''', (contact_id,))
    
    signature = cursor.fetchone()
    conn.close()

    if signature and signature[0]:
        signature_image = BytesIO(signature[0])  # Convert the binary data into BytesIO object for FPDF
        return signature_image
    return None

# Function to fetch contact and application details together
def fetch_contact_with_application(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to join contact data with application data
    cursor.execute(''' 
        SELECT c.id, c.name, c.email, c.phone, a.interest, a.reason, a.skillsets, d.document_name 
        FROM contacts c 
        JOIN applications a ON c.id = a.contact_id 
        LEFT JOIN application_documents d ON c.id = d.contact_id 
        WHERE c.id = ? 
    ''', (contact_id,))
    contact_data = cursor.fetchone()
    conn.close()

    # Check if contact data is found
    if contact_data:
        return {
            "id": contact_data["id"],
            "name": contact_data["name"],
            "email": contact_data["email"],
            "phone": contact_data["phone"],
            "interest": contact_data["interest"],
            "reason": contact_data["reason"],
            "skillsets": contact_data["skillsets"],
            "document_name": contact_data["document_name"]
        }
    return None

# Function to create a form-like document with the signature next to the header
def create_document(contact_name, contact_email, contact_phone, document_name, interest, reason, skillsets, signature_image=None, timestamp=None):
    pdf = FPDF()
    pdf.add_page()

    # Set title and header
    pdf.set_font("Arial", size=18, style='B')
    pdf.set_text_color(52, 152, 219)  # Blue color for the header
    pdf.cell(200, 10, txt="Job Application Form", ln=True, align='C')
    pdf.ln(10)

    # Add form fields section
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Position Applied For:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"{interest}", ln=True)
    pdf.ln(5)

    # Name field (First and Last)
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Name:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"{contact_name}", ln=True)
    pdf.ln(5)

    # Email field
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Email:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"{contact_email}", ln=True)
    pdf.ln(5)

    # Phone field
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Phone Number:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"{contact_phone}", ln=True)
    pdf.ln(5)

    # Reason field
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Reason for Application:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(200, 10, txt=f"{reason}")
    pdf.ln(5)

    # Skillsets field
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Skillsets:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(200, 10, txt=f"{skillsets}")
    pdf.ln(10)

    # Document info
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Document Information", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Document: {document_name}", ln=True)
    pdf.ln(10)

    # Signature section: place the signature image next to the header
    pdf.set_font("Arial", size=12)
    pdf.cell(140, 10, txt="Signature:", ln=True)

    # If signature_image is provided, place it next to the signature text
    if signature_image:
        # Save the BytesIO signature image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            signature_image.seek(0)  # Rewind the image to the start
            temp_file.write(signature_image.read())  # Save to temp file
            temp_file_path = temp_file.name  # Get the path of the temporary file

        # Now add the image to the PDF
        pdf.image(temp_file_path, x=30, y=pdf.get_y(), w=40, h=20)  # Adjust the x, y position as needed

    pdf.ln(30)  # Space after signature

    # If timestamp is provided, add it to the document
    if timestamp:
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Signature applied on: {timestamp}", ln=True)
        pdf.ln(10)

    # Timestamp at the bottom of the document
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(200, 10, txt=f"Document signed on: {timestamp}", ln=True)
    pdf.ln(20)

    # Create a buffer to store the PDF
    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))  # Write to memory buffer
    pdf_output.seek(0)  # Reset the buffer pointer to the beginning of the file

    return pdf_output

# Function to provide the PDF download link
def generate_and_download_pdf(contact_name, contact_email, contact_phone, document_name, interest, reason, skillsets, contact_id, signature_image):

    # Fetch the signature image and timestamp from the database
    signature_image, timestamp = fetch_signature_and_timestamp_from_db(contact_id)

    # Create the document
    pdf_output = create_document(contact_name, contact_email, contact_phone, document_name, interest, reason, skillsets, signature_image)

    # Provide PDF download link
    pdf_output.seek(0)
    b64_pdf = base64.b64encode(pdf_output.read()).decode('utf-8')
    href = f'<a href="data:file/pdf;base64,{b64_pdf}" download="{document_name}.pdf">Download the document</a>'
    st.markdown(href, unsafe_allow_html=True)

# Function to fetch contacts and display the dropdown menu
def document_page():
    st.title("Document Generation")

    # Initialize the session state for drawing signature if not already initialized
    if "drawing_signature" not in st.session_state:
        st.session_state.drawing_signature = False

    # Fetch contacts and display the dropdown menu
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()  # This will return a list of Row objects

    conn.close()

    # Display a dropdown menu with the list of contacts
    if contacts:
        contact_names = [contact[3] for contact in contacts]  # contact[3] is name in the database index.

        contact_selection = st.selectbox("Select a contact", contact_names)

        # Fetch selected contact details
        selected_contact = contacts[contact_names.index(contact_selection)]
        contact_id = selected_contact[0]  # Assuming contact[0] is the contact_id

        # Fetch the contact and application details together
        contact_data = fetch_contact_with_application(contact_id)

        if contact_data:
            contact_name = contact_data["name"]
            contact_email = contact_data["email"]
            contact_phone = contact_data["phone"]
            interest = contact_data["interest"]
            reason = contact_data["reason"]
            skillsets = contact_data["skillsets"]
            document_name = contact_data["document_name"]

            # Display the contact information
            st.write(f"Contact ID: {contact_id}")
            st.write(f"Contact Name: {contact_name}")
            st.write(f"Contact Email: {contact_email}")
            st.write(f"Contact Phone: {contact_phone}")
            st.write(f"Interest: {interest}")
            st.write(f"Reason: {reason}")
            st.write(f"Skillsets: {skillsets}")

            # Option to draw a signature
            if st.button("Draw Signature"):
                st.session_state.drawing_signature = True

            # Only show the signature drawing canvas if the flag is set
            if st.session_state.drawing_signature:
                draw_signature(contact_id)

            # Fetch signature from the database and pass to PDF generation
            signature_image = fetch_signature_from_db(contact_id)

            # Button to generate and download PDF
            if st.button("Generate and Download Document"):
                generate_and_download_pdf(contact_name, contact_email, contact_phone, document_name, interest, reason, skillsets, contact_id, signature_image)
        else:
            st.write("No data found for this contact.")
    else:
        st.write("No contacts found in the database.")

# Run the document generation page
if __name__ == "__main__":
    document_page()
