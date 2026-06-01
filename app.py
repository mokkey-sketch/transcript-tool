import streamlit as st
import importlib.util
import sys
import os

# Define the file path manually
file_path = os.path.join(os.path.dirname(__file__), "engine.py")

# Dynamically load the module
spec = importlib.util.spec_from_file_location("engine", file_path)
engine = importlib.util.module_from_spec(spec)
sys.modules["engine"] = engine
spec.loader.exec_module(engine)

# Access the function
run_transcript_job = engine.run_transcript_job

st.title("Transcript Tool")

sheet_id = st.text_input("Google Sheet ID")
source = st.text_input("Source Tab", "Form")
target = st.text_input("Target Tab", "Transcript results")

if st.button("Start Processing"):
    if not sheet_id:
        st.error("Please enter a Google Sheet ID.")
    else:
        with st.spinner('Processing...'):
            try:
                status = run_transcript_job(sheet_id, source, target)
                st.success(status)
            except Exception as e:
                st.error(f"Error: {e}")
