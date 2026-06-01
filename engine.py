import subprocess
import textwrap
import gspread
from google.oauth2.service_account import Credentials
import json
import streamlit as st

def get_gc():
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds_dict = json.loads(st.secrets["GCP_CREDENTIALS"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

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
