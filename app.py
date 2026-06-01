import streamlit as st
import pandas as pd
import sqlite3

def get_db():
    return sqlite3.connect('pipeline.db', check_same_thread=False)

st.title("🛡️ Dashboard")

with st.sidebar:
    input_text = st.text_area("Add URLs:")
    if st.button("Add to Queue"):
        conn = get_db()
        for url in input_text.split('\n'):
            if url.strip():
                conn.execute("INSERT OR IGNORE INTO queue VALUES (?, 'PENDING', '')", (url.strip(),))
        conn.commit()
        conn.close()
        st.rerun()

# View Data
conn = get_db()
df = pd.read_sql("SELECT * FROM queue", conn)
conn.close()
st.dataframe(df)
