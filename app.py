import streamlit as st
import pandas as pd
import sqlite3

# --- Initialize DB on startup (Before any other code) ---
def init_db():
    conn = sqlite3.connect('pipeline.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS queue 
                    (url TEXT PRIMARY KEY, status TEXT, transcript TEXT)''')
    conn.commit()
    conn.close()

# Run this once
init_db()

# --- Now your read_sql will work ---
def get_db():
    return sqlite3.connect('pipeline.db', check_same_thread=False)

st.title("🛡️ Dashboard")

# The rest of your UI code...
