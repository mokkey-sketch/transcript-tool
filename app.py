import streamlit as st
import sys
import os

# Ensure the current directory is in the path
sys.path.append(os.getcwd())

try:
    from engine import process_transcript
    st.write("Engine loaded successfully!")
except Exception as e:
    st.error(f"Failed to load engine: {e}")
    st.stop()

# ... rest of your UI code ...
