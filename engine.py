import streamlit as st
import subprocess
import textwrap
import gspread
from google.oauth2.service_account import Credentials

# --- 1. SETUP (Service Account) ---
# You will upload your 'credentials.json' to the same folder as app.py
def get_gc():
    creds = Credentials.from_service_account_file("credentials.json")
    return gspread.authorize(creds)

# --- 2. THE ENGINE ---
def process_transcript(sheet_id, source_tab, target_tab):
    gc = get_gc()
    sh = gc.open_by_key(sheet_id)
    source_ws = sh.worksheet(source_tab)
    target_ws = sh.worksheet(target_tab)
    
    rows = source_ws.get_all_values()
    write_row = 2
    
    for i in range(1, len(rows)):
        url = rows[i][1]
        if not url or "youtube" not in url: continue
        
        # Note: We assume bun is installed in the system environment
        result = subprocess.run(
            ["bun", "run", "ytranscript/src/cli.ts", "get", url],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            transcript = result.stdout.strip()
            chunks = textwrap.wrap(transcript, width=45000)
            for chunk in chunks:
                target_ws.update_cell(write_row, 1, url)
                target_ws.update_cell(write_row, 2, chunk)
                write_row += 1
    return "Done!"

# --- 3. THE UI ---
st.title("YouTube Transcript Tool")
sheet_id = st.text_input("Sheet ID")
source = st.text_input("Source Tab", "Form")
target = st.text_input("Target Tab", "Transcript results")

if st.button("Run"):
    with st.spinner("Processing..."):
        result = process_transcript(sheet_id, source, target)
        st.success(result)