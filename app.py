import streamlit as st
import pandas as pd
import time
import random
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from io import BytesIO

st.set_page_config(page_title="Stable Transcript Batcher", layout="wide")
st.title("🛡️ Stable Transcript Batch Extractor")

# --- Persistent State Management ---
if 'batch_queue' not in st.session_state:
    st.session_state.batch_queue = []
if 'results' not in st.session_state:
    st.session_state.results = pd.DataFrame(columns=["URL", "Transcript"])

# --- Core Functions ---
def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript_safe(video_id):
    try:
        # Polite delay to prevent 429 errors
        time.sleep(random.uniform(3.0, 6.0))
        data = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([chunk['text'] for chunk in data])
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        return f"FAILED: {type(e).__name__}"
    except Exception as e:
        return f"FAILED: {str(e)}"

# --- UI Layout ---
urls_text = st.text_area("Paste ALL URLs (one per line):", height=150)

if st.button("Initialize Batch"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    st.session_state.batch_queue = urls
    st.session_state.results = pd.DataFrame(columns=["URL", "Transcript"])
    st.rerun()

# --- Batch Processing Logic ---
if st.session_state.batch_queue:
    st.write(f"Remaining in queue: {len(st.session_state.batch_queue)}")
    
    # Process 5 videos per click to avoid rate limits
    batch_size = 5
    current_batch = st.session_state.batch_queue[:batch_size]
    
    if st.button(f"Process Next {len(current_batch)} Videos"):
        new_data = []
        for url in current_batch:
            vid = extract_video_id(url)
            text = get_transcript_safe(vid) if vid else "INVALID_URL"
            new_data.append({"URL": url, "Transcript": text})
            st.session_state.batch_queue.remove(url)
        
        # Append to results DataFrame
        df_new = pd.DataFrame(new_data)
        st.session_state.results = pd.concat([st.session_state.results, df_new], ignore_index=True)
        st.rerun()

# --- Display & Export ---
if not st.session_state.results.empty:
    st.dataframe(st.session_state.results)
    
    towrite = BytesIO()
    st.session_state.results.to_csv(towrite, index=False)
    towrite.seek(0)
    
    st.download_button(
        label="Download Results (CSV)",
        data=towrite,
        file_name="results.csv",
        mime="text/csv"
    )
