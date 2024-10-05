import datetime
import streamlit as st
import streamlit_shadcn_ui as ui
from dashboard import show_dashboard
from account import show_account
from assessments import show_assessments
from food_journal import show_food_journal
from supabase import create_client, Client
import os

API_URL: str = os.environ.get("SUPABASE_URL")
API_KEY: str = os.environ.get("SUPABASE_KEY")

@st.cache_resource
def get_supabase_client(api_url, api_key):
    return create_client(api_url, api_key)

supabase_client: Client = get_supabase_client(API_URL, API_KEY)

# Function to check if user_id exists in the UserProfile table
def user_exists(user_id):
    response = supabase_client.table("UserProfile").select("*").eq("user_id", user_id).execute()
    return len(response.data) > 0

st.sidebar.header("User Login Screen")

if 'user_id' in st.session_state:
    print(f"Debug: user_id in session state: {st.session_state['user_id']}")
    if user_exists(st.session_state['user_id']):
        st.sidebar.write(f"Welcome back, {st.session_state['username']}!")
        sign_out_button = st.sidebar.button("Sign Out", key="sign_out_button")
        if sign_out_button:
            response = supabase_client.auth.sign_out()
            if response:
                st.session_state.clear()
                print("Debug: Session state cleared on sign out.")
            else:
                st.sidebar.error("Refresh the page...")
    else:
        st.sidebar.error("User ID not found. Please create an account.")
        st.session_state.clear()
        print("Debug: Session state cleared because user ID not found.")
else:
    st.sidebar.write("Please enter your details to login or create an account.")
    selected_tab = st.sidebar.radio("Select an option", options=['Login', 'Create Account'], index=0, key="auth_tabs")
    invite_code = st.sidebar.text_input("Invite Code", key="invite_code_input", placeholder="Enter invite code")

    if selected_tab == 'Login':
        st.sidebar.subheader("Login")
        email = st.sidebar.text_input("Email", key="email_input", placeholder="Your email")
        password = st.sidebar.text_input("Password", key="password_input", placeholder="Your password", type="password")
        login_button = st.sidebar.button("Login", key="login_button")

        if login_button:
            if email and password and invite_code == "FoodFixr25":
                try:
                    response = supabase_client.auth.sign_in_with_password(
                        {"email": email, "password": password}
                    )
                    if response:
                        user_id = response.user.id
                        if user_exists(user_id):
                            user_metadata = response.user.user_metadata
                            st.session_state['user_id'] = user_id
                            st.session_state['username'] = user_metadata['first_name']
                            st.sidebar.empty()
                            st.write(f"Welcome back, {st.session_state['username']}!")
                            st.balloons()
                        else:
                            st.sidebar.error("User ID not found. Please create an account.")
                    else:
                        st.sidebar.error("Failed to login.")
                except Exception as e:
                    if "Email not confirmed" in str(e):
                        st.sidebar.error("Email not confirmed. Please check your inbox for a confirmation email.")
                    else:
                        st.sidebar.error(f"An error occurred: {e}")
            else:
                st.sidebar.error("Please enter your email, password, and a valid invite code to login.")

    elif selected_tab == 'Create Account':
        st.sidebar.subheader("Create Account")
        username = st.sidebar.text_input("User Name", key="username_input", placeholder="Create a User Name")
        email = st.sidebar.text_input("Email", key="create_email_input", placeholder="Your email")
        password = st.sidebar.text_input("Password", key="create_password_input", placeholder="Create a password", type="password")
        retype_password = st.sidebar.text_input("Retype Password", key="retype_password_input", placeholder="Retype your password", type="password")
        date_of_birth = st.sidebar.date_input("Date of Birth", key="dob_input")
        create_account_button = st.sidebar.button("Create Account", key="create_account_button")

        if create_account_button:
            print(f"Debug: Username entered: {username}")
            print(f"Debug: Email entered: {email}")
            print(f"Debug: Password entered: {password}")
            print(f"Debug: Retype Password entered: {retype_password}")
            print(f"Debug: Date of Birth entered: {date_of_birth}")
            print(f"Debug: Invite Code entered: {invite_code}")
            
            if username and email and password and retype_password and date_of_birth and invite_code == "FIXED_INVITE_CODE":
                if password == retype_password:
                    try:
                        response = supabase_client.auth.sign_up(
                            {
                                "email": email,
                                "password": password,
                                "options": {"data": {"first_name": username, "date_of_birth": str(date_of_birth)}},
                            }
                        )
                        print(f"Debug: Response from sign_up: {response}")
                        if response:
                            user_id = response.user.id
                            # Insert new user data into UserProfile table
                            insert_response = supabase_client.table("UserProfile").insert({
                                "name": username,
                                "email": email,
                                "date_of_birth": str(date_of_birth),
                                "user_id": user_id,
                                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }).execute()
                            print(f"Debug: Insert response: {insert_response}")

                            if insert_response:
                                st.session_state['user_id'] = user_id
                                st.session_state['username'] = username
                                st.sidebar.empty()  # Remove the sidebar
                                st.write(f"Welcome, {username}!")
                                st.write(st.session_state['user_id'])
                            else:
                                st.sidebar.error("Failed to create account.")
                        else:
                            st.sidebar.error("Failed to create account.")
                    except Exception as e:
                        st.sidebar.error(f"An error occurred: {e}")
                else:
                    st.sidebar.error("Passwords do not match.")
            else:
                st.sidebar.error("Please enter all the required details and a valid invite code to create an account.")

# Add tabs for different sections only if the user is logged in
if 'user_id' in st.session_state:
    value = ui.tabs(options=['Dashboard', 'Health Conditions', 'Assesments', 'Food Journal'], default_value='Dashboard', key="kanaries")

    if value == 'Dashboard':
        show_dashboard()
    elif value == 'Health Conditions':
        show_account()
    elif value == 'Assesments':
        show_assessments()
    elif value == 'Food Journal':
        show_food_journal()