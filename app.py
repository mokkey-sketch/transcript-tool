import streamlit as st
import pandas as pd
import sqlite3
import time
import random
import re
from youtube_transcript_api import YouTubeTranscriptApi
from io import BytesIO

# --- 1. Database Initialization ---
def init_db():
    conn = sqlite3.connect('pipeline.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS queue 
                    (url TEXT PRIMARY KEY, status TEXT, transcript TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. Processing Engine ---
def process_queue():
    conn = sqlite3.connect('pipeline.db', check_same_thread=False)
    pending = conn.execute("SELECT url FROM queue WHERE status = 'PENDING'").fetchall()
    
    for (url,) in pending:
        vid = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        vid = vid.group(1) if vid else None
        
        try:
            # Polite pacing to avoid YouTube 429 errors
            time.sleep(8 + random.uniform(0, 4))
            data = YouTubeTranscriptApi.get_transcript(vid)
            text = " ".join([c['text'] for c in data])
            conn.execute("UPDATE queue SET status='OK', transcript=? WHERE url=?", (text, url))
        except Exception as e:
            conn.execute("UPDATE queue SET status='FAILED', transcript=? WHERE url=?", (str(e), url))
        
        conn.commit()
    conn.close()

# --- 3. UI Layer ---
st.set_page_config(page_title="Production Pipeline", layout="wide")
st.title("🛡️ Dashboard")

with st.sidebar:
    input_text = st.text_area("Add URLs (one per line):")
    if st.button("Add to Queue"):
        conn = sqlite3.connect('pipeline.db', check_same_thread=False)
        for url in input_text.split('\n'):
            if url.strip():
                conn.execute("INSERT OR IGNORE INTO queue VALUES (?, 'PENDING', '')", (url.strip(),))
        conn.commit()
        conn.close()
        st.rerun()

if st.button("Process Pending Queue"):
    with st.spinner("Processing in background..."):
        process_queue()
        st.success("Batch processing complete!")
        st.rerun()

# --- 4. Data View & Export ---
conn = sqlite3.connect('pipeline.db', check_same_thread=False)
df = pd.read_sql("SELECT * FROM queue", conn)
conn.close()

st.dataframe(df, use_container_width=True)

if not df.empty:
    towrite = BytesIO()
    df.to_csv(towrite, index=False)
    towrite.seek(0)
    st.download_button("Download CSV", towrite, "results.csv", "text/csv")
