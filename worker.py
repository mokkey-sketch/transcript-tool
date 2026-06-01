import sqlite3
import time
import re
from youtube_transcript_api import YouTubeTranscriptApi

def get_db():
    return sqlite3.connect('pipeline.db', check_same_thread=False)

def process_worker():
    print("Worker started...")
    while True:
        conn = get_db()
        # Atomic lock: process only one batch at a time
        pending = conn.execute("SELECT url FROM queue WHERE status='PENDING' LIMIT 5").fetchall()
        
        if pending:
            for (url,) in pending:
                vid = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
                vid = vid.group(1) if vid else None
                
                try:
                    time.sleep(10) # Heavy throttling
                    data = YouTubeTranscriptApi.get_transcript(vid)
                    text = " ".join([c['text'] for c in data])
                    conn.execute("UPDATE queue SET status='OK', transcript=? WHERE url=?", (text, url))
                except Exception as e:
                    conn.execute("UPDATE queue SET status='FAILED', transcript=? WHERE url=?", (str(e), url))
                conn.commit()
        
        conn.close()
        time.sleep(5) # Idle time

if __name__ == "__main__":
    process_worker()
