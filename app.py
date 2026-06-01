import streamlit as st
import pandas as pd
import subprocess
import os
import shutil

# Ensure bun is installed
BUN_PATH = os.path.expanduser("~/.bun/bin/bun")

def install_bun():
    if not os.path.exists(BUN_PATH):
        st.info("Installing Bun runtime...")
        subprocess.run(["curl", "-fsSL", "https://bun.sh/install", "|", "bash"], shell=True)
    return os.path.exists(BUN_PATH)

st.title("YouTube Transcript Batch Tool")

# Check for bun on load
if not install_bun():
    st.error("Bun installation failed. Please check environment permissions.")

urls_text = st.text_area("Paste your YouTube URLs (one per line)", height=150)
urls = [u.strip() for u in urls_text.split('\n') if u.strip()]

def get_transcript_via_bun(url):
    # Call bun directly using the path
    result = subprocess.run(
        [BUN_PATH, "run", "src/cli.ts", "get", url],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        raise Exception(result.stderr.strip())

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
