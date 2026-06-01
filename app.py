import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(layout="wide")
st.title("🛡️ Dashboard")

# Add URLs to DB
input_text = st.text_area("Add URLs:")
if st.button("Add to Queue"):
    conn = sqlite3.connect('pipeline.db', check_same_thread=False)
    for url in input_text.split('\n'):
        if url.strip():
            conn.execute("INSERT OR IGNORE INTO queue VALUES (?, 'PENDING', '')", (url.strip(),))
    conn.commit()
    conn.close()
    st.rerun()

# Display current status
conn = sqlite3.connect('pipeline.db', check_same_thread=False)
df = pd.read_sql("SELECT * FROM queue", conn)
conn.close()
st.dataframe(df, use_container_width=True)

# Auto-refresh
time.sleep(5)
st.rerun()
