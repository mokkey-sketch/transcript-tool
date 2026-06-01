import sqlite3
import time
import random
import re
from youtube_transcript_api import YouTubeTranscriptApi

def get_db():
    # Connect to the shared database
    return sqlite3.connect('pipeline.db', check_same_thread=False)

def process_worker():
    print("Worker engine initialized. Waiting for URLs...")
    while True:
        conn = get_db()
        # Fetch up to 5 pending items
        pending = conn.execute("SELECT url FROM queue WHERE status='PENDING' LIMIT 5").fetchall()
        
        for (url,) in pending:
            vid = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
            vid = vid.group(1) if vid else None
            
            try:
                # Polite pacing to avoid YouTube 429 errors
                time.sleep(random.uniform(5, 10))
                data = YouTubeTranscriptApi.get_transcript(vid)
                text = " ".join([c['text'] for c in data])
                conn.execute("UPDATE queue SET status='OK', transcript=? WHERE url=?", (text, url))
            except Exception as e:
                conn.execute("UPDATE queue SET status='FAILED', transcript=? WHERE url=?", (str(e), url))
            
            conn.commit()
            print(f"Processed: {url}")
        
        conn.close()
        time.sleep(5)

if __name__ == "__main__":
    process_worker()
