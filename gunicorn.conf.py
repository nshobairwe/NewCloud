# gunicorn.conf.py
import os
import threading
import multiprocessing

# --- Gunicorn Settings ---
workers = 1
worker_class = 'sync'
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
timeout = 30
loglevel = 'info'
accesslog = '-'
errorlog = '-'

# --- Global lock to ensure thread runs only ONCE ---
_ping_thread_lock = multiprocessing.Lock()
_ping_thread_started = False

def post_worker_init(worker):
    """Runs in each worker AFTER forking"""
    global _ping_thread_started

    with _ping_thread_lock:
        if not _ping_thread_started:
            # Import here to avoid circular import
            from app import background_ping_job
            thread = threading.Thread(target=background_ping_job, daemon=True)
            thread.start()
            worker.log.info("Background ping job STARTED (once)")
            _ping_thread_started = True
        else:
            worker.log.info("Background ping job already running")