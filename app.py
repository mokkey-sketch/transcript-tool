import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from io import BytesIO
import re

# Set page configuration
st.set_page_config(page_title="Batch Transcript Extractor", layout="wide")

# Persistent State Management
if 'results' not in st.session_state:
    st.session_state.results = []

st.title("🛡️ Stable Batch Transcript Extractor")

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        data = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([chunk['text'] for chunk in data])
    except Exception as e:
        return f"ERROR: {str(e)}"

# User input area
urls_text = st.text_area("Paste YouTube URLs (one per line):", height=150)

if st.button("Process Batch"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    st.session_state.results = [] # Clear previous results
    
    with st.spinner("Fetching transcripts..."):
        for url in urls:
            vid = extract_video_id(url)
            if vid:
                text = get_transcript(vid)
                st.session_state.results.append({"URL": url, "Transcript": text})
            else:
                st.session_state.results.append({"URL": url, "Transcript": "ERROR: Invalid URL"})
    st.rerun()

# Display Results from Memory
if st.session_state.results:
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)
    
    # Download logic using BytesIO (No file creation in repo)
    towrite = BytesIO()
    df.to_csv(towrite, index=False)
    towrite.seek(0)
    
    st.download_button(
        label="Download Results (CSV)",
        data=towrite,
        file_name="results.csv",
        mime="text/csv"
    )
