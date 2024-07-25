import streamlit as st
import pandas as pd
from database import get_user, add_user, get_all_residents, get_resident, add_or_update_resident

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None
if 'residents' not in st.session_state:
    st.session_state.residents = []

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
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# Logout Functionality
def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.edit_index = None
    st.session_state.residents = []
    st.experimental_rerun()

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
                st.experimental_rerun()
            else:
                st.warning("No resident found with the given apartment number.")
                return

        # Default values when adding
        apartment_number = apartment_number_input
        resident_type = "Owner"
        owner_name = ""
        owner_contact = ""
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
            resident_name = resident[4]
            resident_contact = resident[5]
            maintenance_paid = resident[6]
            defaulted_amount = resident[7]

        # Form to input resident information
        with st.form(key='resident_form'):
            resident_type = st.selectbox("Occupancy Type", ["Owner", "Tenant"], index=["Owner", "Tenant"].index(resident_type))
            owner_name = st.text_input("Owner Name", value=owner_name)
            owner_contact = st.text_input("Owner Contact", value=owner_contact)

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
                add_or_update_resident(apartment_number, resident_type, owner_name, owner_contact, resident_name, resident_contact, maintenance_paid, defaulted_amount)
                st.success("Resident information saved successfully")
                st.session_state.edit_index = None
                st.experimental_rerun()

# Display Residents Page
def display_residents_page():
    st.title("Residents Information")

    with st.container():
        st.write("Scroll here to view more content...")
        st.session_state.residents = get_all_residents()

        if st.session_state.residents:
            # Create a DataFrame for display
            df = pd.DataFrame(st.session_state.residents, columns=["apartment_number", "resident_type", "owner_name", "owner_contact", "resident_name", "resident_contact", "maintenance_paid", "defaulted_amount"])
            st.dataframe(df)
        else:
            st.write("No residents information available yet.")

# Main app logic
if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a Page", ["Display Residents", "Add Resident"])

    if page == "Add Resident":
        add_resident_page()
    elif page == "Display Residents":
        display_residents_page()

    st.sidebar.button("Logout", on_click=logout)






