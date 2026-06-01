import streamlit as st
import pandas as pd
import time
import random
from youtube_transcript_api import YouTubeTranscriptApi
from io import BytesIO
import re

st.set_page_config(page_title="Production Batch System", layout="wide")
st.title("🛡️ Production Batch System v2")

# --- Persistent Data Store ---
if 'batch_queue' not in st.session_state:
    st.session_state.batch_queue = []
if 'results' not in st.session_state:
    st.session_state.results = []

# --- Helper Functions ---
def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        # Added jitter to make requests look less automated
        time.sleep(random.uniform(5.0, 10.0)) 
        data = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([chunk['text'] for chunk in data])
    except Exception as e:
        return f"FAILED: {str(e)}"

# --- UI Interface ---
urls_text = st.text_area("Paste ALL URLs (one per line):", height=150)

if st.button("Initialize Batch"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    st.session_state.batch_queue = urls
    st.session_state.results = []
    st.rerun()

# --- Batch Processing Logic ---
if st.session_state.batch_queue:
    st.info(f"Remaining in queue: {len(st.session_state.batch_queue)}")
    
    # Process only 5 at a time to stay under YouTube's radar
    batch_size = 5
    current_batch = st.session_state.batch_queue[:batch_size]
    
    if st.button(f"Process Next {len(current_batch)} Videos"):
        for url in current_batch:
            vid = extract_video_id(url)
            text = get_transcript(vid) if vid else "INVALID_URL"
            st.session_state.results.append({"URL": url, "Transcript": text})
            st.session_state.batch_queue.remove(url)
        st.rerun()

# --- Display & Export ---
if st.session_state.results:
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)
    
    towrite = BytesIO()
    df.to_csv(towrite, index=False)
    towrite.seek(0)
    st.download_button("Download CSV", towrite, "results.csv", "text/csv")
