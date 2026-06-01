import streamlit as st
import pandas as pd
import subprocess
import os

st.title("YouTube Transcript Batch Tool")

urls_text = st.text_area("Paste your YouTube URLs (one per line)", height=150)
urls = [u.strip() for u in urls_text.split('\n') if u.strip()]

def get_transcript_via_bun(url):
    # This is the standard install path for bun on Linux
    bun_path = os.path.expanduser("~/.bun/bin/bun")
    
    # We pass the full path to the bun executable
    result = subprocess.run(
        [bun_path, "run", "src/cli.ts", "get", url],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        # If it fails, return the error message for debugging
        raise Exception(f"Bun error: {result.stderr}")

if st.button("Process Batch"):
    if not urls:
        st.warning("Please paste at least one URL.")
    else:
        results = []
        for url in urls:
            try:
                transcript = get_transcript_via_bun(url)
                results.append({"URL": url, "Transcript": transcript})
                st.success(f"Processed: {url}")
            except Exception as e:
                st.error(f"Could not fetch {url}: {e}")
        
        if results:
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="transcripts.csv", mime="text/csv")
