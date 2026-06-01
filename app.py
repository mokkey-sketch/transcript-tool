import streamlit as st
import pandas as pd
import sqlite3
import time
import random
import re
from youtube_transcript_api import YouTubeTranscriptApi
from io import BytesIO

# --- Database Setup ---
def get_db():
    conn = sqlite3.connect('pipeline.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS queue 
                    (url TEXT PRIMARY KEY, status TEXT, transcript TEXT)''')
    return conn

# --- Core Engine ---
def process_queue():
    conn = get_db()
    # Get unprocessed items
    pending = conn.execute("SELECT url FROM queue WHERE status = 'PENDING'").fetchall()
    
    for (url,) in pending:
        vid = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        vid = vid.group(1) if vid else None
        
        try:
            time.sleep(8 + random.uniform(0, 4)) # Strict Pacing
            data = YouTubeTranscriptApi.get_transcript(vid)
            text = " ".join([c['text'] for c in data])
            conn.execute("UPDATE queue SET status='OK', transcript=? WHERE url=?", (text, url))
        except Exception as e:
            conn.execute("UPDATE queue SET status=?, transcript=? WHERE url=?", ('FAILED', str(e), url))
        
        conn.commit()
    conn.close()

# --- UI ---
st.title("🚀 Production VM Pipeline")

with st.sidebar:
    input_text = st.text_area("Paste URLs (one per line):")
    if st.button("Add to Database"):
        conn = get_db()
        for url in input_text.split('\n'):
            if url.strip():
                conn.execute("INSERT OR IGNORE INTO queue VALUES (?, 'PENDING', '')", (url.strip(),))
        conn.commit()
        conn.close()
        st.rerun()

if st.button("Process Pending Queue"):
    with st.spinner("Processing..."):
        process_queue()
        st.success("Batch Complete!")
        st.rerun()

# --- Data View ---
conn = get_db()
df = pd.read_sql("SELECT * FROM queue", conn)
conn.close()

st.dataframe(df)

if not df.empty:
    towrite = BytesIO()
    df.to_csv(towrite, index=False)
    towrite.seek(0)
    st.download_button("Download Database Export", towrite, "results.csv", "text/csv")
