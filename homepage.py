import streamlit as st

def home():
    st.set_page_config(page_title="CRM - Home", page_icon=":house:", layout="wide")
    
    # Add custom styles with CSS including sidebar styling
    st.markdown("""
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4; /* Lighter grey background */
                color: white; /* White text for better contrast */
                margin: 0;
                padding: 0;
            }

            .header {
                font-size: 50px;
                font-weight: 600;
                color: #3498db;
                text-align: center;
                margin-top: 50px;
                animation: fadeIn 1.5s ease-in-out;
            }

            .subtitle {
                font-size: 30px;
                color: white;
                text-align: center;
                margin-top: 10px;
                margin-bottom: 30px;
                animation: fadeIn 1.5s ease-in-out;
            }

            .content {
                font-size: 18px;
                color: white; /* White text */
                text-align: center;
                margin-bottom: 50px;
                animation: fadeIn 2s ease-in-out;
            }

            .box {
                padding: 20px;
                margin-top: 20px;
                animation: fadeIn 2s ease-in-out;
                text-align: center; /* Center the text */
                background-color: transparent; /* Remove the white box */
                border: none; /* Remove border */
            }

            .box p {
                margin-bottom: 20px;
            }

            .button {
                font-size: 18px;
                font-weight: bold;
                background-color: #3498db;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                border-radius: 12px;
                border: none;
                cursor: pointer;
                animation: bounceIn 1s ease-in-out;
            }

            .button:hover {
                background-color: #2980b9;
                transform: scale(1.1);
                transition: all 0.3s ease-in-out;
            }

            /* Position the logo at the top-right corner */
            .logo {
                position: absolute;
                top: 10px;
                right: 10px;
                width: 50%; /* Resize to half the size */
            }

            @keyframes fadeIn {
                0% {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                100% {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @keyframes bounceIn {
                0% {
                    opacity: 0;
                    transform: scale(0.5);
                }
                60% {
                    opacity: 1;
                    transform: scale(1.1);
                }
                100% {
                    transform: scale(1);
                }
            }

            /* New sidebar styling */
            .sidebar {
                background-color: #2c3e50;
                padding: 20px;
                border-radius: 10px;
                margin: 10px;
            }

            .nav-link {
                display: block;
                padding: 10px 15px;
                color: white;
                text-decoration: none;
                font-size: 16px;
                margin: 5px 0;
                border-radius: 5px;
                transition: background-color 0.3s;
            }

            .nav-link:hover {
                background-color: #3498db;
                color: white;
            }

            .nav-header {
                color: #3498db;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                text-align: center;
            }
        </style>
    """, unsafe_allow_html=True)

    # Create two columns: sidebar and main content
    col1, col2 = st.columns([1, 4])

    # Sidebar Navigation
    #with col1:
        #st.sidebar.title("Navigation")
        
        # Only keep the homepage link until other pages are created
        #st.sidebar.page_link("homepage.py", label="🏠 Home")

        # Comment out these links until the pages are created
        # st.sidebar.page_link("pages/1_application_form.py", label="📝 Application Form")
        # st.sidebar.page_link("pages/2_budget_line_items.py", label="💰 Budget Line Items")
        # st.sidebar.page_link("pages/3_budgets.py", label="📊 Budgets")
        # st.sidebar.page_link("pages/4_crm_contact.py", label="👥 CRM Contacts")
        # st.sidebar.page_link("pages/5_document_generation.py", label="📄 Document Generation")

    # Main content
    with col2:
        # Add the logo to the top right
        st.image('BusinessTracker.png', use_container_width=False, width=200)

        # Header section
        st.markdown('<div class="header">Welcome to BusinessTracker</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Efficient way to keep a track of your tasks</div>', unsafe_allow_html=True)

        # Description of the CRM features
        st.markdown("""
            <div class="content">
                Welcome to the CRM system, designed to simplify the process of managing and interacting with your contacts. This platform allows you to:
            </div>
        """, unsafe_allow_html=True)

        # Box for the description
        st.markdown("""
            <div class="box">
                <p>Add, update, and delete contacts</p>
                <p>Search contacts by name</p>
                <p>Send personalized emails to clients</p>
                <p>Maintain and organize customer data for better service</p>
            </div>
        """, unsafe_allow_html=True)

        # Call to Action button
        st.markdown(""" 
            <div style="text-align:center;">
                <a href="http://localhost:8501" class="button" style="color: white;">Manage Applications</a>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    home()
