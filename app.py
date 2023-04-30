import streamlit as st
import pandas as pd
from src.pd_functions import *

# Path to results
RESULTS_PATH = 'data/results.csv'

def main():
    # Get participant name
    participant_name = get_participant_name()

    # Handle file upload
    if participant_name:
        uploaded_file = st.file_uploader("Choose a file")
        process_file_upload(uploaded_file, participant_name)

    # Show leaderboard
    try:
        show_leaderboard()
    except:
        st.write("There are no submissions yet.")

def get_participant_name():
    text_input_container = st.empty()
    text_input_container.text_input("Introduce participant name: ", key="text_input")

    if st.session_state.text_input != "":
        text_input_container.empty()
        st.info(f'Participant name {st.session_state.text_input}')
        return st.session_state.text_input

    return None

def process_file_upload(uploaded_file, participant_name):
    if uploaded_file is not None:
        try:
            test = get_ready_test(RESULTS_PATH, uploaded_file)
            participant_results = get_metrics(RESULTS_PATH, test)

            st.success('Dataframe uploaded successfully!')

            display_participant_results(participant_results)

            update_submissions(participant_results)

        except Exception as e:
            st.error(f"The file has a wrong format, please, review it and load it again. {str(e)}")

def display_participant_results(participant_results):
    st.title('Participant results')
    st.dataframe(participant_results)

if __name__ == "__main__":
    main()
