import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
import re

st.set_page_config(page_title="Transcript Tool", layout="centered")
st.title("YouTube Transcript Batch Tool")

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

urls_text = st.text_area("Paste YouTube URLs (one per line):", height=150)
urls = [u.strip() for u in urls_text.split('\n') if u.strip()]

if st.button("Process Batch"):
    if not urls:
        st.warning("Please add at least one URL.")
    else:
        results = []
        progress = st.progress(0)
        
        for i, url in enumerate(urls):
            vid = extract_video_id(url)
            if not vid:
                st.error(f"Invalid URL: {url}")
                continue
            
            try:
                # Stable call for version 0.6.1
                transcript_list = YouTubeTranscriptApi.get_transcript(vid)
                # Dictionary access is now safe because we pinned to 0.6.1
                text = " ".join([chunk['text'] for chunk in transcript_list])
                results.append({"URL": url, "Transcript": text})
                st.success(f"Processed: {vid}")
            except Exception as e:
                st.error(f"Failed {vid}: {str(e)}")
            
            progress.progress((i + 1) / len(urls))

        if results:
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "transcripts.csv", "text/csv")
