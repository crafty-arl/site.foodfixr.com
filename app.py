import streamlit as st
import streamlit_shadcn_ui as ui
from dashboard import show_dashboard
from account import show_account
from assessments import show_assessments
from food_journal import show_food_journal

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
