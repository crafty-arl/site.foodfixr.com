import streamlit as st
import streamlit_shadcn_ui as ui
from supabase_client import supabase_client  # Import supabase_client from the new module
import pandas as pd

# Global variables to store user inputs
food_allergies = []
dietary_restrictions = []
chronic_conditions = []
autoimmune_conditions = []
gut_health_issues = ""
weight_management_goals = ""
blood_sugar_sensitivity = False
digestive_conditions = ""
medications_supplements = []
pregnancy_or_breastfeeding = False
food_preferences = []

def show_account():
    global food_allergies, dietary_restrictions, chronic_conditions, autoimmune_conditions
    global gut_health_issues, weight_management_goals, blood_sugar_sensitivity, digestive_conditions
    global medications_supplements, pregnancy_or_breastfeeding, food_preferences

    st.header("Health Conditions")

    selected_category = ui.tabs(options=["Allergies & Restrictions", "Chronic Conditions", "Other Issues", "Medications & Supplements"], value="allergies_restrictions")
    
    if selected_category == "Allergies & Restrictions":
        selected_tab = ui.tabs(options=["Food Allergies", "Dietary Restrictions"], value="food_allergies")
        if selected_tab == "Food Allergies":
            food_allergies = st.multiselect(
                "List your food allergies",
                ["Peanuts", "Shellfish", "Dairy", "Gluten"],
                food_allergies
            )
            custom_food_allergy = st.text_input("Add your own food allergy")
            if custom_food_allergy:
                food_allergies.append(custom_food_allergy)
        elif selected_tab == "Dietary Restrictions":
            dietary_restrictions = st.multiselect(
                "List your dietary restrictions",
                ["Vegan", "Vegetarian", "Keto", "Paleo"],
                dietary_restrictions
            )
            custom_dietary_restriction = st.text_input("Add your own dietary restriction")
            if custom_dietary_restriction:
                dietary_restrictions.append(custom_dietary_restriction)

    elif selected_category == "Chronic Conditions":
        selected_tab = ui.tabs(options=["Chronic", "Autoimmune"], value="chronic_conditions")
        if selected_tab == "Chronic":
            chronic_conditions = st.multiselect(
                "List your chronic conditions",
                ["Diabetes", "Hypertension", "Asthma", "Arthritis"],
                chronic_conditions
            )
            custom_chronic_condition = st.text_input("Add your own chronic condition")
            if custom_chronic_condition:
                chronic_conditions.append(custom_chronic_condition)
        elif selected_tab == "Autoimmune":
            autoimmune_conditions = st.multiselect(
                "List your autoimmune conditions",
                ["Lupus", "Rheumatoid Arthritis", "Celiac Disease", "Multiple Sclerosis"],
                autoimmune_conditions
            )
            custom_autoimmune_condition = st.text_input("Add your own autoimmune condition")
            if custom_autoimmune_condition:
                autoimmune_conditions.append(custom_autoimmune_condition)

    elif selected_category == "Other Issues":
        selected_tab = ui.tabs(options=["Gut Health", "Weight Mgmt", "Blood Sugar", "Digestive"], value="gut_health_issues")
        if selected_tab == "Gut Health":
            gut_health_issues = st.text_area("Describe your gut health issues", value=gut_health_issues, key="gut_health_issues_input")
        elif selected_tab == "Weight Mgmt":
            weight_management_goals = st.text_area("Describe your weight management goals", value=weight_management_goals, key="weight_management_goals_input")
        elif selected_tab == "Blood Sugar":
            blood_sugar_sensitivity = st.checkbox("Do you have blood sugar sensitivity?", value=blood_sugar_sensitivity, key="blood_sugar_sensitivity_input")
        elif selected_tab == "Digestive":
            digestive_conditions = st.text_area("Describe your digestive conditions", value=digestive_conditions, key="digestive_conditions_input")

    elif selected_category == "Medications & Supplements":
        selected_tab = ui.tabs(options=["Meds & Supps", "Pregnancy/Breastfeeding", "Preferences"], value="meds_supps")
        if selected_tab == "Meds & Supps":
            medications_supplements = st.multiselect(
                "List your medications and supplements",
                ["Vitamin D", "Omega-3", "Probiotics", "Iron"],
                medications_supplements
            )
            custom_medication_supplement = st.text_input("Add your own medication or supplement")
            if custom_medication_supplement:
                medications_supplements.append(custom_medication_supplement)
        elif selected_tab == "Pregnancy/Breastfeeding":
            pregnancy_or_breastfeeding = st.checkbox("Are you pregnant or breastfeeding?", value=pregnancy_or_breastfeeding, key="pregnancy_or_breastfeeding_input")
        elif selected_tab == "Preferences":
            food_preferences = st.multiselect(
                "List your food preferences",
                ["Spicy", "Sweet", "Salty", "Sour"],
                food_preferences
            )
            custom_food_preference = st.text_input("Add your own food preference")
            if custom_food_preference:
                food_preferences.append(custom_food_preference)

    clicked = ui.button("Save Health Conditions", key="save_health_conditions_btn", variant="outline")

    if clicked:
        # Save data to Supabase table
        data = {
            "user_id": st.session_state['user_id'],
            "food_allergies": food_allergies,
            "dietary_restrictions": dietary_restrictions, 
            "chronic_conditions": chronic_conditions,
            "gut_health_issues": gut_health_issues,
            "weight_management_goals": weight_management_goals,
            "blood_sugar_sensitivity": blood_sugar_sensitivity,
            "digestive_conditions": digestive_conditions,
            "medications_supplements": medications_supplements,
            "pregnancy_or_breastfeeding": pregnancy_or_breastfeeding,
            "autoimmune_conditions": autoimmune_conditions,
            "food_preferences": food_preferences
        }
        supabase_client.table("HealthConditions").insert(data).execute()
        st.success("Health conditions saved successfully!")

        # Clear global variables
        food_allergies = []
        dietary_restrictions = []
        chronic_conditions = []
        autoimmune_conditions = []
        gut_health_issues = ""
        weight_management_goals = ""
        blood_sugar_sensitivity = False
        digestive_conditions = ""
        medications_supplements = []
        pregnancy_or_breastfeeding = False
        food_preferences = []

    # Display table of submitted health conditions
    if 'user_id' in st.session_state:
        user_id = st.session_state['user_id']
        response = supabase_client.table("HealthConditions").select("*").eq("user_id", user_id).execute()
    if response:
        health_conditions = response.data
        # Filter out 'id' and 'user_id' from the response data
        for condition in health_conditions:
            condition.pop('condition_id', None)
            condition.pop('user_id', None)
            condition.pop('created_at', None)
        health_conditions_df = pd.DataFrame(health_conditions)
        ui.table(data=health_conditions_df, maxHeight=300)