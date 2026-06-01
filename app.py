import subprocess
import sys

# Force install the official library if it's missing or corrupted
subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api"])

import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
import re

st.title("YouTube Transcript Batch Tool")

urls_text = st.text_area("Paste your YouTube URLs (one per line)", height=150)
urls = [u.strip() for u in urls_text.split('\n') if u.strip()]

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

if st.button("Process Batch"):
    if not urls:
        st.warning("Please paste at least one URL.")
    else:
        results = []
        for url in urls:
            video_id = extract_video_id(url)
            if not video_id:
                st.error(f"Invalid URL: {url}")
                continue
            
            try:
                # Direct call to the library
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript = " ".join([t['text'] for t in transcript_list])
                results.append({"URL": url, "Transcript": transcript})
                st.success(f"Processed: {video_id}")
            except Exception as e:
                st.error(f"Error fetching {video_id}: {e}")
        
        if results:
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="transcripts.csv", mime="text/csv")
