import random
import streamlit as st
import streamlit_shadcn_ui as ui
from supabase import create_client, Client
import os
import json
from datetime import datetime

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase_client: Client = create_client(url, key)

# Global variable to track progress
progress = 0

def insert_data_if_not_exists(table_name, data, unique_key):
    for item in data:
        try:
            # Convert unique_key to string to avoid UUID error
            item[unique_key] = str(item[unique_key])
            response = supabase_client.table(table_name).select("*").eq(unique_key, item[unique_key]).execute()
            if not response.data:
                supabase_client.table(table_name).insert(item).execute()
        except Exception as e:
            if "Server disconnected" not in str(e):
                st.error(f"An error occurred: {e}")
            # Optionally, log the error or take other actions

def show_assessments():
    global progress

    st.header("Assessments")
    st.write("This is the Assessments page.")
    
    # Load SurveyCategory.json and SurveyQuestion.json with error handling
    try:
        with open('json_surveys/SurveyCategory.json') as f:
            survey_category_data = json.load(f)
    except json.JSONDecodeError as e:
        st.error(f"Error loading SurveyCategory.json: {e}")
        return
    
    try:
        with open('json_surveys/SurveyQuestion.json') as f:
            survey_question_data = json.load(f)
    except json.JSONDecodeError as e:
        st.error(f"Error loading SurveyQuestion.json: {e}")
        return
    
    # Calculate progress
    total_questions = len(survey_question_data)
    answered_questions = 0
    
    # Display progress bar at the top
    st.progress(progress)
    
    # Create tabs for each survey category
    category_names = [category['category_name'] for category in survey_category_data]
    selected_tab = ui.tabs(options=category_names, default_value=category_names[0], key="survey_categories")
    
    # Display questions for the selected category
    for category in survey_category_data:
        if selected_tab == category['category_name']:
            st.subheader(category['category_name'])
            category_questions = [q for q in survey_question_data if q['category_id'] == str(category['category_id'])]
            if not category_questions:
                st.error("No questions available for this category.")
                continue
            question_numbers = [f"Question {q['question_id']}" for q in category_questions]
            try:
                selected_question = ui.select(options=question_numbers, key=f"questions_{category['category_id']}")
            except IndexError as e:
                st.error(f"Error: {e}")
                continue
            st.markdown(f"Survey: {selected_question}")
            for question in category_questions:
                if selected_question == f"Question {question['question_id']}":
                    st.write(question['question_text'])
                    score = st.radio(
                        label="",
                        options=[
                            "😫Never ever",  # -5
                            "🥺Barely or rarely",  # -4
                            "😏Sort of",  # +1
                            "🙂Moderately for sure",  # +3
                            "🤩Absolutely" # +5
                        ],
                        key=f"radio_{question['question_id']}"
                    )
                    submit_button = st.button("Submit", key=f"submit_{question['question_id']}")
                    if submit_button:
                        if score:
                            answered_questions += 1
                            if score == "😫Never ever":
                                score_value = -5
                            elif score == "🥺Barely or rarely":
                                score_value = -4
                            elif score == "😏Sort of":
                                score_value = +1
                            elif score == "🙂Moderately for sure":
                                score_value = +3
                            elif score == "🤩Absolutely":
                                score_value = +5
                            
                            # Insert data into Survey table
                            survey_data = {
                                "user_id": st.session_state['user_id'],
                                "completed_at": datetime.utcnow().isoformat(),
                                "survey_id": random.randint(1, 32767),  # Changed to fit within smallint range
                                "category_id": int(question['category_id'])
                            }
                            try:
                                supabase_client.table("Survey").insert(survey_data).execute()
                                st.success("Survey response submitted successfully!")
                            except Exception as e:
                                st.error(f"An error occurred while submitting the survey: {e}")
                            
                            # Insert data into SurveyResponse table
                            survey_response_data = {
                                "survey_id": survey_data["survey_id"],
                                "question_id": int(question['question_id']),
                                "score": score_value
                            }
                            try:
                                supabase_client.table("SurveyResponse").insert(survey_response_data).execute()
                                st.success("Survey response details submitted successfully!")
                                st.balloons()
                                # Remove the answered question from the list
                                survey_question_data = [q for q in survey_question_data if q['question_id'] != question['question_id']]
                                # Update progress bar
                                progress = answered_questions / total_questions
                            except Exception as e:
                                st.error(f"An error occurred while submitting the survey response details: {e}")
                        else:
                            st.error("Please select a score before submitting.")
    
    # Insert data into Supabase tables if not exists
    insert_data_if_not_exists("SurveyCategory", survey_category_data, "category_id")
    insert_data_if_not_exists("SurveyQuestion", survey_question_data, "question_id")