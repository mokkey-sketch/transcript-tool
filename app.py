import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import re

st.set_page_config(page_title="Batch Transcript Tool", layout="wide")
st.title("YouTube Transcript Batch Extractor")

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript_safe(video_id):
    """Fetches transcript or returns a descriptive error state."""
    try:
        # Pinned to 0.6.1 logic
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([chunk['text'] for chunk in transcript_list])
    except (TranscriptsDisabled, NoTranscriptFound):
        return "ERROR: Transcripts disabled or not found"
    except VideoUnavailable:
        return "ERROR: Video unavailable"
    except Exception as e:
        return f"ERROR: {str(e)}"

urls_text = st.text_area("Paste URLs (one per line):", height=150)
urls = [u.strip() for u in urls_text.split('\n') if u.strip()]

if st.button("Start Batch Processing"):
    if not urls:
        st.warning("Please add at least one URL.")
    else:
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, url in enumerate(urls):
            vid = extract_video_id(url)
            status_text.text(f"Processing ({i+1}/{len(urls)}): {url}")
            
            if not vid:
                results.append({"URL": url, "Transcript": "ERROR: Invalid URL"})
            else:
                transcript = get_transcript_safe(vid)
                results.append({"URL": url, "Transcript": transcript})
            
            progress_bar.progress((i + 1) / len(urls))

        status_text.text("Batch processing complete.")
        
        # Display results and allow download
        df = pd.DataFrame(results)
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download All Results (CSV)", csv, "batch_transcripts.csv", "text/csv")
