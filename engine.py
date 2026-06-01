import textwrap
import gspread
from google.oauth2.service_account import Credentials
import json
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re

def get_gc():
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds_dict = json.loads(st.secrets["GCP_CREDENTIALS"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

def extract_video_id(url):
    # Regex to extract video ID from various YouTube URL formats
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def process_transcript(sheet_id, source_tab, target_tab):
    gc = get_gc()
    sh = gc.open_by_key(sheet_id)
    source_ws = sh.worksheet(source_tab)
    target_ws = sh.worksheet(target_tab)
    
    rows = source_ws.get_all_values()
    write_row = 2
    
    for i in range(1, len(rows)):
        url = rows[i][1]
        video_id = extract_video_id(url)
        
        if not video_id:
            continue
            
        try:
            # Fetch transcript using the native Python library
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([t['text'] for t in transcript_list])
            
            chunks = textwrap.wrap(transcript, width=45000)
            for chunk in chunks:
                target_ws.update_cell(write_row, 1, url)
                target_ws.update_cell(write_row, 2, chunk)
                write_row += 1
        except Exception as e:
            print(f"Could not fetch transcript for {url}: {e}")
            continue
            
    return "Done!"
