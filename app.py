import streamlit as st
import streamlit_shadcn_ui as ui
from dashboard import show_dashboard
from account import show_account
from assessments import show_assessments
from food_journal import show_food_journal
import os
from supabase import create_client, Client
from postgrest import APIError

API_URL: str = os.environ.get("SUPABASE_URL")
API_KEY: str = os.environ.get("SUPABASE_KEY")
supabase_client: Client = create_client(API_URL, API_KEY)

st.write(supabase_client)

ui.avatar(src="https://your_image_url")
st.write("Welcome User name")

selected_tab = ui.tabs(options=['Dashboard', 'Account', 'Assessments', 'Food Journal'], default_value='Dashboard', key="kanaries")

if selected_tab == 'Dashboard':
    show_dashboard()
elif selected_tab == 'Account':
    show_account()
elif selected_tab == 'Assessments':
    show_assessments()
elif selected_tab == 'Food Journal':
    show_food_journal()

if st.button('Insert Data'):
    try:
        response = (
            supabase_client.table("table_name")
            .insert(
                [
                    {
                        "id": 1,
                        "Date": "Denmark",
                        "Race": "1",
                        "Track": "Mario Kart Stadium",
                        "Finish": "1",
                    }
                ]
            )
            .execute()
        )
        st.write("Data inserted successfully")
    except APIError as e:
        st.error(f"An error occurred: {e}")
