# local_pinger.py (run on your PC)
import subprocess
import json
import time
import requests
from datetime import datetime

# Your regions
regions = {
     "Dar es Salaam": {"wan": "10.8.235.22", "gateway": "10.8.235.21", "lan": ["10.11.0.0", "10.11.0.1", "10.11.0.2"]},
    "Temeke": {"wan": "10.8.238.250", "gateway": "10.8.238.249", "lan": ["10.8.63.0", "10.8.63.1", "10.8.63.3"]},
    "Kinondoni": {"wan": "10.8.234.6", "gateway": "10.8.234.5", "lan": ["10.12.2.0", "10.12.2.1", "10.12.2.3"]},
    "Upanga": {"wan": "10.8.238.226", "gateway": "10.8.238.225", "lan": ["10.12.3.0", "10.12.3.1", "10.12.3.3"]},
    "Ilala": {"wan": "10.8.234.2", "gateway": "10.8.234.1", "lan": ["10.12.6.0", "10.12.6.1", "10.12.6.3"]},
    "Dodoma": {"wan": "10.20.251.82", "gateway": "10.20.251.81", "lan": ["10.20.11.0", "10.20.11.1", "10.20.11.3"]},
    "Tabora": {"wan": "10.20.251.206", "gateway": "10.20.251.205", "lan": ["10.20.12.0", "10.20.12.1", "10.20.12.3"]},
    "Shinyanga": {"wan": "10.20.251.226", "gateway": "10.20.251.225", "lan": ["10.20.13.0", "10.20.13.1", "10.20.13.3"]},
    "Mwanza": {"wan": "10.20.254.226", "gateway": "10.20.254.225", "lan": ["10.20.63.0", "10.20.63.1", "10.20.63.3"]},
    "Iringa": {"wan": "10.20.251.42", "gateway": "10.20.251.41", "lan": ["10.24.75.0", "10.24.75.1", "10.24.75.3"]},
    "Kigoma": {"wan": "10.20.252.66", "gateway": "10.20.252.65", "lan": ["10.4.0.0", "10.4.0.1", "10.4.0.2"]},
    "Kagera": {"wan": "10.20.252.70", "gateway": "10.20.252.69", "lan": ["10.4.1.0", "10.4.1.1", "10.4.1.3"]},
    "Musoma": {"wan": "10.20.252.70", "gateway": "10.20.252.73", "lan": ["10.4.2.0", "10.4.2.1", "10.4.2.3"]},
    "Singida": {"wan": "10.8.234.6", "gateway": "10.20.248.17", "lan": ["10.4.3.0", "10.4.3.1", "10.4.3.3"]},
    "Lindi": {"wan": "10.8.238.66", "gateway": "10.8.238.70", "lan": ["10.4.4.0", "10.4.4.1", "10.4.4.3"]},
    "Mtwara": {"wan": "10.8.238.70", "gateway": "10.20.252.69", "lan": ["10.4.5.0", "10.4.5.1", "10.4.5.3"]},
    "Metropolitan": {"wan": "10.8.235.142", "gateway": "10.8.235.141", "lan": ["10.4.6.0", "10.4.6.1", "10.4.6.3"]},
    "Arusha": {"wan": "10.4.255.150", "gateway": "10.4.255.149", "lan": ["10.4.37.0", "10.4.37.1", "10.4.37.3"]},
    "Moshi": {"wan": "10.6.255.106", "gateway": "10.6.255.105", "lan": ["10.6.24.0", "10.6.24.1", "10.6.24.3"]},
    "Tanga": {"wan": "10.7.255.90", "gateway": "10.7.255.89", "lan": ["10.7.21.0", "10.7.21.1", "10.7.21.3"]},
    "Morogoro": {"wan": "10.25.79.74", "gateway": "10.25.79.73", "lan": ["10.25.86.0","10.25.86.1","10.25.86.2"]},
    "Mbeya": {"wan": "10.36.254.174", "gateway": "10.46.254.173", "lan": ["10.64.166.0","10.64.166.1","10.64.166.2"]},
    "Katavi": {"wan": "10.35.255.110", "gateway": "10.35.255.109", "lan": ["10.64.167.0","10.64.167.1","10.64.167.2"]},
    "Ruvuma": {"wan": "10.36.249.85", "gateway": "10.36.249.84", "lan": ["10.64.168.0","10.64.168.1","10.64.168.2"]},
    "HQ Internet": {"wan": "41.59.57.102", "gateway": "41.59.57.1012", "lan": ["41.59.57.100","41.59.57.101","41.59.57.102"]},

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