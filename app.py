import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import os

# --- Configuration & Setup ---
st.set_page_config(page_title="Batch Transcript System", layout="wide")

# Persistent storage for progress
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = []
if 'urls_to_process' not in st.session_state:
    st.session_state.urls_to_process = []

st.title("🛡️ Restart-Proof Batch Transcript Extractor")

# --- System Controls Panel ---
with st.sidebar:
    st.subheader("System Controls")
    if st.button("🔄 Hard Reset App"):
        os._exit(0) # Forces container restart
    if st.button("🗑️ Clear All Progress"):
        st.session_state.processed_data = []
        st.session_state.urls_to_process = []
        st.rerun()

# --- Batch Logic ---
urls_text = st.text_area("Paste URLs (one per line):", height=150)

if st.button("Start/Resume Batch"):
    new_urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    st.session_state.urls_to_process = new_urls

def get_transcript_safe(video_id):
    try:
        # Pinned to 0.6.1 dictionary logic
        data = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([chunk['text'] for chunk in data])
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- Execution ---
if st.session_state.urls_to_process:
    total = len(st.session_state.urls_to_process)
    progress_bar = st.progress(0)
    
    for i, url in enumerate(st.session_state.urls_to_process):
        # Skip if already processed (Resume Capability)
        if any(d['URL'] == url for d in st.session_state.processed_data):
            continue
            
        vid = url.split("v=")[-1].split("&")[0] # Simple ID extraction
        transcript = get_transcript_safe(vid)
        
        st.session_state.processed_data.append({"URL": url, "Transcript": transcript})
        progress_bar.progress((i + 1) / total)

# --- Output ---
if st.session_state.processed_data:
    df = pd.DataFrame(st.session_state.processed_data)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results", csv, "batch_results.csv", "text/csv")
