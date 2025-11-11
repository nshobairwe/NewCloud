# local_pinger.py (run on your PC)
import subprocess
import json
import time
import requests
from datetime import datetime

# Your regions
regions = {
    "Dar es Salaam": {"wan": "10.8.235.22", "gateway": "10.8.235.21",
                      "lan": ["10.11.0.0", "10.11.0.1", "10.11.0.2"]},
    "Temeke": {"wan": "10.8.238.250", "gateway": "10.8.238.249",
               "lan": ["10.8.63.0", "10.8.63.1", "10.8.63.3"]},
    # ... add all ...
}

RENDER_URL = "https://newcloud.onrender.com/update"  # Change this!
INTERVAL = 10  # seconds

def ping_ip(ip):
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "2000", ip],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return "ACTIVE" if "TTL=" in result.stdout else "INACTIVE"
    except:
        return "INACTIVE"

def collect_results():
    results = {}
    for region, info in regions.items():
        items = []
        # WAN
        items.append({"ip": info["wan"], "label": "WAN", "status": ping_ip(info["wan"])})
        # Gateway
        items.append({"ip": info["gateway"], "label": "Gateway", "status": ping_ip(info["gateway"])})
        # LAN
        for ip in info["lan"]:
            items.append({"ip": ip, "label": "LAN", "status": ping_ip(ip)})
        results[region] = items
    return results

def send_to_cloud():
    data = {"results": collect_results()}
    try:
        requests.post(RENDER_URL, json=data, timeout=10)
        print(f"[{datetime.now()}] Sent to cloud")
    except Exception as e:
        print(f"Failed to send: {e}")

if __name__ == "__main__":
    print("Local pinger started...")
    while True:
        send_to_cloud()
        time.sleep(INTERVAL)