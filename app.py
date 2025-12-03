import streamlit as st

import time



# --- 1. CONFIGURATION & DESIGN ---

st.set_page_config(page_title="Login / Sign Up UI", page_icon="🔑", layout="centered")



# Custom CSS for better presentation (optional, but nice)

st.markdown("""

    <style>

    /* Center the main content better */

    .stApp {

        background-color: #f7f9fc;

    }

    .stContainer {

        padding: 2rem;

        background-color: white;

        border-radius: 10px;

        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

    }

    h2 {

        color: #1f50a2; /* A nice blue color */

        text-align: center;

        margin-bottom: 20px;

    }

    .stButton>button {

        background-color: #1f50a2;

        color: white;

        border: none;

        border-radius: 5px;

        padding: 10px;

        width: 100%;

        margin-top: 15px;

    }

    </style>

""", unsafe_allow_html=True)



st.title("Welcome to the App")

st.markdown("A Streamlit version of your Login/Sign Up interface.")



# Use Streamlit columns to display Sign In and Sign Up forms side-by-side

col1, col2 = st.columns(2)



# --- 2. SIGN IN FORM (Equivalent to form-box login) ---

with col1.container(border=True):

    st.markdown("<h2>Sign In</h2>", unsafe_allow_html=True)

    

    # Text input fields

    login_username = st.text_input("Username", key="login_user", placeholder="Enter your username")

    login_password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")

    

    # Login Button

    if st.button("Login", key="login_btn", use_container_width=True):

        if login_username and login_password:

            # Placeholder action for login

            with st.spinner('Logging in...'):

                time.sleep(1) # Simulate network delay

            st.success(f"Successfully logged in as **{login_username}**!")

        else:

            st.warning("Please enter both username and password.")



# --- 3. SIGN UP FORM (Equivalent to form-box register) ---

with col2.container(border=True):

    st.markdown("<h2>Sign Up</h2>", unsafe_allow_html=True)

    

    # Text input fields

    register_username = st.text_input("Username", key="reg_user", placeholder="Choose a username")

    register_email = st.text_input("Email", key="reg_email", placeholder="Enter your email")

    register_password = st.text_input("Password", type="password", key="reg_pass", placeholder="Choose a secure password")

    

    # Sign Up Button

    if st.button("Sign Up", key="register_btn", use_container_width=True):

        if register_username and register_email and register_password:

            # Placeholder action for registration

            with st.spinner('Registering user...'):

                time.sleep(1) # Simulate network delay

            st.success(f"Account for **{register_username}** created! Check **{register_email}** for verification.")

        else:

            st.warning("Please fill in all registration fields.")



st.markdown("---")

st.info("In a real application, the actions would interact with a database for authentication.")
