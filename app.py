import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import time
import re
from io import BytesIO

# Set page configuration
st.set_page_config(page_title="Batch Transcript Extractor", layout="wide")
st.title("🛡️ Production Transcript Batch Pipeline")

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def fetch_with_retry(video_id, retries=3):
    """Fetches transcript with delays to avoid 429 rate-limiting."""
    for attempt in range(retries):
        try:
            # Pinned stable dictionary-based fetch
            data = YouTubeTranscriptApi.get_transcript(video_id)
            if not data:
                return "EMPTY_RESPONSE"
            return " ".join([chunk['text'] for chunk in data])
        
        except (TranscriptsDisabled, NoTranscriptFound):
            return "NO_TRANSCRIPT_AVAILABLE"
        except Exception as e:
            # If we hit 429 (Too Many Requests), wait longer before retrying
            if "429" in str(e):
                time.sleep(5)  # Wait 5 seconds if rate-limited
            else:
                time.sleep(2)  # Standard retry delay
            if attempt == retries - 1:
                return f"ERROR: {str(e)}"
    return "FAILED_AFTER_RETRIES"

# UI Logic
urls_text = st.text_area("Paste URLs (one per line):", height=150)

if st.button("Start Batch Processing"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    results = []
    progress_bar = st.progress(0)
    
    with st.spinner("Processing batch..."):
        for i, url in enumerate(urls):
            vid = extract_video_id(url)
            if not vid:
                results.append({"URL": url, "Transcript": "INVALID_URL"})
            else:
                # IMPORTANT: Throttle between every single request
                time.sleep(2.0) 
                text = fetch_with_retry(vid)
                results.append({"URL": url, "Transcript": text})
            
            progress_bar.progress((i + 1) / len(urls))

    # Output Layer
    df = pd.DataFrame(results)
    st.dataframe(df)
    
    towrite = BytesIO()
    df.to_csv(towrite, index=False)
    towrite.seek(0)
    st.download_button("Download Batch CSV", towrite, "results.csv", "text/csv")
