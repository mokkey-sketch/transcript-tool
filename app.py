import streamlit as st
import pandas as pd
import sqlite3

# --- 1. Database Initialization (Only runs once) ---
def init_db():
    conn = sqlite3.connect('pipeline.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS queue 
                    (url TEXT PRIMARY KEY, status TEXT, transcript TEXT)''')
    conn.commit()
    conn.close()

init_db() # Call this ONCE at the top

# --- 2. Database Helpers ---
def add_urls_to_db(urls):
    conn = sqlite3.connect('pipeline.db', check_same_thread=False)
    for url in urls:
        if url.strip():
            conn.execute("INSERT OR IGNORE INTO queue VALUES (?, 'PENDING', '')", (url.strip(),))
    conn.commit()
    conn.close()

# --- 3. UI Layer ---
st.title("🛡️ Dashboard")

input_text = st.text_area("Add URLs (one per line):")

if st.button("Add to Queue"):
    urls = input_text.split('\n')
    add_urls_to_db(urls)
    st.success(f"Added {len(urls)} URLs to database.")
    st.rerun()

# --- 4. Data View ---
conn = sqlite3.connect('pipeline.db', check_same_thread=False)
df = pd.read_sql("SELECT * FROM queue", conn)
conn.close()

st.dataframe(df)
