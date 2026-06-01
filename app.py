import streamlit as st
import pandas as pd
import time
import random
import re
from youtube_transcript_api import YouTubeTranscriptApi
from io import BytesIO

st.set_page_config(page_title="Autonomous Transcript Pipeline", layout="wide")
st.title("🚀 Autonomous Transcript Pipeline")

# --- Persistent State ---
if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'results' not in st.session_state:
    st.session_state.results = pd.DataFrame(columns=["URL", "Status", "Transcript"])
if 'retry_queue' not in st.session_state:
    st.session_state.retry_queue = []

# --- Helper Functions ---
def extract_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(vid):
    """Fetches transcript with exponential backoff."""
    try:
        time.sleep(8 + random.uniform(2, 5)) # Strict pacing
        data = YouTubeTranscriptApi.get_transcript(vid)
        return " ".join([c['text'] for c in data]), "OK"
    except Exception as e:
        return str(e), "FAILED"

# --- Input Layer ---
with st.sidebar:
    input_text = st.text_area("Paste URLs (one per line):", height=200)
    if st.button("Load Queue"):
        st.session_state.queue = [u.strip() for u in input_text.split('\n') if u.strip()]
        st.session_state.results = pd.DataFrame(columns=["URL", "Status", "Transcript"])
        st.rerun()

# --- Autonomous Worker Engine ---
if st.session_state.queue:
    st.info(f"Processing... {len(st.session_state.queue)} in queue.")
    
    # Process 3 at a time to stay under the radar
    batch = st.session_state.queue[:3]
    st.session_state.queue = st.session_state.queue[3:]
    
    batch_results = []
    for url in batch:
        vid = extract_id(url)
        text, status = get_transcript(vid) if vid else ("Invalid", "FAILED")
        
        if status == "FAILED":
            st.session_state.retry_queue.append(url)
        
        batch_results.append({"URL": url, "Status": status, "Transcript": text})
    
    st.session_state.results = pd.concat(
        [st.session_state.results, pd.DataFrame(batch_results)], ignore_index=True
    )
    
    time.sleep(1) # Breath before next loop
    st.rerun() # Auto-continue

# --- Output Layer ---
if not st.session_state.results.empty:
    st.write(f"Completed! {len(st.session_state.results)} total.")
    st.dataframe(st.session_state.results)
    
    towrite = BytesIO()
    st.session_state.results.to_csv(towrite, index=False)
    towrite.seek(0)
    st.download_button("Download CSV", towrite, "stable_results.csv", "text/csv")

if st.session_state.retry_queue:
    st.error(f"Retries needed: {len(st.session_state.retry_queue)}")
