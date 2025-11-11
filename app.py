# app.py – FINAL VERSION

import os
import subprocess
import concurrent.futures
import threading
import time
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

# --- Config ---
PING_INTERVAL = int(os.getenv("PING_INTERVAL", "10"))
PING_TIMEOUT  = int(os.getenv("PING_TIMEOUT", "3"))
ping_results = {}

# --- Regions ---
regions = {
    "Dar es Salaam": {"wan": "10.8.235.22", "gateway": "10.8.235.21",
                      "lan": ["10.11.0.0", "10.11.0.1", "10.11.0.2"]},
    "Temeke": {"wan": "10.8.238.250", "gateway": "10.8.238.249",
               "lan": ["10.8.63.0", "10.8.63.1", "10.8.63.3"]},
    # ... add all your regions ...
}

# --- Ping function ---
def ping_ip(ip: str) -> dict:
    param = "-n" if os.name == "nt" else "-c"
    timeout_flag = "-w" if os.name == "nt" else "-W"
    timeout_val = str(PING_TIMEOUT * 1000) if os.name == "nt" else str(PING_TIMEOUT)
    cmd = ["ping", param, "1", timeout_flag, timeout_val, ip]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=PING_TIMEOUT + 3, text=True)
        alive = "TTL=" in result.stdout
        return {"ip": ip, "status": "ACTIVE" if alive else "INACTIVE"}
    except Exception:
        return {"ip": ip, "status": "INACTIVE"}

# --- Background job (MUST be at top level for import) ---
def background_ping_job():
    global ping_results
    while True:
        new_results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as exe:
            future_to_key = {}
            for region, info in regions.items():
                f = exe.submit(ping_ip, info["wan"])
                future_to_key[f] = (region, "WAN")
                f = exe.submit(ping_ip, info["gateway"])
                future_to_key[f] = (region, "Gateway")
                for ip in info["lan"]:
                    f = exe.submit(ping_ip, ip)
                    future_to_key[f] = (region, "LAN")

            for fut in concurrent.futures.as_completed(future_to_key):
                region, label = future_to_key[fut]
                res = fut.result()
                res["label"] = label
                new_results.setdefault(region, []).append(res)

        ping_results = new_results
        print(f"Scan complete. Results: {len(ping_results)} regions")
        time.sleep(PING_INTERVAL)

# --- Flask route ---
@app.route("/")
def index():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S EAT")
    print(f"Rendering page. Results has {len(ping_results)} regions")  # DEBUG
    return render_template(
        "index.html",
        results=ping_results,
        interval=PING_INTERVAL,
        current_time=current_time
    )

# --- Local dev only ---
if __name__ == "__main__":
    thread = threading.Thread(target=background_ping_job, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)