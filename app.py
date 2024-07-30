import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from database import get_user, add_user, get_all_residents, get_resident, add_or_update_resident

# Load environment variables
load_dotenv()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None
if 'residents' not in st.session_state:
    st.session_state.residents = []
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Send email function
def send_email(to_email, subject, body):
    try:
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT'))
        from_email = os.getenv('EMAIL_USER')
        from_password = os.getenv('EMAIL_PASSWORD')

        # Check if environment variables are loaded
        if not smtp_server or not smtp_port or not from_email or not from_password:
            st.error("SMTP configuration is missing.")
            return

        # Setup the server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, from_password)

        # Create email
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server.send_message(msg)
        server.quit()
        #st.success(f"Email sent successfully to {to_email}")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Login Page
def login_page():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        user = get_user(username)
        if user and user[1] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid username or password")

# Logout Functionality
def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.edit_index = None
    st.session_state.residents = []
    st.rerun()

# Add/Update Resident Page
def add_resident_page():
    st.title("Add/Update Resident")
    
    with st.container():
        st.write("Scroll here to view more content...")
        apartment_number_input = st.text_input("Apartment Number")

        if st.button("Fetch Details"):
            resident = get_resident(apartment_number_input)
            if resident:
                st.session_state.edit_index = next(i for i, r in enumerate(st.session_state.residents) if r[0] == apartment_number_input)
                st.rerun()
            else:
                st.warning("No resident found with the given apartment number.")
                return

        # Default values when adding
        apartment_number = apartment_number_input
        resident_type = "Owner"
        owner_name = ""
        owner_contact = ""
        owner_email = ""  # Default value for new field
        resident_name = ""
        resident_contact = ""
        maintenance_paid = "No"
        defaulted_amount = 0.0

        if st.session_state.edit_index is not None:
            # Prefill form if editing
            resident = st.session_state.residents[st.session_state.edit_index]
            apartment_number = resident[0]
            resident_type = resident[1]
            owner_name = resident[2]
            owner_contact = resident[3]
            owner_email = resident[4]  # Prefill email
            resident_name = resident[5]
            resident_contact = resident[6]
            maintenance_paid = resident[7]
            defaulted_amount = resident[8]

        # Form to input resident information
        with st.form(key='resident_form'):
            resident_type = st.selectbox("Occupancy Type", ["Owner", "Tenant"], index=["Owner", "Tenant"].index(resident_type))
            owner_name = st.text_input("Owner Name", value=owner_name)
            owner_contact = st.text_input("Owner Contact", value=owner_contact)
            owner_email = st.text_input("Owner Email", value=owner_email)  # New field

            if resident_type == "Owner":
                resident_name = owner_name
                resident_contact = owner_contact
                st.write("Since you chose Owner, Resident Name and Contact will be the same as Owner.")
            else:
                resident_name = st.text_input("Occupant Name", value=resident_name)
                resident_contact = st.text_input("Occupant Contact", value=resident_contact)

            maintenance_paid = st.selectbox("Maintenance Paid", ["Yes", "No"], index=["Yes", "No"].index(maintenance_paid))
            defaulted_amount = st.number_input("Defaulted Amount", min_value=0.0, value=defaulted_amount, format="%.2f")

            submit_button = st.form_submit_button(label="Save")

            if submit_button:
                add_or_update_resident(apartment_number, resident_type, owner_name, owner_contact, owner_email, resident_name, resident_contact, maintenance_paid, defaulted_amount)
                st.success("Resident information saved successfully")
                st.session_state.edit_index = None
                st.session_state.form_submitted = True

    if st.session_state.form_submitted:
        st.session_state.form_submitted = False
        st.rerun()

# Display Residents Page
def display_residents_page():
    st.title("Residents Information")

    with st.container():
        st.write("Scroll here to view more content...")
        st.session_state.residents = get_all_residents()

        if st.session_state.residents:
            # Create a DataFrame for display
            df = pd.DataFrame(st.session_state.residents, columns=[
                "apartment_number", "resident_type", "owner_name", "owner_contact", "owner_email", "resident_name", "resident_contact", "maintenance_paid", "defaulted_amount"])
            st.dataframe(df)
        else:
            st.write("No residents information available yet.")

# Send Emails Page
def send_emails_page():
    st.title("Send Email to All Residents")

    # Default values
    default_subject = "JRFOWS Maintenance fees for "
    default_body = """Dear Residents,

Please pay the Maintenance fees (Rs 4000) before 10th of this month to avoid late fees.

Thanks 
JRFOWS"""

    # Input fields with default values
    email_subject = st.text_input("Email Subject", default_subject)
    email_body = st.text_area("Email Body", default_body)

    if st.button("Send Email to All"):
        residents = get_all_residents()
        if not residents:
            st.warning("No residents found.")
            return

        for resident in residents:
            email = resident[4]  # owner_email column
            if email:
                send_email(email, email_subject, email_body)
        st.success("Emails sent to all residents.")

# Main app logic
if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a Page", ["Display Residents", "Add Resident", "Send Emails"])

    if page == "Add Resident":
        add_resident_page()
    elif page == "Display Residents":
        display_residents_page()
    elif page == "Send Emails":
        send_emails_page()

    st.sidebar.button("Logout", on_click=logout)