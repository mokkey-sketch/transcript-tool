import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from io import BytesIO
import re
import time

# Set page configuration
st.set_page_config(page_title="Production Transcript Tool", layout="wide")
st.title("🛡️ Production Transcript Batch Extractor")

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript_safe(video_id):
    """Fetches transcript and categorizes failures gracefully."""
    try:
        # Pinned to 0.6.1 dictionary-based logic
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([chunk['text'] for chunk in transcript_list])
    
    except (TranscriptsDisabled, NoTranscriptFound):
        return "ERROR: No transcript available (check if captions are enabled)"
    except VideoUnavailable:
        return "ERROR: Video is unavailable or private"
    except Exception as e:
        # Catches the 'no element found' XML errors and other issues
        return f"ERROR: {str(e)}"

# UI Layout
urls_text = st.text_area("Paste YouTube URLs (one per line):", height=150)

if st.button("Start Batch Processing"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, url in enumerate(urls):
        vid = extract_video_id(url)
        status_text.text(f"Processing ({i+1}/{len(urls)}): {vid if vid else 'Invalid'}")
        
        if not vid:
            results.append({"URL": url, "Transcript": "ERROR: Invalid URL"})
        else:
            # Throttling to prevent IP blocks/rate limiting
            time.sleep(1.2)
            transcript = get_transcript_safe(vid)
            results.append({"URL": url, "Transcript": transcript})
        
        progress_bar.progress((i + 1) / len(urls))

    status_text.text("Batch processing complete.")
    
    # Display results
    df = pd.DataFrame(results)
    st.dataframe(df)
    
    # Generate CSV in memory (no file creation in repo to avoid loops)
    towrite = BytesIO()
    df.to_csv(towrite, index=False)
    towrite.seek(0)
    
    st.download_button(
        label="Download All Results (CSV)",
        data=towrite,
        file_name="batch_results.csv",
        mime="text/csv"
    )
