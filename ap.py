import streamlit as st
from engine import run_transcript_job

st.title("Disneyland® Parijs Transcript Tool")

sheet_id = st.text_input("Google Sheet ID")
source = st.text_input("Source Tab", "Form")
target = st.text_input("Target Tab", "Transcript results")

if st.button("Start Processing"):
    with st.spinner('Processing...'):
        try:
            status = run_transcript_job(sheet_id, source, target)
            st.success(status)
        except Exception as e:
            st.error(f"Error: {e}")