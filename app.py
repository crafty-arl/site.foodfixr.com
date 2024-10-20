import datetime
import streamlit as st
import streamlit_shadcn_ui as ui
from dashboard import show_dashboard
from account import show_health_conditions
from assessments import show_assessments
from food_journal import show_food_journal
from supabase import create_client, Client
import os
import account  # Change this line
import logging
import json
from cryptography.fernet import Fernet

API_URL: str = os.environ.get("SUPABASE_URL")
API_KEY: str = os.environ.get("SUPABASE_KEY")

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@st.cache_resource
def get_supabase_client(api_url, api_key):
    return create_client(api_url, api_key)

supabase_client: Client = get_supabase_client(API_URL, API_KEY)

# Function to get query parameters
def get_query_params():
    # Use session state instead of experimental_get_query_params
    return {
        "signed_in": st.session_state.get("signed_in", "false")
    }

# Function to set query parameters
def set_query_params(params):
    # Update session state instead of experimental_set_query_params
    for key, value in params.items():
        st.session_state[key] = value

def show_auth_interface():
    st.title("User Authentication")
    st.write("Please enter your details to login or create an account.")
    selected_tab = st.radio("Select an option", options=['Login', 'Create Account'], index=0, key="auth_tabs_main")
    invite_code = st.text_input("Invite Code", key="invite_code_input_main", placeholder="Enter invite code")

    if selected_tab == 'Login':
        st.subheader("Login")
        email = st.text_input("Email", key="email_input_main", placeholder="Your email")
        password = st.text_input("Password", key="password_input_main", placeholder="Your password", type="password")
        login_button = st.button("Login", key="login_button_main")

        if login_button:
            handle_login(email, password, invite_code)
    elif selected_tab == 'Create Account':
        show_create_account_interface()

def handle_login(email, password, invite_code):
    logging.debug("Attempting login with email: %s", email)
    if email and password and invite_code == "FoodFixr25":
        try:
            response = supabase_client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if response.session:
                logging.info("Login successful for user: %s", email)
                st.session_state['access_token'] = response.session.access_token
                st.session_state['refresh_token'] = response.session.refresh_token
                st.session_state['user_id'] = response.user.id
                st.session_state['username'] = response.user.user_metadata.get('first_name')
                set_query_params({"signed_in": "true"})
                save_session_to_file()  # Save session to file
                st.experimental_rerun()  # Rerun the app to redirect to dashboard
            else:
                logging.error("Failed to login for user: %s", email)
                st.error("Failed to login.")
        except Exception as e:
            logging.exception("An error occurred during login")
            if "Email not confirmed" in str(e):
                st.error("Email not confirmed. Please check your inbox for a confirmation email.")
            else:
                st.error(f"An error occurred: {e}")
    else:
        logging.warning("Invalid login attempt with email: %s", email)
        st.error("Please enter your email, password, and a valid invite code to login.")

def show_create_account_interface():
    st.subheader("Create Account")
    username = st.text_input("User Name", key="username_input_main", placeholder="Create a User Name")
    email = st.text_input("Email", key="create_email_input_main", placeholder="Your email")
    password = st.text_input("Password", key="create_password_input_main", placeholder="Create a password", type="password")
    retype_password = st.text_input("Retype Password", key="retype_password_input_main", placeholder="Retype your password", type="password")
    date_of_birth = st.date_input("Date of Birth", key="dob_input_main")
    create_account_button = st.button("Create Account", key="create_account_button_main")

    if create_account_button:
        handle_create_account(username, email, password, retype_password, date_of_birth)

def handle_create_account(username, email, password, retype_password, date_of_birth):
    invite_code = st.session_state.get("invite_code_input_main")
    if username and email and password and retype_password and date_of_birth and invite_code == "FoodFixr25":
        if password == retype_password:
            try:
                response = supabase_client.auth.sign_up(
                    {
                        "email": email,
                        "password": password,
                        "options": {"data": {"first_name": username, "date_of_birth": str(date_of_birth)}},
                    }
                )
                if response.user:
                    user_id = response.user.id
                    # Insert new user data into UserProfile table
                    insert_response = supabase_client.table("UserProfile").insert({
                        "name": username,
                        "email": email,
                        "date_of_birth": str(date_of_birth),
                        "user_id": user_id,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }).execute()

                    if insert_response:
                        st.session_state['user_id'] = user_id
                        st.session_state['username'] = username
                        set_query_params({"signed_in": "true"})
                        st.success(f"Account created successfully. Welcome, {username}!")
                        st.experimental_rerun()  # Rerun the app to redirect to dashboard
                    else:
                        st.error("Failed to create account.")
                else:
                    st.error("Failed to create account.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Passwords do not match.")
    else:   
        st.error("Please enter all the required details and a valid invite code to create an account.")

# Function definitions for encryption and session management
def load_key():
    key_file = "session_encryption/secret.key"
    if not os.path.exists(key_file):
        # Generate a new key if the file doesn't exist
        key = Fernet.generate_key()
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, "wb") as file:
            file.write(key)
        return key
    else:
        # Read the existing key
        with open(key_file, "rb") as file:
            return file.read()

def encrypt_data(data):
    key = load_key()
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(data):
    key = load_key()
    f = Fernet(key)
    return f.decrypt(data).decode()

def save_session_to_file():
    session_data = {
        "access_token": st.session_state.get('access_token'),
        "refresh_token": st.session_state.get('refresh_token'),
        "user_id": st.session_state.get('user_id'),
        "username": st.session_state.get('username')
    }
    encrypted_data = encrypt_data(json.dumps(session_data))
    with open("session.json", "wb") as file:
        file.write(encrypted_data)

def load_session_from_file():
    try:
        with open("session.json", "rb") as file:
            encrypted_data = file.read()
            session_data = json.loads(decrypt_data(encrypted_data))
            st.session_state.update(session_data)
            logging.info("Session loaded from file")
    except Exception as e:
        logging.error("Failed to load session from file: %s", e)

# Load session data on app start
if 'access_token' not in st.session_state:
    load_session_from_file()

query_params = get_query_params()
signed_in = query_params.get("signed_in", "false")

if signed_in == "true" and 'username' in st.session_state:
    # Add sign out button to the right corner
    _, _, sign_out_col = st.columns([1, 1, 1])
    with sign_out_col:
        if st.button("Sign Out", key="sign_out_button"):
            # Sign out from Supabase
            supabase_client.auth.sign_out()
            # Clear all session state
            st.session_state.clear()
            # Remove session file
            os.remove("session.json")
            st.experimental_rerun()
    
    # Add tabs for different sections
    value = ui.tabs(options=['Dashboard', 'Health Conditions', 'Assessments', 'Food Journal'], default_value='Dashboard', key="kanaries")

    if value == 'Dashboard':
        show_dashboard()
    elif value == 'Health Conditions':
        account.show_account()
    elif value == 'Assessments':
        show_assessments()
    elif value == 'Food Journal':
        show_food_journal()
else:
    show_auth_interface()

def refresh_token():
    if 'refresh_token' in st.session_state:
        try:
            response = supabase_client.auth.refresh_session(st.session_state['refresh_token'])
            if response.session:
                st.session_state['access_token'] = response.session.access_token
                st.session_state['refresh_token'] = response.session.refresh_token
                return True
        except Exception as e:
            st.error(f"Failed to refresh token: {e}")
    return False

def fetch_user_data(access_token):
    # Use the access token to fetch user data from your backend
    # This is a placeholder and should be replaced with actual API calls
    return {"name": st.session_state['username'], "id": st.session_state['user_id']}

def process_with_ai(user_data):
    # This is where you would integrate your AI processing
    # For now, it's just a placeholder
    return f"AI recommendations for {user_data['name']}"

def show_user_interface(user_data, ai_recommendations):
    st.write(f"Welcome, {user_data['name']}!")
    st.write(ai_recommendations)
    # Add your tabs and other UI elements here
