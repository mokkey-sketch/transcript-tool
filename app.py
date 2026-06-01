import streamlit as st
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.getcwd())

# 1. Attempt to import the function
try:
    from engine import process_transcript
    st.success("Engine loaded successfully!")
except Exception as e:
    st.error(f"Failed to load engine: {e}")
    st.stop()

# 2. Render the UI ONLY if the import succeeded
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
                status = process_transcript(sheet_id, source, target)
                st.success(status)
            except Exception as e:
                st.error(f"Error during execution: {e}")
