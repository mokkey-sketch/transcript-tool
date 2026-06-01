import streamlit as st
import pandas as pd
import time
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from io import BytesIO

st.set_page_config(page_title="Production Transcript Tool", layout="wide")
st.title("🛡️ Production Transcript Batch Extractor")

def extract_video_id(url):
    import re
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript_safe(video_id):
    try:
        data = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([chunk['text'] for chunk in data])
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        return f"FAILED: {type(e).__name__}"
    except Exception as e:
        return f"FAILED: {str(e)}"

urls_text = st.text_area("Paste YouTube URLs (one per line):", height=150)

if st.button("Start Batch Processing"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    results = []
    
    with st.spinner("Processing..."):
        for url in urls:
            vid = extract_video_id(url)
            if vid:
                time.sleep(2.0) # Throttling
                text = get_transcript_safe(vid)
                results.append({"URL": url, "Transcript": text})
            else:
                results.append({"URL": url, "Transcript": "ERROR: Invalid URL"})
    
    st.session_state.results = pd.DataFrame(results)
    st.rerun()

if 'results' in st.session_state:
    st.dataframe(st.session_state.results)
    
    # Corrected CSV download logic
    towrite = BytesIO()
    st.session_state.results.to_csv(towrite, index=False)
    towrite.seek(0)
    
    # CORRECT: st.download_button is a Streamlit function, not a BytesIO method
    st.download_button(
        label="Download Results (CSV)",
        data=towrite,
        file_name="results.csv",
        mime="text/csv"
    )
