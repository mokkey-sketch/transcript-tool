import streamlit as st
import pandas as pd
import subprocess
import time
from io import BytesIO

st.set_page_config(page_title="Bulletproof Transcript Tool", layout="wide")
st.title("🛡️ Bulletproof Transcript Batcher")

# --- 1. Core Extraction Engine (Using Bun CLI) ---
def get_transcript(url):
    """Calls your stable Bun CLI to get the transcript."""
    try:
        # Calls the specific CLI path you verified works
        result = subprocess.run(
            ["bun", "run", "ytranscript/src/cli.ts", "get", url],
            capture_output=True,
            text=True,
            timeout=30 # Add timeout to prevent hangs
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"ERROR: CLI Failed ({result.stderr.strip()})"
    except Exception as e:
        return f"ERROR: Execution failed: {str(e)}"

# --- 2. State & UI ---
if 'results' not in st.session_state:
    st.session_state.results = []

urls_text = st.text_area("Paste URLs (one per line):", height=150)

if st.button("Start Batch Processing"):
    urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
    st.session_state.results = [] # Clear state for new batch
    
    progress = st.progress(0)
    for i, url in enumerate(urls):
        st.write(f"Processing: {url}")
        
        # Throttling: The "Anti-429" layer
        time.sleep(2.5) 
        
        transcript = get_transcript(url)
        st.session_state.results.append({"URL": url, "Transcript": transcript})
        
        progress.progress((i + 1) / len(urls))
    st.rerun()

# --- 3. Memory-Safe Export ---
if st.session_state.results:
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)
    
    towrite = BytesIO()
    df.to_csv(towrite, index=False)
    towrite.seek(0)
    
    st.download_button("Download CSV", towrite, "stable_results.csv", "text/csv")
