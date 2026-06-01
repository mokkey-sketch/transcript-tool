import streamlit as st
import pandas as pd
import time
import random
import re
import json
import os
import shutil
from youtube_transcript_api import YouTubeTranscriptApi
from io import BytesIO

st.set_page_config(page_title="Autonomous Pipeline", layout="wide")
st.title("🚀 Autonomous Pipeline with Hard Reset")

STATE_FILE = "pipeline_state.json"

# --- Reset/Restart Logic ---
def hard_reset():
    """Wipes all state and restarts the app to a blank slate."""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- State Management ---
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                saved = json.load(f)
                st.session_state.batch_queue = saved.get("queue", [])
                st.session_state.queue_index = saved.get("index", 0)
        except: pass

if 'batch_queue' not in st.session_state:
    load_state()
    if 'batch_queue' not in st.session_state:
        st.session_state.batch_queue = []
        st.session_state.queue_index = 0

if 'results' not in st.session_state:
    st.session_state.results = pd.DataFrame(columns=["URL", "Status", "Transcript"])

# --- UI Sidebar ---
with st.sidebar:
    st.header("Pipeline Controls")
    input_text = st.text_area("Paste URLs:", height=150)
    if st.button("Load & Start Pipeline"):
        st.session_state.batch_queue = [u.strip() for u in input_text.split('\n') if u.strip()]
        st.session_state.queue_index = 0
        st.session_state.results = pd.DataFrame(columns=["URL", "Status", "Transcript"])
        st.rerun()
    
    st.divider()
    if st.button("🚨 HARD RESET (Wipe All)"):
        hard_reset()

# --- Execution Engine ---
batch_size = 5
remaining = len(st.session_state.batch_queue) - st.session_state.queue_index

if remaining > 0:
    st.info(f"Pipeline running: {st.session_state.queue_index} / {len(st.session_state.batch_queue)} processed.")
    
    # Process batch
    start = st.session_state.queue_index
    current_batch = st.session_state.batch_queue[start : start + batch_size]
    
    new_data = []
    for url in current_batch:
        vid = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        vid = vid.group(1) if vid else None
        
        # Safe Fetching
        try:
            time.sleep(8 + random.uniform(0, 4))
            data = YouTubeTranscriptApi.get_transcript(vid)
            text, status = " ".join([c['text'] for c in data]), "OK"
        except Exception as e:
            text, status = str(e), "FAILED"
            
        new_data.append({"URL": url, "Status": status, "Transcript": text})
    
    # Update state
    st.session_state.results = pd.concat([st.session_state.results, pd.DataFrame(new_data)], ignore_index=True)
    st.session_state.queue_index += len(current_batch)
    
    # Save State
    with open(STATE_FILE, "w") as f:
        json.dump({"queue": st.session_state.batch_queue, "index": st.session_state.queue_index}, f)
        
    st.rerun()

# --- Display ---
if not st.session_state.results.empty:
    st.dataframe(st.session_state.results)
