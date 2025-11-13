# local_pinger.py  (run on your PC)
import subprocess
import time
import requests
from datetime import datetime

# ------------------------------------------------------------------
# 1. Regions – LAN can be a single string OR a list of strings
# ------------------------------------------------------------------
regions = {
    "Dar es Salaam": {"wan": "10.8.235.22", "gateway": "10.8.235.21", "lan": "10.11.0.1"},
    "Temeke":        {"wan": "10.8.238.250", "gateway": "10.8.238.249", "lan": "10.8.63.1"},
    "Kinondoni":     {"wan": "10.8.234.6",   "gateway": "10.8.234.5",   "lan": "10.12.2.1"},
    "Upanga":        {"wan": "10.8.238.226", "gateway": "10.8.238.225", "lan": "10.12.3.1"},
    "Ilala":         {"wan": "10.8.234.2",   "gateway": "10.8.234.1",   "lan": "10.12.6.1"},
    "Dodoma":        {"wan": "10.20.251.82", "gateway": "10.20.251.81", "lan": "10.20.11.1"},
    # … (all your other regions) …
    "HQ Internet":   {"wan": "41.59.57.102", "gateway": "41.59.57.102", "lan": "41.59.57.101"},
    "NHC House":     {"wan": "10.4.244.146", "gateway": "10.4.244.145", "lan": "10.15.4.1"},
}

RENDER_URL = "https://newcloud.onrender.com/update"
INTERVAL   = 10   # seconds

# ------------------------------------------------------------------
# 2. Ping a single IP (Windows)
# ------------------------------------------------------------------
def ping_ip(ip: str) -> str:
    try:
        out = subprocess.run(
            ["ping", "-n", "1", "-w", "2000", ip],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=5
        )
        return "ACTIVE" if "TTL=" in out.stdout else "INACTIVE"
    except Exception:
        return "INACTIVE"

# ------------------------------------------------------------------
# 3. Build the payload – ALWAYS three rows per region
# ------------------------------------------------------------------
def collect_results() -> dict:
    payload = {}
    for region, info in regions.items():
        rows = []

        # ---- WAN ----------------------------------------------------
        rows.append({
            "ip": info["wan"],
            "label": "WAN",
            "status": ping_ip(info["wan"])
        })

        # ---- Gateway ------------------------------------------------
        rows.append({
            "ip": info["gateway"],
            "label": "Gateway",
            "status": ping_ip(info["gateway"])
        })

        # ---- LAN (single string OR list) ---------------------------
        lan = info["lan"]
        if isinstance(lan, list):
            # if you ever go back to multiple LAN IPs
            for ip in lan:
                rows.append({"ip": ip, "label": "LAN", "status": ping_ip(ip)})
        else:
            # single LAN IP (your current case)
            rows.append({"ip": lan, "label": "LAN", "status": ping_ip(lan)})

        payload[region] = rows
    return payload

# ------------------------------------------------------------------
# 4. POST to Render
# ------------------------------------------------------------------
def send_to_cloud() -> None:
    data = {"results": collect_results()}
    try:
        r = requests.post(RENDER_URL, json=data, timeout=10)
        if r.status_code == 200:
            print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Sent to cloud – OK")
        else:
            print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] HTTP {r.status_code}")
    except Exception as e:
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] ERROR: {e}")

# ------------------------------------------------------------------
# 5. Main loop
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("Local pinger started – press Ctrl+C to stop")
    while True:
        send_to_cloud()
        time.sleep(INTERVAL)