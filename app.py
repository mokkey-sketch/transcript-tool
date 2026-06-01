import streamlit as st
import pandas as pd
import time
import random
import re
from youtube_transcript_api import YouTubeTranscriptApi
from io import BytesIO

st.set_page_config(page_title="Autonomous Batch Processor", layout="wide")
st.title("🚀 Autonomous Transcript Pipeline")

# --- Initialize State ---
if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'results' not in st.session_state:
    st.session_state.results = pd.DataFrame(columns=["URL", "Status", "Transcript"])

# --- Helper Functions ---
def extract_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript_safe(video_id, attempt=0):
    """Exponential backoff with jitter."""
    try:
        # Pacing: 8-15s per request to avoid IP blocking
        time.sleep(8 + (attempt * 2) + random.uniform(0, 3))
        data = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([c['text'] for c in data]), "OK"
    except Exception as e:
        if "429" in str(e) and attempt < 3:
            return get_transcript_safe(video_id, attempt + 1)
        return str(e), "FAILED"

# --- Input Layer ---
with st.sidebar:
    urls_input = st.text_area("Paste URLs (one per line):", height=200)
    if st.button("Load Queue"):
        st.session_state.queue = [u.strip() for u in urls_input.split('\n') if u.strip()]
        st.session_state.results = pd.DataFrame(columns=["URL", "Status", "Transcript"])
        st.rerun()

# --- Autonomous Engine ---
if st.session_state.queue:
    st.warning(f"Processing... {len(st.session_state.queue)} items remaining.")
    
    # Process batch of 5
    batch = st.session_state.queue[:5]
    st.session_state.queue = st.session_state.queue[5:] # FIFO slice
    
    new_rows = []
    for url in batch:
        vid = extract_id(url)
        text, status = get_transcript_safe(vid) if vid else ("Invalid ID", "FAILED")
        new_rows.append({"URL": url, "Status": status, "Transcript": text})
    
    # Merge results
    df_new = pd.DataFrame(new_rows)
    st.session_state.results = pd.concat([st.session_state.results, df_new], ignore_index=True)
    
    # Auto-rerun to keep the conveyor belt moving
    time.sleep(1)
    st.rerun()

# --- Output Layer ---
if not st.session_state.results.empty:
    st.success("Batch completed!")
    st.dataframe(st.session_state.results)
    
    towrite = BytesIO()
    st.session_state.results.to_csv(towrite, index=False)
    towrite.seek(0)
    st.download_button("Download CSV", towrite, "batch_results.csv", "text/csv")
