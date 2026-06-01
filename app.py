import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from io import BytesIO
import time
import re

# Set page configuration
st.set_page_config(page_title="Transcript Batch Tool", layout="wide")
st.title("YouTube Transcript Batch Tool")

# Function to extract ID reliably
def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# Fetch function with throttling
def get_transcript(video_id):
    try:
        # This replaces your 'bun run cli.ts' command
        data = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([chunk['text'] for chunk in data])
    except Exception as e:
        return f"ERROR: {str(e)}"

# UI Layout
urls_text = st.text_area("Paste URLs (one per line):", height=150)

if st.button("Start Batch Processing"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    results = []
    progress_bar = st.progress(0)
    
    with st.spinner("Processing..."):
        for i, url in enumerate(urls):
            vid = extract_video_id(url)
            if vid:
                # Throttling to prevent YouTube blocks
                time.sleep(1.0)
                text = get_transcript(vid)
                results.append({"URL": url, "Transcript": text})
            else:
                results.append({"URL": url, "Transcript": "ERROR: Invalid URL"})
            
            progress_bar.progress((i + 1) / len(urls))

    # Display results
    df = pd.DataFrame(results)
    st.dataframe(df)
    
    # Generate CSV in memory (no files created in repo)
    towrite = BytesIO()
    df.to_csv(towrite, index=False)
    towrite.seek(0)
    
    st.download_button("Download CSV", towrite, "results.csv", "text/csv")
