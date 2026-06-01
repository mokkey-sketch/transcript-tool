import streamlit as st
from engine import process_transcript

st.title("YouTube Transcript Tool")

sheet_id = st.text_input("Sheet ID")
source = st.text_input("Source Tab", "Form")
target = st.text_input("Target Tab", "Transcript results")

if st.button("Run"):
    if not sheet_id:
        st.error("Please enter a Sheet ID.")
    else:
        with st.spinner("Processing..."):
            try:
                # Call the correct function name here!
                status = process_transcript(sheet_id, source, target)
                st.success(status)
            except Exception as e:
                st.error(f"Error: {e}")
