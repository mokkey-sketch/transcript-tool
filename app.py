import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import time
import re
from io import BytesIO

st.set_page_config(page_title="Production Batch Pipeline", layout="wide")
st.title("🚀 Production Batch Transcript Pipeline")

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def fetch_with_retry(video_id, retries=2):
    """Fetches transcript with exponential backoff and retries."""
    for attempt in range(retries):
        try:
            # Pinned stable dictionary-based fetch
            data = YouTubeTranscriptApi.get_transcript(video_id)
            if not data:
                return "EMPTY_RESPONSE_FROM_YOUTUBE"
            return " ".join([chunk['text'] for chunk in data])
        
        except (TranscriptsDisabled, NoTranscriptFound):
            return "NO_TRANSCRIPT_AVAILABLE"
        except VideoUnavailable:
            return "VIDEO_UNAVAILABLE"
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)  # Backoff delay
                continue
            return f"ERROR: {str(e)}"
    return "FAILED_AFTER_RETRIES"

# UI Logic
urls_text = st.text_area("Paste URLs (one per line):", height=150)

if st.button("Start Production Batch"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    results = []
    progress_bar = st.progress(0)
    
    for i, url in enumerate(urls):
        vid = extract_video_id(url)
        if not vid:
            results.append({"URL": url, "Transcript": "INVALID_URL"})
        else:
            # Throttling: prevent rate-limiting by sleeping between requests
            time.sleep(1.5) 
            text = fetch_with_retry(vid)
            results.append({"URL": url, "Transcript": text})
            
        progress_bar.progress((i + 1) / len(urls))

    st.session_state.final_df = pd.DataFrame(results)
    st.rerun()

# Output Layer
if 'final_df' in st.session_state:
    st.dataframe(st.session_state.final_df)
    towrite = BytesIO()
    st.session_state.final_df.to_csv(towrite, index=False)
    towrite.seek(0)
    st.download_button("Download Batch Results", towrite, "batch_results.csv", "text/csv")
