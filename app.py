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
        progress_bar = st.progress(0)
        
        for index, url in enumerate(urls):
            video_id = extract_video_id(url)
            if not video_id:
                st.error(f"Invalid URL: {url}")
                continue
            
            try:
                # Use the static method directly
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript = " ".join([t['text'] for t in transcript_list])
                results.append({"URL": url, "Transcript": transcript})
                st.success(f"Processed: {video_id}")
            except Exception as e:
                st.error(f"Could not fetch {url}: {e}")
            
            progress_bar.progress((index + 1) / len(urls))

        if results:
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download all transcripts as CSV",
                data=csv,
                file_name="transcripts.csv",
                mime="text/csv"
            )
