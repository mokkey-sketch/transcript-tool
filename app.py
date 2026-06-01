import streamlit as st
import pandas as pd
import sqlite3
import time

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect('pipeline.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS queue 
                    (url TEXT PRIMARY KEY, status TEXT, transcript TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- UI Layout ---
st.set_page_config(page_title="Production Pipeline", layout="wide")
st.title("🛡️ Autonomous Dashboard")

# Input Section
with st.sidebar:
    input_text = st.text_area("Add URLs (one per line):", height=200)
    if st.button("Add to Queue"):
        conn = sqlite3.connect('pipeline.db', check_same_thread=False)
        for url in input_text.split('\n'):
            if url.strip():
                conn.execute("INSERT OR IGNORE INTO queue VALUES (?, 'PENDING', '')", (url.strip(),))
        conn.commit()
        conn.close()
        st.rerun()

# Display Section
conn = sqlite3.connect('pipeline.db', check_same_thread=False)
df = pd.read_sql("SELECT * FROM queue", conn)
conn.close()

st.dataframe(df, use_container_width=True)

# Auto-Refresh Logic
time.sleep(5)
st.rerun()
