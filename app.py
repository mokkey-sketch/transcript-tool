import streamlit as st
import pandas as pd
import time
import random
import re
from youtube_transcript_api import YouTubeTranscriptApi
from io import BytesIO

st.set_page_config(page_title="Transcript Pipeline", layout="wide")
st.title("🛡️ Deterministic Transcript Pipeline")

# --- Persistent State ---
if 'batch_queue' not in st.session_state:
    st.session_state.batch_queue = []
if 'queue_index' not in st.session_state:
    st.session_state.queue_index = 0
if 'results' not in st.session_state:
    st.session_state.results = pd.DataFrame(columns=["URL", "Status", "Transcript"])

# --- Core Logic ---
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript_safe(vid):
    """Paced fetch with retry logic."""
    try:
        # Stronger pacing for production stability
        time.sleep(8 + random.uniform(0, 4)) 
        data = YouTubeTranscriptApi.get_transcript(vid)
        return " ".join([c['text'] for c in data]), "OK"
    except Exception as e:
        return str(e), "FAILED"

# --- Sidebar Input ---
with st.sidebar:
    input_text = st.text_area("Paste URLs:", height=200)
    if st.button("Load & Reset Queue"):
        st.session_state.batch_queue = [u.strip() for u in input_text.split('\n') if u.strip()]
        st.session_state.queue_index = 0
        st.session_state.results = pd.DataFrame(columns=["URL", "Status", "Transcript"])
        st.rerun()

# --- Batch Processing Engine ---
batch_size = 5
remaining = len(st.session_state.batch_queue) - st.session_state.queue_index

if remaining > 0:
    st.info(f"Progress: {st.session_state.queue_index} / {len(st.session_state.batch_queue)} processed.")
    
    if st.button(f"Process Next {min(batch_size, remaining)} Videos"):
        start = st.session_state.queue_index
        end = start + batch_size
        current_batch = st.session_state.batch_queue[start:end]
        
        new_data = []
        for url in current_batch:
            vid = extract_video_id(url)
            text, status = get_transcript_safe(vid) if vid else ("Invalid", "FAILED")
            new_data.append({"URL": url, "Status": status, "Transcript": text})
            
        st.session_state.results = pd.concat([st.session_state.results, pd.DataFrame(new_data)], ignore_index=True)
        st.session_state.queue_index += batch_size
        st.rerun()
else:
    st.success("All videos processed!")

# --- Output Layer ---
if not st.session_state.results.empty:
    st.dataframe(st.session_state.results)
    towrite = BytesIO()
    st.session_state.results.to_csv(towrite, index=False)
    towrite.seek(0)
    st.download_button("Download CSV", towrite, "stable_results.csv", "text/csv")
