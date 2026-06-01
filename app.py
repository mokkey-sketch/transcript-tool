import streamlit as st
import pandas as pd
import time
import re
from io import BytesIO
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

# Set page configuration
st.set_page_config(page_title="Stable Transcript Batcher", layout="wide")
st.title("🛡️ Stable Transcript Batch Extractor")

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript_safe(video_id):
    """Fetches transcript with exponential backoff for 429 errors."""
    for attempt in range(4): # Try up to 4 times
        try:
            data = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([chunk['text'] for chunk in data])
        
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
            return f"FAILED: {type(e).__name__}"
        
        except Exception as e:
            if "429" in str(e):
                # Rate limited: wait longer each attempt
                time.sleep(10 * (attempt + 1))
            else:
                # Other errors: wait briefly and retry
                time.sleep(2)
    return "FAILED: Exhausted retries (429/Blocking)"

# UI Layout
urls_text = st.text_area("Paste YouTube URLs (one per line):", height=150)

if st.button("Start Batch Processing"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    results = []
    progress_bar = st.progress(0)
    
    with st.spinner("Processing in safe mode..."):
        for i, url in enumerate(urls):
            vid = extract_video_id(url)
            if vid:
                # Polite request spacing: 3 seconds per request
                time.sleep(3.0) 
                text = get_transcript_safe(vid)
                results.append({"URL": url, "Transcript": text})
            else:
                results.append({"URL": url, "Transcript": "ERROR: Invalid URL"})
            
            progress_bar.progress((i + 1) / len(urls))

    # Store in session state for display
    st.session_state.results = pd.DataFrame(results)
    st.rerun()

# Display Results
if 'results' in st.session_state:
    st.dataframe(st.session_state.results)
    
    # Download logic
    towrite = BytesIO()
    st.session_state.results.to_csv(towrite, index=False)
    towrite.seek(0)
    
    st.download_button(
        label="Download Results (CSV)",
        data=towrite,
        file_name="stable_results.csv",
        mime="text/csv"
    )
