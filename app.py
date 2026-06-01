import streamlit as st
import pandas as pd
import subprocess
import re

st.title("YouTube Transcript Batch Tool")

urls_text = st.text_area("Paste your YouTube URLs (one per line)", height=150)
urls = [u.strip() for u in urls_text.split('\n') if u.strip()]

def get_transcript_via_bun(url):
    # This calls the command that you know works in your Colab
    result = subprocess.run(
        ["bun", "run", "src/cli.ts", "get", url],
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
        progress_bar = st.progress(0)
        
        for index, url in enumerate(urls):
            try:
                transcript = get_transcript_via_bun(url)
                results.append({"URL": url, "Transcript": transcript})
                st.success(f"Processed: {url}")
            except Exception as e:
                st.error(f"Could not fetch {url}: {e}")
            
            progress_bar.progress((index + 1) / len(urls))

        if results:
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download all transcripts as CSV",
                data=csv,
                file_name="transcripts.csv",
                mime="text/csv"
            )
