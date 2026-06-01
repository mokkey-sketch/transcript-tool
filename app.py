import streamlit as st
import pandas as pd
import time
from youtube_transcript_api import YouTubeTranscriptApi
from io import BytesIO

st.set_page_config(page_title="Production Transcript Tool", layout="wide")
st.title("🛡️ Production Transcript Batch Extractor")

def extract_video_id(url):
    # Regex for video ID
    import re
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def fetch_transcript(video_id):
    """Fetches transcript with exponential backoff to avoid 429 errors."""
    for attempt in range(3):
        try:
            data = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([chunk['text'] for chunk in data])
        except Exception as e:
            if "429" in str(e):
                time.sleep(10 * (attempt + 1)) # Wait longer on rate limit
            else:
                time.sleep(2) # Standard wait
    return "FAILED: Could not retrieve transcript"

# UI Logic
urls_text = st.text_area("Paste YouTube URLs (one per line):", height=150)

if st.button("Start Batch Processing"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    results = []
    
    with st.spinner("Processing in safe mode..."):
        for url in urls:
            vid = extract_video_id(url)
            if vid:
                # Polite request spacing
                time.sleep(2.5) 
                text = fetch_transcript(vid)
                results.append({"URL": url, "Transcript": text})
            else:
                results.append({"URL": url, "Transcript": "INVALID_URL"})
            
    st.session_state.results = pd.DataFrame(results)
    st.rerun()

# Output
if 'results' in st.session_state:
    st.dataframe(st.session_state.results)
    towrite = BytesIO()
    st.session_state.results.to_csv(towrite, index=False)
    towrite.download_button("Download CSV", towrite, "results.csv", "text/csv")
