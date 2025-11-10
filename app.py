# --------------------------------------------------------------
# app.py  –  Ping monitor (Render + local Windows)
# --------------------------------------------------------------

import os
import subprocess
import concurrent.futures
import threading
import time
from flask import Flask, render_template

app = Flask(__name__)

# ------------------------------------------------------------------
# 1. Regions (keep your full list – only 2 shown for brevity)
# ------------------------------------------------------------------
regions = {
    "Dar es Salaam": {"wan": "10.8.235.22", "gateway": "10.8.235.21",
                      "lan": ["10.11.0.0", "10.11.0.1", "10.11.0.2"]},
    "Temeke": {"wan": "10.8.238.250", "gateway": "10.8.238.249",
               "lan": ["10.8.63.0", "10.8.63.1", "10.8.63.3"]},
    # … add the rest of your regions here …
}

# ------------------------------------------------------------------
# 2. Config (env vars – safe defaults)
# ------------------------------------------------------------------
PING_INTERVAL = int(os.getenv("PING_INTERVAL", "5"))   # seconds between scans
PING_TIMEOUT  = int(os.getenv("PING_TIMEOUT", "2"))    # seconds per ping

ping_results = {}

# ------------------------------------------------------------------
# 3. One ping – works on **Linux (Render)** and **Windows**
# ------------------------------------------------------------------
def ping_ip(ip: str) -> dict:
    """Return {'ip': ip, 'status': 'ACTIVE'|'INACTIVE'}"""
    # -c 1   → Linux   (count = 1)
    # -n 1   → Windows
    param = "-n" if os.name == "nt" else "-c"
    # -W = Linux timeout in seconds, -w = Windows timeout in ms
    timeout_flag = "-W" if os.name != "nt" else "-w"
    timeout_val  = str(PING_TIMEOUT) if os.name != "nt" else str(PING_TIMEOUT * 1000)

    cmd = ["ping", param, "1", timeout_flag, timeout_val, ip]

    try:
        output = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=PING_TIMEOUT + 2,   # a little safety
            text=True,
        )
        # Both Linux and Windows show "TTL=" when alive
        alive = "TTL=" in output.stdout or "ttl=" in output.stdout
        return {"ip": ip, "status": "ACTIVE" if alive else "INACTIVE"}
    except Exception:
        return {"ip": ip, "status": "INACTIVE"}

# ------------------------------------------------------------------
# 4. Background worker – **started only once**
# ------------------------------------------------------------------
def background_ping_job():
    global ping_results
    while True:
        new_results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as exe:
            future_to_key = {}

            for region, info in regions.items():
                # WAN
                f = exe.submit(ping_ip, info["wan"])
                future_to_key[f] = (region, "WAN")
                # Gateway
                f = exe.submit(ping_ip, info["gateway"])
                future_to_key[f] = (region, "Gateway")
                # LAN
                for lan_ip in info["lan"]:
                    f = exe.submit(ping_ip, lan_ip)
                    future_to_key[f] = (region, "LAN")

            for fut in concurrent.futures.as_completed(future_to_key):
                region, label = future_to_key[fut]
                res = fut.result()
                res["label"] = label
                new_results.setdefault(region, []).append(res)

        ping_results = new_results
        time.sleep(PING_INTERVAL)

# ------------------------------------------------------------------
# 5. Flask route
# ------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", results=ping_results, interval=PING_INTERVAL)

# ------------------------------------------------------------------
# 6. Entry point – **single background thread** (Render + local)
# ------------------------------------------------------------------
# Start the worker **once** when the module is first imported
_thread = threading.Thread(target=background_ping_job, daemon=True)
_thread.start()

if __name__ == "__main__":
    # Local dev only – Flask dev server
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)