import streamlit as st
import pandas as pd
import io
# Use the library we identified earlier instead of bun
from youtube_transcript_api import YouTubeTranscriptApi 

st.title("YouTube Transcript Tool")

# 1. Simple Input
urls_text = st.text_area("Paste your YouTube URLs (one per line)")
urls = [u.strip() for u in urls_text.split('\n') if u.strip()]

if st.button("Get Transcripts"):
    results = []
    
    # 2. Processing
    for url in urls:
        try:
            # Assuming you use a utility to get video ID
            video_id = url.split("v=")[-1] 
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([t['text'] for t in transcript_list])
            results.append({"URL": url, "Transcript": transcript})
            st.write(f"✓ Fetched: {url}")
        except Exception as e:
            st.error(f"Error on {url}: {e}")

    # 3. Direct Download
    if results:
        df = pd.DataFrame(results)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="transcripts.csv")
