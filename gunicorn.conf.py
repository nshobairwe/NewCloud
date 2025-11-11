# gunicorn.conf.py
import os
import threading
from app import background_ping_job  # ← This now works!

workers = 1
worker_class = 'sync'
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
loglevel = 'info'
accesslog = '-'
errorlog = '-'

def when_ready(server):
    thread = threading.Thread(target=background_ping_job, daemon=True)
    thread.start()
    server.log.info("Background ping job started on Render!")